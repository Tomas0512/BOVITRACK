# Modelos ORM de BoviTrack
# Aquí se importan todos los modelos para que Alembic los detecte automáticamente.
# Cada vez que crees un nuevo modelo, impórtalo aquí.

from app.models.user import User
from app.models.password_reset_token import PasswordResetToken

__all__ = ["User", "PasswordResetToken"]
