"""Frontera HTTP de farms: fincas y catálogos, potreros y lotes, unidos en `router`."""

from fastapi import APIRouter

from app.modules.farms.router.farms import router as farms_router
from app.modules.farms.router.land_plots import router as land_plots_router
from app.modules.farms.router.paddocks import router as paddocks_router

router = APIRouter()
router.include_router(farms_router)
router.include_router(paddocks_router)
router.include_router(land_plots_router)

__all__ = ["router"]
