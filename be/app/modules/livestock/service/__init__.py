"""
Capa de negocio del módulo livestock: un servicio por agregado.
"""

from app.modules.livestock.service.bovines import BovineService
from app.modules.livestock.service.calves import CalfService
from app.modules.livestock.service.movements import MovementService
from app.modules.livestock.service.weights import WeightService

__all__ = ["BovineService", "CalfService", "MovementService", "WeightService"]
