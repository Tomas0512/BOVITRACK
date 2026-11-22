"""
Módulo: modules/livestock/service/bovines.py
¿Qué? Casos de uso de la ficha del bovino: registrar (uno o por CSV), listar,
      consultar, editar y retirar; y registrar crías nacidas de un parto (lo
      pide el módulo de reproducción).
¿Para qué? Llevar el inventario vivo del hato con genealogía y ubicación.
¿Impacto? Garantiza que:
          - el número de identificación es único dentro de la finca (409);
          - padre, madre, lote y potrero son de ESTA finca, y el potrero es
            coherente con el lote (si no se indica lote, se toma el del potrero);
          - el bovino y su registro de auditoría se guardan juntos o no se guardan;
          - retirar es lógico (los historiales del animal se conservan).
          No conoce HTTP ni SQLAlchemy; lotes y potreros los consulta por puertos.
"""

import csv
import io
import uuid
from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Any, Protocol

from pydantic import ValidationError

from app.modules.livestock.models import Bovine
from app.modules.livestock.repository import BovineRepository
from app.modules.livestock.schemas import BovineCreate, BovineUpdate
from app.shared.exceptions import BusinessRuleError, ConflictError, DomainError, NotFoundError
from app.shared.ports import AuditRecorder, FarmScopeChecker, LandPlotLookup, PaddockLookup, PaddockRef

BOVINE_NOT_FOUND = "Bovino no encontrado"
DUPLICATE_IDENTIFICATION = "Ya existe un bovino con esa identificación en la finca"
PARENT_NOT_IN_FARM = "El bovino padre/madre indicado no existe en esta finca"
PLOT_NOT_IN_FARM = "El lote indicado no existe en esta finca"
PADDOCK_NOT_IN_FARM = "El potrero indicado no existe en esta finca"
PADDOCK_OTHER_PLOT = "El potrero indicado pertenece a otro lote."
CSV_WITHOUT_HEADERS = "El CSV no tiene cabeceras"


class IdByNameLookup(Protocol):
    """Puerto hacia fincas: id de un lote o potrero de la finca por su nombre (sin distinguir mayúsculas)."""

    def __call__(self, farm_id: uuid.UUID, name: str) -> uuid.UUID | None: ...


def _user(user_id: uuid.UUID | None) -> str | None:
    return str(user_id) if user_id else None


class BovineService:
    """Casos de uso de la ficha del bovino."""

    def __init__(
        self,
        repository: BovineRepository,
        land_plot_exists: LandPlotLookup,
        find_paddock: PaddockLookup,
        ensure_farm_scope: FarmScopeChecker,
        land_plot_id_by_name: IdByNameLookup,
        paddock_id_by_name: IdByNameLookup,
        record_audit: AuditRecorder,
    ) -> None:
        self._repo = repository
        self._land_plot_exists = land_plot_exists
        self._find_paddock = find_paddock
        self._ensure_farm_scope = ensure_farm_scope
        self._land_plot_id_by_name = land_plot_id_by_name
        self._paddock_id_by_name = paddock_id_by_name
        self._record_audit = record_audit

    # ── Validaciones ─────────────────────────────────────────

    def _active_paddock(self, farm_id: uuid.UUID, paddock_id: uuid.UUID) -> PaddockRef:
        paddock = self._find_paddock(farm_id, paddock_id)
        if paddock is None:
            raise BusinessRuleError(PADDOCK_NOT_IN_FARM)
        return paddock

    # ── Casos de uso ─────────────────────────────────────────

    def create_bovine(self, farm_id: uuid.UUID, data: BovineCreate, user_id: uuid.UUID) -> Bovine:
        if self._repo.identification_taken(farm_id, data.identification_number):
            raise ConflictError(DUPLICATE_IDENTIFICATION)
        for parent_id in (data.father_id, data.mother_id):
            if parent_id and self._repo.get_in_farm(farm_id, parent_id) is None:
                raise BusinessRuleError(PARENT_NOT_IN_FARM)
        if data.land_plot_id and not self._land_plot_exists(farm_id, data.land_plot_id):
            raise BusinessRuleError(PLOT_NOT_IN_FARM)

        values = data.model_dump()
        if data.paddock_id:
            paddock = self._active_paddock(farm_id, data.paddock_id)
            if data.land_plot_id and paddock.land_plot_id != data.land_plot_id:
                raise BusinessRuleError(PADDOCK_OTHER_PLOT)
            if not data.land_plot_id:
                values["land_plot_id"] = paddock.land_plot_id

        bovine = Bovine(farm_id=farm_id, registered_by=user_id, **values)
        try:
            self._repo.add(bovine)
            self._repo.flush()
            self._record_audit(user_id=str(user_id), farm_id=str(farm_id), action="create", entity="bovine",
                               entity_id=str(bovine.id), details={"tag": bovine.identification_number})
            self._repo.commit()
            self._repo.refresh(bovine)
        except Exception:
            self._repo.rollback()
            raise
        return bovine

    def list_bovines(
        self,
        farm_id: uuid.UUID,
        *,
        sex: str | None = None,
        status_filter: str | None = None,
        purpose: str | None = None,
    ) -> Sequence[Bovine]:
        return self._repo.list_active(farm_id, sex=sex, status=status_filter, purpose=purpose)

    def list_breeds(self, farm_id: uuid.UUID) -> list[str]:
        return self._repo.list_breeds(farm_id)

    def get_bovine(self, farm_id: uuid.UUID, bovine_id: uuid.UUID) -> Bovine:
        bovine = self._repo.get_in_farm(farm_id, bovine_id)
        if bovine is None:
            raise NotFoundError(BOVINE_NOT_FOUND)
        return bovine

    def update_bovine(
        self, farm_id: uuid.UUID, bovine_id: uuid.UUID, data: BovineUpdate, user_id: uuid.UUID | None = None
    ) -> Bovine:
        bovine = self.get_bovine(farm_id, bovine_id)
        changes = data.model_dump(exclude_unset=True)

        new_ident = changes.get("identification_number")
        if new_ident and self._repo.identification_taken(farm_id, new_ident, exclude_id=bovine_id):
            raise ConflictError(DUPLICATE_IDENTIFICATION)
        if changes.get("land_plot_id") is not None:
            self._ensure_farm_scope(farm_id, land_plot_id=changes["land_plot_id"])
        if changes.get("father_id") is not None:
            self._ensure_farm_scope(farm_id, bovine_id=changes["father_id"])
        if changes.get("mother_id") is not None:
            self._ensure_farm_scope(farm_id, bovine_id=changes["mother_id"])

        # Coherencia finca > lote > potrero con los valores finales.
        final_land = changes["land_plot_id"] if "land_plot_id" in changes else bovine.land_plot_id
        final_paddock = changes["paddock_id"] if "paddock_id" in changes else bovine.paddock_id
        if final_paddock:
            paddock = self._active_paddock(farm_id, final_paddock)
            if final_land is not None and paddock.land_plot_id != final_land:
                raise BusinessRuleError(PADDOCK_OTHER_PLOT)
            if final_land is None:
                changes["land_plot_id"] = paddock.land_plot_id

        for field, value in changes.items():
            setattr(bovine, field, value)
        try:
            self._repo.flush()
            self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="update", entity="bovine",
                               entity_id=str(bovine.id), details={"tag": bovine.identification_number})
            self._repo.commit()
            self._repo.refresh(bovine)
        except Exception:
            self._repo.rollback()
            raise
        return bovine

    def delete_bovine(self, farm_id: uuid.UUID, bovine_id: uuid.UUID, user_id: uuid.UUID | None = None) -> None:
        """Retiro lógico: el bovino sale del listado pero sus historiales se conservan."""
        bovine = self.get_bovine(farm_id, bovine_id)
        bovine.is_active = False
        bovine.status = "retirado"
        bovine.exit_date = date.today()
        bovine.exit_reason = "retirado"
        try:
            self._record_audit(user_id=_user(user_id), farm_id=str(farm_id), action="delete", entity="bovine",
                               entity_id=str(bovine.id), details={"tag": bovine.identification_number})
            self._repo.commit()
        except Exception:
            self._repo.rollback()
            raise

    # ── Carga masiva ─────────────────────────────────────────

    def import_bovines(
        self, farm_id: uuid.UUID, rows: list[tuple[int, BovineCreate]], user_id: uuid.UUID
    ) -> dict[str, Any]:
        """Registra cada fila con create_bovine; una fila con error no detiene las demás.

        Cada fila llega con su número de línea REAL en el CSV, para que el
        usuario sepa exactamente qué corregir.
        """
        imported = 0
        errors: list[dict[str, Any]] = []
        for idx, data in rows:
            try:
                self.create_bovine(farm_id, data, user_id)
                imported += 1
            except DomainError as exc:
                errors.append({"row": idx, "error": exc.message})
            except Exception as exc:  # noqa: BLE001 - reporte por fila, no abortar
                errors.append({"row": idx, "error": f"Error inesperado: {exc}"})
        return {"imported": imported, "failed": len(errors), "errors": errors}

    def import_csv(self, farm_id: uuid.UUID, content: str, user_id: uuid.UUID) -> dict[str, Any]:
        """Interpreta un CSV (UTF-8) de bovinos y registra las filas válidas.

        Columnas obligatorias: identification_number, sex, birth_date, entry_type,
        entry_date. Opcionales: name, breed, color, purpose, observations,
        birth_weight, current_weight, land_plot y paddock (por nombre).
        """
        reader = csv.DictReader(io.StringIO(content))
        if not reader.fieldnames:
            raise BusinessRuleError(CSV_WITHOUT_HEADERS)
        headers = {h.strip().lower(): h for h in reader.fieldnames}

        rows: list[tuple[int, BovineCreate]] = []
        raw_errors: list[dict[str, Any]] = []
        read = 0
        for idx, raw in enumerate(reader, start=2):  # la fila 1 es la cabecera
            read += 1
            get = lambda *names: next((raw[headers[n]].strip() for n in names if n in headers and (raw.get(headers[n]) or "")), "")  # noqa: E731
            try:
                payload: dict[str, Any] = {
                    "identification_number": get("identification_number", "id"),
                    "sex": (get("sex") or "").lower(),
                    "birth_date": get("birth_date", "birthdate"),
                    "entry_type": (get("entry_type", "entrytype") or "").lower(),
                    "entry_date": get("entry_date", "entrydate"),
                }
                for field, col in (("name", "name"), ("breed", "breed"), ("color", "color"), ("purpose", "purpose"), ("observations", "observations")):
                    value = get(col)
                    if value:
                        payload[field] = value
                for field, col in (("birth_weight", "birth_weight"), ("current_weight", "current_weight")):
                    value = get(col)
                    if value:
                        payload[field] = Decimal(value.replace(",", "."))
                land_plot = get("land_plot", "landplot", "lote")
                paddock = get("paddock", "potrero")
                payload["land_plot_id"] = self._land_plot_id_by_name(farm_id, land_plot) if land_plot else None
                payload["paddock_id"] = self._paddock_id_by_name(farm_id, paddock) if paddock else None
                rows.append((idx, BovineCreate(**payload)))
            except ValidationError as exc:
                raw_errors.append({"row": idx, "error": "; ".join(e["msg"] for e in exc.errors())[:200]})
            except Exception as exc:  # noqa: BLE001
                raw_errors.append({"row": idx, "error": f"Fila no válida: {exc}"})

        result = self.import_bovines(farm_id, rows, user_id)
        errors = sorted(raw_errors + result["errors"], key=lambda e: e["row"])
        # total = filas de datos leídas; failed = TODAS las que no se importaron
        # (antes total y failed solo contaban las filas que pasaron el formato).
        return {
            "total": read,
            "imported": result["imported"],
            "failed": len(errors),
            "errors": errors,
        }

    # ── Puerto ofrecido a reproduction (CalfRegistrar) ───────

    def register_calf_from_birth(
        self,
        farm_id: uuid.UUID,
        *,
        identification_number: str,
        sex: str,
        birth_date: date,
        mother_id: uuid.UUID,
        registered_by: uuid.UUID,
    ) -> uuid.UUID:
        """Registra una cría nacida de un parto y devuelve su id.

        Hace flush (no commit): la cría queda en la misma transacción que el
        evento reproductivo; si el evento falla, la cría tampoco se guarda.
        """
        calf = Bovine(
            farm_id=farm_id,
            registered_by=registered_by,
            identification_number=identification_number,
            sex=sex,
            birth_date=birth_date,
            entry_type="nacimiento",
            entry_date=birth_date,
            mother_id=mother_id,
        )
        self._repo.add(calf)
        self._repo.flush()
        self._record_audit(user_id=str(registered_by), farm_id=str(farm_id), action="create", entity="bovine",
                           entity_id=str(calf.id), details={"calf_from": "parto", "mother_id": str(mother_id)})
        return calf.id
