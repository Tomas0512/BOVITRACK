# -*- coding: utf-8 -*-
"""
test_01_home_page.py
---------------------
VISTA: HomePage (ruta "/")

QUE HACE ESTE ARCHIVO:
Verifica que la pagina de aterrizaje (landing page) publica de BoviTrack
cargue correctamente y que sus enlaces principales de navegacion (Header)
lleven al usuario a Login y a Registro.

IMPACTO PARA EL PROYECTO:
La HomePage es la puerta de entrada de TODOS los usuarios nuevos. Si el
titulo principal no carga o los botones de "Iniciar sesion"/"Registrarse"
no funcionan, se pierde la captacion de nuevos ganaderos usando la
plataforma, por lo que es la vista con mayor prioridad de negocio.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestHomePage(BaseTest):

    def test_hero_title_is_visible(self):
        """
        CASO DE USO 1: El titulo principal (hero) de la landing page debe
        ser visible al cargar la vista.
        Impacto: si este elemento no aparece, el usuario no entiende de
        que trata el producto y probablemente abandona la pagina.
        """
        self.driver.get(config.BASE_URL)

        # Localizador por XPath relativo, filtrando por el texto de marca
        # dentro del encabezado <h1>. Se prefiere sobre un XPath absoluto
        # porque no se rompe si se reordenan secciones de la pagina.
        hero_title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'BoviTrack')]"))
        )
        self.assertTrue(hero_title.is_displayed(), "El titulo principal (hero) no es visible")

    def test_navigation_links_to_login_and_register(self):
        """
        CASO DE USO 2: Los enlaces "Iniciar sesion" y "Registrarse" del
        header deben redirigir a las rutas /login y /register.
        Impacto: son los dos unicos caminos de entrada al sistema; un
        enlace roto aqui bloquea por completo la adquisicion de usuarios.
        """
        self.driver.get(config.BASE_URL)

        login_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Iniciar sesión"))
        )
        login_link.click()
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url,
                       "El enlace 'Iniciar sesión' no redirige a /login")

        # Regresamos a Home para probar el segundo enlace de forma aislada.
        self.driver.get(config.BASE_URL)
        register_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Registrarse"))
        )
        register_link.click()
        self.wait.until(EC.url_contains("/register"))
        self.assertIn("/register", self.driver.current_url,
                       "El enlace 'Registrarse' no redirige a /register")


if __name__ == "__main__":
    unittest.main()
