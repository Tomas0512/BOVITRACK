# -*- coding: utf-8 -*-
"""
run_all_tests.py
-------------------
QUE HACE:
Descubre y ejecuta automaticamente TODAS las clases de prueba de este
directorio (los 15 archivos test_01_*.py ... test_15_*.py) y muestra un
resumen final con el numero de pruebas ejecutadas, exitosas y fallidas.

IMPACTO PARA EL PROYECTO:
Permite correr la suite COMPLETA de 30 casos de prueba (15 vistas x 2
casos) con un solo comando, tal como se ejecutaria en un pipeline de
integracion continua (CI/CD), sin tener que invocar archivo por archivo.

USO:
    python run_all_tests.py
"""

import sys
import unittest


if __name__ == "__main__":
    # discover() busca automaticamente todos los archivos que empiecen
    # con "test_" en el directorio actual y los agrupa en una sola suite.
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=".", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Codigo de salida distinto de 0 si algo fallo: util para que un
    # pipeline de CI/CD marque el build como "fallido" automaticamente.
    sys.exit(0 if result.wasSuccessful() else 1)
