"""Modelos ORM de farms: fincas, lotes, potreros y catálogos (departamentos, ciudades, propósitos)."""

from app.modules.farms.models.department import City, Department
from app.modules.farms.models.farm import Farm, LandPlot
from app.modules.farms.models.paddock import Paddock, PaddockHerd
from app.modules.farms.models.purpose import Purpose

__all__ = ["City", "Department", "Farm", "LandPlot", "Paddock", "PaddockHerd", "Purpose"]
