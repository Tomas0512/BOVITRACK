# -*- coding: utf-8 -*-
"""
base_test.py
------------
Clase base heredada por TODAS las clases de prueba del proyecto BoviTrack.

QUE HACE:
Centraliza la inicializacion (setUp) y el cierre (tearDown) del navegador
Chrome, para que cada una de las 15 clases de prueba (una por vista) NO
tenga que repetir el mismo bloque de arranque/cierre de WebDriver.
Tambien centraliza el flujo de login, ya que 5 de las 15 vistas son
protegidas (requieren sesion iniciada), y la captura de SCREENSHOTS de
evidencia al finalizar cada prueba (requisito explicito de la guia:
"Capturar una evidencia grafica del resultado final de la prueba").

IMPACTO EN EL PROYECTO:
- Aplica el principio DRY (Don't Repeat Yourself): evita duplicar en 15
  archivos el mismo codigo de creacion/cierre del driver y de login.
- Aisla cada caso de prueba: como setUp() crea un navegador NUEVO por cada
  metodo test_*, una prueba que deja datos o sesion "sucia" no afecta a
  la siguiente (principio de independencia de las pruebas automatizadas).
- Si el equipo decide migrar de Chrome a Firefox, o cambiar la estrategia
  de espera, el cambio se hace en un solo lugar y se propaga a las 30
  pruebas de la suite.
"""

import os
import unittest
from datetime import datetime

import os
from glob import glob

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


def _find_chrome() -> str | None:
    """Detecta el ejecutable de Chrome en rutas comunes de Windows."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def _find_chromedriver() -> str | None:
    """Usa un ChromeDriver ya descargado por Selenium Manager (cache local)
    para evitar la llamada de red de Selenium Manager que puede colgarse."""
    cache = os.path.expandvars(r"%USERPROFILE%\.cache\selenium")
    hits = glob(os.path.join(cache, "chromedriver", "win64", "*", "chromedriver.exe"))
    return sorted(hits)[-1] if hits else None


class BaseTest(unittest.TestCase):
    """
    Clase padre (TestCase de unittest) que agrupa la configuracion comun
    de Selenium. Las clases hijas (una por vista) solo deben preocuparse
    por escribir la logica propia de sus casos de uso.
    """

    def setUp(self):
        """
        Se ejecuta ANTES de cada metodo test_* de las clases hijas.
        Inicializa un WebDriver de Chrome "limpio" (sin cookies ni
        localStorage de una prueba anterior) para garantizar pruebas
        independientes y repetibles.
        """
        options = Options()
        # --start-maximized asegura que los elementos responsivos (menus,
        # botones de accion) se muestren igual que en un monitor de
        # escritorio, evitando falsos negativos por vista movil/colapsada.
        options.add_argument("--start-maximized")
        chrome_path = _find_chrome()
        if chrome_path:
            options.binary_location = chrome_path
        elif os.environ.get("CHROME_BIN"):
            options.binary_location = os.environ["CHROME_BIN"]

        driver_path = _find_chromedriver()
        if driver_path:
            # Usa el driver cacheadó: evita que Selenium Manager consulte la red.
            self.driver = webdriver.Chrome(options=options, service=Service(executable_path=driver_path))
        else:
            self.driver = webdriver.Chrome(options=options)

        # WebDriverWait = espera EXPLICITA: en vez de un time.sleep() fijo
        # (que desperdicia tiempo o puede ser insuficiente), Selenium
        # revisa el DOM cada poco tiempo hasta que la condicion se cumpla
        # o se agote el limite de config.EXPLICIT_WAIT_SECONDS. Esto hace
        # las pruebas mas rapidas y mas estables frente a las llamadas
        # asincronas del backend (FastAPI) que tarda en responder.
        self.wait = WebDriverWait(self.driver, config.EXPLICIT_WAIT_SECONDS)

    def tearDown(self):
        """
        Se ejecuta DESPUES de cada metodo test_*, incluso si la prueba
        fallo o lanzo una excepcion.

        1) Captura un SCREENSHOT como evidencia grafica del resultado
           final (requisito de la guia y de la lista de chequeo):
             - Prueba FALLIDA: screenshots/<test>_FAIL_<fecha>.png
             - Prueba EXITOSA: screenshots/<test>_OK_<fecha>.png
               (controlable con config.SCREENSHOT_ON_SUCCESS).
        2) Cierra el navegador para no dejar procesos de Chrome
           "huerfanos" consumiendo memoria/CPU en el equipo local o en
           el agente de CI/CD.
        """
        if getattr(self, "driver", None) is not None:
            self._capture_evidence_screenshot()
            self.driver.quit()

    # ------------------------------------------------------------------
    # Evidencia grafica: screenshot al finalizar CADA prueba
    # ------------------------------------------------------------------
    def _test_failed(self):
        """
        Detecta si el metodo de prueba actual termino en fallo/error.

        Se consulta el estado interno de unittest porque tearDown() corre
        ANTES de que el runner imprima el resumen, y su implementacion
        cambio en Python 3.11:
        - Python <= 3.10: _Outcome.errors acumula las excepciones.
        - Python >= 3.11: ese acumulador ya no existe; el fallo se registra
          de inmediato en el objeto resultado (_Outcome.result), por lo que
          basta revisar si la ultima entrada de failures/errors pertenece a
          este mismo test.
        Si no es posible determinarlo, se asume fallo para garantizar la
        captura de evidencia.
        """
        outcome = getattr(self, "_outcome", None)
        if outcome is None:
            return True
        errors = getattr(outcome, "errors", None)
        if errors is not None:
            return any(exc for _test, exc in errors if exc is not None)
        result = getattr(outcome, "result", None)
        if result is not None:
            for bucket in ("failures", "errors"):
                entries = getattr(result, bucket, [])
                if entries and entries[-1][0] is self:
                    return True
            return False
        return True

    def _capture_evidence_screenshot(self):
        """
        Guarda una captura de pantalla del estado FINAL del navegador en
        qa_e2e/screenshots/ con el nombre:
            <metodo_test>_<OK|FAIL>_<YYYYmmdd_HHMMSS>.png

        Impacto: cumple el entregable de la guia ("adjuntando la captura
        de evidencia de ejecucion") sin repetir codigo en los 15 archivos
        de prueba; ademas facilita diagnosticar fallos intermitentes.
        """
        try:
            failed = self._test_failed()
        except Exception:
            failed = True
        if not failed and not config.SCREENSHOT_ON_SUCCESS:
            return
        try:
            screenshots_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                config.SCREENSHOTS_DIR,
            )
            os.makedirs(screenshots_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_name = self.id().split(".")[-1]
            status = "FAIL" if failed else "OK"
            filepath = os.path.join(
                screenshots_dir, f"{test_name}_{status}_{timestamp}.png"
            )
            self.driver.save_screenshot(filepath)
        except WebDriverException:
            # Si el navegador ya crasheo o se cerro, no interrumpimos el
            # cierre limpio ni enmascaramos el resultado de la prueba.
            pass

    # ------------------------------------------------------------------
    # Utilidades reutilizables entre las vistas PROTEGIDAS
    # ------------------------------------------------------------------
    def login(self, email=config.TEST_EMAIL, password=config.TEST_PASSWORD):
        """
        Automatiza el flujo de inicio de sesion para llegar a las vistas
        protegidas (Dashboard, Crear/Detalle de finca, Detalle de bovino,
        Dashboard economico, Reportes) sin repetir estos mismos pasos en
        cada uno de los archivos de prueba que dependen de estar logueado.

        Impacto: si el formulario de login cambia de estructura, solo se
        actualiza este metodo y las 5 vistas protegidas siguen funcionando.
        """
        self.driver.get(f"{config.BASE_URL}/login")

        # Localizador por ID: la opcion mas rapida y estable (Regla de Oro).
        email_field = self.wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_field.clear()
        email_field.send_keys(email)

        password_field = self.driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)

        # Localizador por CSS Selector: boton de tipo submit del formulario.
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Se espera a que la URL contenga "/dashboard" como evidencia de
        # que la autenticacion fue exitosa y el token quedo almacenado.
        self.wait.until(EC.url_contains("/dashboard"))
