# Modelos ORM de BoviTrack
# Aquí se importan todos los modelos para que Alembic los detecte automáticamente.
# Cada vez que crees un nuevo modelo, impórtalo aquí.

from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.models.email_verification_token import EmailVerificationToken
from app.models.audit_log import AuditLog
from app.models.role import Role, Permission
from app.models.department import Department, City
from app.models.purpose import Purpose
from app.models.farm import Farm, UserFarm, LandPlot
from app.models.paddock import Paddock, PaddockHerd
from app.models.bovine import Bovine, BovineIdentification, BovineAudit
from app.models.food import Food, Consumption
from app.models.treatment import Treatment
from app.models.milk_production import MilkProduction
from app.models.task import Task

__all__ = [
    "User", "PasswordResetToken", "EmailVerificationToken", "AuditLog",
    "Role", "Permission",
    "Department", "City",
    "Purpose",
    "Farm", "UserFarm", "LandPlot",
    "Paddock", "PaddockHerd",
    "Bovine", "BovineIdentification", "BovineAudit",
    "Food", "Consumption",
    "Treatment",
    "MilkProduction",
    "Task",
]
