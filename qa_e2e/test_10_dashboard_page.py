# -*- coding: utf-8 -*-
"""
test_10_dashboard_page.py
-----------------------------
VISTA: DashboardPage (ruta protegida "/dashboard")

QUE HACE ESTE ARCHIVO:
Usa el metodo self.login() heredado de BaseTest para autenticarse antes
de cada prueba (setUp -> login), y luego valida que el saludo
personalizado al usuario y el enlace de "Crear finca" esten disponibles.

IMPACTO PARA EL PROYECTO:
Es la pantalla "central" a la que llega el usuario tras autenticarse; es
el punto de partida hacia el resto de la aplicacion (fincas, bovinos,
reportes). Si este componente falla, el usuario queda bloqueado justo
despues de iniciar sesion, aunque el login en si haya funcionado.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestDashboardPage(BaseTest):

    def test_authenticated_user_sees_personalized_greeting(self):
        """
        CASO DE USO 1: tras iniciar sesion, el Dashboard debe mostrar un
        saludo con el nombre del usuario autenticado ("Bienvenido, {nombre}!").
        Impacto: confirma que el token de sesion se uso correctamente
        para obtener los datos del usuario desde el backend (FastAPI).
        """
        self.login()

        greeting = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Bienvenido,')]"))
        )
        self.assertTrue(greeting.is_displayed(),
                         "No se muestra el saludo personalizado en el Dashboard")

    def test_create_farm_link_navigates_to_farm_form(self):
        """
        CASO DE USO 2: el enlace "Crear finca" (visible para el rol
        Administrador) debe llevar a la vista CreateFarmPage ("/farms/new").
        Impacto: valida el punto de entrada principal para dar de alta
        una nueva finca, funcionalidad base de todo el sistema BoviTrack.
        """
        self.login()

        create_farm_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Crear finca"))
        )
        create_farm_link.click()

        self.wait.until(EC.url_contains("/farms/new"))
        self.assertIn("/farms/new", self.driver.current_url,
                       "El enlace 'Crear finca' no navega a /farms/new")


if __name__ == "__main__":
    unittest.main()
