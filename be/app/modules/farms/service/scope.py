"""
Módulo: modules/farms/service/scope.py (alcance de finca)
¿Qué? Comprueba que un bovino, un lote y/o una persona pertenezcan a la finca.
      Es la implementación del puerto FarmScopeChecker (app.shared.ports).
¿Para qué? Evitar acceso cruzado (IDOR): crear un tratamiento, una tarea o un
           pesaje que apunte a un animal, lote o persona de OTRA finca.
¿Impacto? 400 (BusinessRuleError) con el mismo mensaje de antes si algo no pertenece.

¿Por qué recibe find_bovine? Los bovinos son de livestock, que está POR ENCIMA de
farms en las capas: farms no puede importarlo. Cada módulo consumidor le pasa el
buscador de bovinos que obtiene de livestock (inyección). La membresía, en
cambio, sí la pide farms a identity, que está por debajo.
"""

import uuid
from collections.abc import Callable

from app.shared.exceptions import BusinessRuleError
from app.shared.ports import BovineLookup, FarmMembershipCheck, LandPlotLookup

BOVINE_NOT_IN_FARM = "El bovino indicado no existe en esta finca."
LAND_PLOT_NOT_IN_FARM = "El lote indicado no existe en esta finca."
USER_NOT_IN_FARM = "El usuario asignado no pertenece a esta finca."


class FarmScopeService:
    def __init__(
        self,
        *,
        land_plot_exists: LandPlotLookup,
        farm_owner: Callable[[uuid.UUID], uuid.UUID | None],
        is_member: FarmMembershipCheck,
        find_bovine: BovineLookup | None = None,
    ) -> None:
        self._land_plot_exists = land_plot_exists
        self._farm_owner = farm_owner
        self._is_member = is_member
        self._find_bovine = find_bovine

    def __call__(
        self,
        farm_id: uuid.UUID,
        *,
        bovine_id: uuid.UUID | None = None,
        land_plot_id: uuid.UUID | None = None,
        member_user_id: uuid.UUID | None = None,
    ) -> None:
        """FarmScopeChecker: no devuelve nada si todo es de la finca; si no, BusinessRuleError."""
        if bovine_id is not None:
            if self._find_bovine is None:
                raise RuntimeError("FarmScopeService necesita find_bovine para validar un bovino")
            if self._find_bovine(farm_id, bovine_id) is None:
                raise BusinessRuleError(BOVINE_NOT_IN_FARM)
        if land_plot_id is not None and not self._land_plot_exists(farm_id, land_plot_id):
            raise BusinessRuleError(LAND_PLOT_NOT_IN_FARM)
        if member_user_id is not None and not self._belongs(farm_id, member_user_id):
            raise BusinessRuleError(USER_NOT_IN_FARM)

    def _belongs(self, farm_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Miembro ACTIVO de la finca (lo responde identity) o su dueño."""
        return self._is_member(farm_id, user_id) or self._farm_owner(farm_id) == user_id
