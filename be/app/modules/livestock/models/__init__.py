"""
Tablas ORM del módulo livestock: bovinos (con identificaciones y auditoría),
pesajes y movimientos de entrada/salida del hato.
"""

from app.modules.livestock.models.bovine import Bovine, BovineAudit, BovineIdentification
from app.modules.livestock.models.movement import MOVEMENT_TYPES, AnimalMovement
from app.modules.livestock.models.weight import Weight

__all__ = ["MOVEMENT_TYPES", "AnimalMovement", "Bovine", "BovineAudit", "BovineIdentification", "Weight"]
