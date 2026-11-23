"""Frontera HTTP de team: rutas públicas (/auth), empleados y moderación (/admin), unidas en `router`."""

from fastapi import APIRouter

from app.modules.team.router.admin import router as admin_router
from app.modules.team.router.employees import router as employees_router
from app.modules.team.router.public import router as public_router

router = APIRouter()
router.include_router(public_router)
router.include_router(employees_router)
router.include_router(admin_router)

__all__ = ["router"]
