"""
Paquete: models (REGISTRO de modelos, sin modelos propios)
¿Qué? Importa los modelos ORM de todos los módulos para que queden registrados
      en Base.metadata.
¿Para qué? Alembic (alembic/env.py) y la app necesitan conocer TODAS las tablas
           para resolver relaciones por nombre y detectar cambios de esquema.
¿Impacto? Cada modelo vive en su módulo (app/modules/<modulo>/models). Al crear
          un modelo nuevo, impórtalo aquí. Es la única excepción a "solo se
          importa la API pública de un módulo" (ver pyproject.toml).
"""

from app.core.audit_trail import AuditLog
from app.modules.documents.models import Document
from app.modules.economics.models import EconomicRecord
from app.modules.farms.models import City, Department, Farm, LandPlot, Paddock, PaddockHerd, Purpose
from app.modules.health.models import SanitaryPlan, Treatment
from app.modules.identity.models import EmailVerificationToken, PasswordResetToken, Permission, Role, User, UserFarm
from app.modules.inventory.models import Consumption, Food, StockMovement
from app.modules.livestock.models import AnimalMovement, Bovine, BovineAudit, BovineIdentification, Weight
from app.modules.milk_production.models import MilkProduction
from app.modules.notifications.models import NotificationLog, UserNotificationPref
from app.modules.reproduction.models import ReproductiveEvent
from app.modules.tasks.models import Task
from app.modules.team.models import FarmInvitation, ReactivationRequest

__all__ = [
    "AnimalMovement", "AuditLog", "Bovine", "BovineAudit", "BovineIdentification", "City", "Consumption",
    "Department", "Document", "EconomicRecord", "EmailVerificationToken", "Farm", "FarmInvitation", "Food",
    "LandPlot", "MilkProduction", "NotificationLog", "Paddock", "PaddockHerd", "PasswordResetToken", "Permission",
    "Purpose", "ReactivationRequest", "ReproductiveEvent", "Role", "SanitaryPlan", "StockMovement", "Task",
    "Treatment", "User", "UserFarm", "UserNotificationPref", "Weight",
]
