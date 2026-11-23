"""
Frontera HTTP del módulo livestock: un router por agregado, unidos en `router`.

  bovines.py   -> /api/v1/farms/{farm_id}/bovines            (ficha y carga CSV)
  weights.py   -> /api/v1/farms/{farm_id}/bovines/{id}/weights
  calves.py    -> /api/v1/farms/{farm_id}/calves             (HU007)
  movements.py -> /api/v1/farms/{farm_id}/movements          (HU009)
"""

from fastapi import APIRouter

from app.modules.livestock.router.bovines import router as bovines_router
from app.modules.livestock.router.calves import router as calves_router
from app.modules.livestock.router.movements import router as movements_router
from app.modules.livestock.router.weights import router as weights_router

router = APIRouter()
router.include_router(bovines_router)
router.include_router(weights_router)
router.include_router(calves_router)
router.include_router(movements_router)

__all__ = ["router"]
