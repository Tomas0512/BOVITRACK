"""
Módulo: modules/farms/dependencies.py (composición del módulo)
¿Qué? 1. Arma por request los servicios de fincas, catálogos, lotes y potreros.
      2. Ofrece a otros módulos los puertos que solo farms sabe responder:
         - build_farm_scope_checker(db, find_bovine=...) -> FarmScopeChecker
           (health, inventory, livestock, reproduction, tasks)
         - build_land_plot_lookup(db)  -> LandPlotLookup  (health, livestock, milk_production)
         - build_paddock_lookup(db)    -> PaddockLookup   (inventory, livestock)
         - build_land_plot_id_by_name(db), build_paddock_id_by_name(db)  (livestock: importación CSV)
         - list_active_farm_ids(db)                       (notifications: tarea programada)
¿Para qué? Que "qué es de esta finca" se defina una sola vez, en el dueño de los datos.
¿Impacto? farms solo usa a identity (está por debajo en las capas): la membresía
          del creador, las fincas de un usuario y los guards.
"""

import uuid
from collections.abc import Callable
from functools import partial

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.audit_trail import add_audit_log
from app.core.database import get_db
from app.modules import identity
from app.modules.farms.repository import CatalogRepository, FarmRepository, LandPlotRepository, PaddockRepository
from app.modules.farms.service import CatalogService, FarmScopeService, FarmService, LandPlotService, PaddockService
from app.shared.ports import BovineLookup, FarmScopeChecker, LandPlotLookup, PaddockLookup, PaddockRef

# Guards de identity (su API pública). Los routers de este módulo los importan
# desde aquí, para que solo este archivo conozca a otro módulo.
from app.modules.identity import get_current_user as get_current_user
from app.modules.identity import require_permission as require_permission


# Id de un lote o potrero por su nombre: cumple el puerto IdByNameLookup de livestock.
IdByName = Callable[[uuid.UUID, str], uuid.UUID | None]


# ── Servicios por request
def get_farm_service(db: Session = Depends(get_db)) -> FarmService:
    return FarmService(
        FarmRepository(db),
        grant_admin=identity.build_admin_granter(db),
        member_farm_ids=identity.build_member_farm_ids(db),
        is_member=identity.build_membership_check(db),
        record_audit=partial(add_audit_log, db),
    )


def get_catalog_service(db: Session = Depends(get_db)) -> CatalogService:
    return CatalogService(CatalogRepository(db))


def get_land_plot_service(db: Session = Depends(get_db)) -> LandPlotService:
    return LandPlotService(LandPlotRepository(db), PaddockRepository(db), record_audit=partial(add_audit_log, db))


def get_paddock_service(db: Session = Depends(get_db)) -> PaddockService:
    return PaddockService(PaddockRepository(db), LandPlotRepository(db), record_audit=partial(add_audit_log, db))


# ── Puertos para otros módulos
def build_farm_scope_checker(db: Session, *, find_bovine: BovineLookup | None = None) -> FarmScopeChecker:
    """FarmScopeChecker. Quien valide bovinos debe pasar find_bovine (lo obtiene de livestock)."""
    return FarmScopeService(
        land_plot_exists=LandPlotRepository(db).exists_in_farm,
        farm_owner=FarmRepository(db).owner_id,
        is_member=identity.build_membership_check(db),
        find_bovine=find_bovine,
    )


def build_land_plot_lookup(db: Session) -> LandPlotLookup:
    """LandPlotLookup: ¿el lote existe y es de la finca?"""
    return LandPlotRepository(db).exists_in_farm


def build_paddock_lookup(db: Session) -> PaddockLookup:
    """PaddockLookup: el potrero ACTIVO de la finca (con su lote), o None."""
    repository = PaddockRepository(db)

    def find(farm_id: uuid.UUID, paddock_id: uuid.UUID) -> PaddockRef | None:
        paddock = repository.find_active_ref(farm_id, paddock_id)
        return PaddockRef(id=paddock.id, land_plot_id=paddock.land_plot_id) if paddock else None

    return find


def build_land_plot_id_by_name(db: Session) -> IdByName:
    """Id de un lote de la finca por su nombre (sin distinguir mayúsculas)."""
    return LandPlotRepository(db).id_by_name


def build_paddock_id_by_name(db: Session) -> IdByName:
    """Id de un potrero de la finca por su nombre (sin distinguir mayúsculas)."""
    return PaddockRepository(db).id_by_name


def list_active_farm_ids(db: Session) -> list[uuid.UUID]:
    """IDs de todas las fincas activas."""
    return FarmRepository(db).active_ids()


def build_farm_name_lookup(db: Session) -> Callable[[uuid.UUID], str | None]:
    """Nombre de la finca (activa o no), o None si no existe (team: invitaciones)."""
    repository = FarmRepository(db)

    def name_of(farm_id: uuid.UUID) -> str | None:
        return repository.name_of(farm_id)

    return name_of
