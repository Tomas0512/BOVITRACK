"""
Módulo identity — API pública (usuarios, autenticación, roles, permisos y membresías).

Es la capa BASE del monolito: no depende de ningún otro módulo, y todos dependen de él.

Lo que ofrece:
  - Guards para los routers de todos los módulos:
      get_current_user, require_permission(module, action), oauth2_scheme
  - Puertos para otros módulos:
      has_permission_anywhere(db, user_id, module, action)   (audit)
      build_farm_member_lookup(db) -> FarmMemberLookup        (notifications)
      build_user_email_lookup(db)  -> UserEmailLookup          (notifications)
      build_membership_check(db)   -> FarmMembershipCheck      (farms)
      build_admin_granter(db)      -> MembershipGranter        (farms)
      build_member_farm_ids(db)    -> MemberFarmIds            (farms)
      build_membership_directory(db) -> usuarios, roles y membresías (team)
      build_password_hasher()      -> hash de contraseñas      (team)
  - Tipos de la cuenta: User (modelo), DocumentType, UserResponse, MessageResponse.
  - api_router: se carga solo cuando se pide (mismo patrón que los demás módulos).
"""

from typing import TYPE_CHECKING, Any

from app.modules.identity.dependencies import (
    build_admin_granter,
    build_farm_member_lookup,
    build_member_farm_ids,
    build_membership_check,
    build_membership_directory,
    build_password_hasher,
    build_user_email_lookup,
    get_current_user,
    has_permission_anywhere,
    oauth2_scheme,
    require_permission,
)
from app.modules.identity.models import User
from app.modules.identity.schemas import DocumentType, MessageResponse, UserResponse

if TYPE_CHECKING:
    from fastapi import APIRouter

    api_router: APIRouter

__all__ = [
    "DocumentType",
    "MessageResponse",
    "User",
    "UserResponse",
    "api_router",
    "build_admin_granter",
    "build_farm_member_lookup",
    "build_member_farm_ids",
    "build_membership_check",
    "build_membership_directory",
    "build_password_hasher",
    "build_user_email_lookup",
    "get_current_user",
    "has_permission_anywhere",
    "oauth2_scheme",
    "require_permission",
]


def __getattr__(name: str) -> Any:
    if name == "api_router":
        from app.modules.identity.router import router

        return router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
