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
# URL directa del backend (FastAPI). Se usa para preparar/limpiar datos de
# prueba via la API (ej: rechazar solicitudes de reactivacion pendientes)
# sin depender de la interfaz.
API_URL = "http://localhost:8000"

# Credenciales del usuario demo creado por be/seed_test_data.py (usuario
# admin de la finca "Hacienda El Porvenir", con acceso a todas las vistas).
TEST_EMAIL = "admin@bovitrack.com"
TEST_PASSWORD = "Demo1234!"

# Credenciales invalidas, usadas en los casos de prueba negativos (login
# fallido) para verificar que el sistema RECHAZA correctamente el acceso.
INVALID_EMAIL = "usuario_no_existe@bovitrack.com"
INVALID_PASSWORD = "ClaveIncorrecta123!"

# Correo de una cuenta DESACTIVADA creada por be/seed_test_data.py. La usa
# test_09 (solicitud de reactivacion): el backend rechaza con 400 a cuentas
# activas ("La cuenta ya esta activa"), por lo que el camino feliz requiere
# un usuario con is_active=False.
INACTIVE_USER_EMAIL = "exempleado@bovitrack.com"

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
# UUIDs reales generados por be/seed_test_data.py en la base de datos de
# pruebas (finca "Hacienda El Porvenir" y uno de sus bovinos activos).
TEST_FARM_ID = "a71fac9a-42d1-43a9-9d91-4818555c90e8"
TEST_BOVINE_ID = "3ba35534-fead-4ad1-8817-defd607d4eea"

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
