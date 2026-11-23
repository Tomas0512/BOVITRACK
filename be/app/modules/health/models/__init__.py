"""
Tablas ORM del módulo health: tratamientos aplicados y planes sanitarios programados.
Se reexportan aquí para que el registro de modelos (app/models/__init__.py) y el
resto del módulo importen desde un solo lugar.
"""

from app.modules.health.models.sanitary_plan import SanitaryPlan
from app.modules.health.models.treatment import Treatment

__all__ = ["SanitaryPlan", "Treatment"]
