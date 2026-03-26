# Routers de Bovitrack (endpoints HTTP agrupados por dominio)

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.farms import router as farms_router

__all__ = ["auth_router", "users_router", "farms_router"]
