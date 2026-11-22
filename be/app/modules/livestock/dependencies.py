"""
Módulo: modules/livestock/dependencies.py (composición del módulo)
¿Qué? 1. Arma por request los servicios de bovinos, pesajes, terneros y
         movimientos, todos sobre la MISMA sesión (una sola transacción).
      2. Ofrece a otros módulos los puertos que el ganado sabe responder:
         - build_bovine_lookup(db)   -> BovineLookup  (milk_production,
           reproduction, documents, health)
         - build_calf_registrar(db)  -> CalfRegistrar (reproduction)
¿Para qué? Que "qué es un bovino de la finca" y "cómo se registra una cría"
           se definan una sola vez, en el dueño de los datos.
¿Impacto? Solo usa módulos de niveles más bajos: farms (lotes, potreros,
          alcance de finca) e identity (guards). De livestock dependen
          inventario, salud, reproducción, producción, documentos y tareas, así
          que no puede formarse un ciclo.
"""

import uuid
from collections.abc import Callable
from datetime import date
from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules import farms
from app.modules.livestock.repository import BovineRepository, MovementRepository, WeightRepository
from app.modules.livestock.service import BovineService, CalfService, MovementService, WeightService
from app.shared.ports import BovineLookup, BovineRef

# Rastro de auditoría: infraestructura de core (no es otro módulo).
from app.core.audit_trail import add_audit_log

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


def build_bovine_service(db: Session) -> BovineService:
    return BovineService(
        repository=BovineRepository(db),
        land_plot_exists=farms.build_land_plot_lookup(db),
        find_paddock=farms.build_paddock_lookup(db),
        ensure_farm_scope=farms.build_farm_scope_checker(db, find_bovine=build_bovine_lookup(db)),
        land_plot_id_by_name=farms.build_land_plot_id_by_name(db),
        paddock_id_by_name=farms.build_paddock_id_by_name(db),
        record_audit=partial(add_audit_log, db),
    )


def get_bovine_service(db: Session = Depends(get_db)) -> BovineService:
    """Dependencia de FastAPI: un BovineService por request."""
    return build_bovine_service(db)


def get_weight_service(db: Session = Depends(get_db)) -> WeightService:
    """Dependencia de FastAPI: un WeightService por request."""
    return WeightService(WeightRepository(db), BovineRepository(db), partial(add_audit_log, db))


def get_calf_service(db: Session = Depends(get_db)) -> CalfService:
    """Dependencia de FastAPI: un CalfService por request."""
    return CalfService(
        bovines=BovineRepository(db),
        weights=WeightRepository(db),
        record_audit=partial(add_audit_log, db),
    )


def get_movement_service(db: Session = Depends(get_db)) -> MovementService:
    """Dependencia de FastAPI: un MovementService por request."""
    return MovementService(MovementRepository(db), BovineRepository(db), partial(add_audit_log, db))


# ── Puertos que el ganado ofrece a otros módulos ──────────────────


def build_bovine_lookup(db: Session) -> BovineLookup:
    """BovineLookup: el bovino de la finca (activo o no) como BovineRef, o None."""
    repo = BovineRepository(db)

    def lookup(farm_id: uuid.UUID, bovine_id: uuid.UUID) -> BovineRef | None:
        bovine = repo.get_in_farm(farm_id, bovine_id)
        return BovineRef(id=bovine.id, sex=bovine.sex) if bovine else None

    return lookup


def build_calf_registrar(db: Session) -> Callable[..., uuid.UUID]:
    """CalfRegistrar (lo define reproduction): registra una cría en la misma transacción."""
    service = build_bovine_service(db)

    def register(
        farm_id: uuid.UUID,
        *,
        identification_number: str,
        sex: str,
        birth_date: date,
        mother_id: uuid.UUID,
        registered_by: uuid.UUID,
    ) -> uuid.UUID:
        return service.register_calf_from_birth(
            farm_id,
            identification_number=identification_number,
            sex=sex,
            birth_date=birth_date,
            mother_id=mother_id,
            registered_by=registered_by,
        )

    return register
