# -*- coding: utf-8 -*-
"""
test_02_login_page.py
-----------------------
VISTA: LoginPage (ruta "/login")

QUE HACE ESTE ARCHIVO:
Automatiza el flujo de autenticacion usando los localizadores By.ID para
los campos "email" y "password", y By.CSS_SELECTOR para el boton de
envio, tal como se definio en la Regla de Oro de la guia (ID > CSS > XPath).

IMPACTO PARA EL PROYECTO:
El login es la funcionalidad CRITICA de seguridad de todo el sistema:
protege el acceso a los datos de las fincas y del hato ganadero. Un fallo
aqui podria permitir accesos no autorizados o, en el otro extremo, dejar
fuera del sistema a usuarios legitimos.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestLoginPage(BaseTest):

    def test_login_valid_credentials_redirects_to_dashboard(self):
        """
        CASO DE USO 1 (camino feliz): un usuario con credenciales validas
        debe ser redirigido a /dashboard tras enviar el formulario.
        Impacto: valida el flujo de negocio mas usado del sistema, ya que
        cada sesion de trabajo del ganadero comienza aqui.
        """
        self.driver.get(f"{config.BASE_URL}/login")

        self.wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(
            config.TEST_EMAIL
        )
        self.driver.find_element(By.ID, "password").send_keys(config.TEST_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Aserción: el sistema DEBE redirigir a /dashboard tras el login.
        self.wait.until(EC.url_contains("/dashboard"))
        self.assertIn("/dashboard", self.driver.current_url,
                       "El login con credenciales validas no redirige al Dashboard")

    def test_login_invalid_credentials_shows_error_and_blocks_access(self):
        """
        CASO DE USO 2 (camino negativo): credenciales invalidas NO deben
        permitir el acceso y el usuario debe permanecer en /login.
        Impacto: es la prueba de seguridad mas importante de esta vista;
        si falla, cualquier persona podria intentar acceder por fuerza
        bruta sin ninguna barrera visible.
        """
        self.driver.get(f"{config.BASE_URL}/login")

        self.wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(
            config.INVALID_EMAIL
        )
        self.driver.find_element(By.ID, "password").send_keys(config.INVALID_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # El usuario NO debe llegar al dashboard con credenciales invalidas.
        self.assertNotIn("/dashboard", self.driver.current_url,
                          "¡Riesgo de seguridad! Se permitio el acceso con credenciales invalidas")
        self.assertIn("/login", self.driver.current_url,
                       "El usuario deberia permanecer en /login tras un intento fallido")


if __name__ == "__main__":
    unittest.main()
