# -*- coding: utf-8 -*-
"""
config.py
---------
Configuracion centralizada para todas las pruebas Selenium del proyecto
BoviTrack.

QUE HACE:
Define constantes reutilizables (URL base del frontend, credenciales de
un usuario de prueba, IDs de finca/bovino de prueba) que las 15 clases de
prueba importan en lugar de "quemar" (hardcodear) estos valores dentro de
cada archivo.

IMPACTO EN EL PROYECTO:
Si el entorno de pruebas cambia (por ejemplo, de localhost a un ambiente
de staging ya desplegado con Docker), basta con editar este UNICO archivo
para que las 30 pruebas (15 vistas x 2 casos) apunten al nuevo entorno,
sin tener que tocar los 15 archivos de prueba uno por uno.
"""

# URL base del frontend de BoviTrack.
# Ajustar segun el entorno: local (Vite dev server), staging o produccion.
# Con "docker-compose up" del proyecto, el frontend normalmente queda
# expuesto en el puerto 5173 (Vite) o 80 (Nginx en el contenedor de fe).
BASE_URL = "http://localhost:5173"

# Credenciales de un usuario YA REGISTRADO y ACTIVO en la base de datos de
# pruebas. Se recomienda crear un usuario fijo "qa_tester@bovitrack.com"
# usando el script be/seed_test_data.py del backend, para no depender de
# datos que puedan cambiar entre ejecuciones.
TEST_EMAIL = "qa_tester@bovitrack.com"
TEST_PASSWORD = "QaTester123!"

# Credenciales invalidas, usadas en los casos de prueba negativos (login
# fallido) para verificar que el sistema RECHAZA correctamente el acceso.
INVALID_EMAIL = "usuario_no_existe@bovitrack.com"
INVALID_PASSWORD = "ClaveIncorrecta123!"

# IDs de una finca y un bovino YA EXISTENTES en la base de datos de
# pruebas. Son necesarios para las vistas protegidas de detalle
# (FarmDetailPage, BovineDetailPage, EconomicDashboard, ReportsPage).
# IMPORTANTE: en BoviTrack estos identificadores son UUID (ver
# be/app/models/farm.py), NO numeros consecutivos. Reemplaza los valores
# de ejemplo por UUIDs REALES copiados de tu base de datos de pruebas
# (por ejemplo desde be/seed_test_data.py o consultando la tabla farms),
# con el formato "3fa85f64-5717-4562-b3fc-2c963f66afa6". Si dejas valores
# invalidos, las vistas protegidas (10 a 15) fallaran al no encontrar el
# recurso.
TEST_FARM_ID = "REEMPLAZAR_CON_UUID_DE_FINCA"
TEST_BOVINE_ID = "REEMPLAZAR_CON_UUID_DE_BOVINO"

# Carpeta (relativa a este archivo) donde base_test.py guarda los
# screenshots de evidencia que exige la guia: uno por prueba, con sufijo
# _OK si la prueba paso y _FAIL si fallo.
SCREENSHOTS_DIR = "screenshots"

# Si es True se captura screenshot tambien cuando la prueba termina bien
# (evidencia de ejecucion exitosa para entregar al instructor). Si es
# False solo se capturan las pruebas fallidas.
SCREENSHOT_ON_SUCCESS = True

# Tiempo maximo (segundos) de espera explicita para que un elemento
# aparezca en el DOM antes de que una prueba falle. 10s es un valor
# prudente para cubrir llamadas asincronas al backend (FastAPI) sin
# alargar demasiado la ejecucion de la suite.
EXPLICIT_WAIT_SECONDS = 10
