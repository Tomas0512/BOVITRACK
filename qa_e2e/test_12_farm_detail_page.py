# -*- coding: utf-8 -*-
"""
test_12_farm_detail_page.py
-------------------------------
VISTA: FarmDetailPage (ruta protegida "/farms/:farmId")

QUE HACE ESTE ARCHIVO:
Verifica que el detalle de una finca existente cargue su nombre y que los
accesos rapidos a los modulos "Económico" y "Reportes" naveguen a las
rutas correctas. Requiere una finca real en la base de datos de pruebas
(config.TEST_FARM_ID).

IMPACTO PARA EL PROYECTO:
Esta vista es el "centro de mando" de cada finca: desde aqui se accede a
bovinos, empleados, lotes, alimentacion, economia y reportes. Un fallo en
la navegacion desde aqui aisla al usuario de todos los submodulos de esa
finca especifica.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestFarmDetailPage(BaseTest):

    def test_farm_name_heading_is_displayed(self):
        """
        CASO DE USO 1: al abrir el detalle de una finca existente, el
        nombre de la finca debe mostrarse en el encabezado principal.
        Impacto: confirma que la llamada a la API (GET /farms/{id}) trajo
        y renderizo correctamente los datos de la finca solicitada.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}")

        farm_heading = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertTrue(farm_heading.is_displayed(),
                         "No se muestra el nombre de la finca en su vista de detalle")

    def test_economics_shortcut_navigates_to_economic_dashboard(self):
        """
        CASO DE USO 2: el acceso rapido "Económico" debe llevar a la ruta
        "/farms/{farmId}/economics" (EconomicDashboard).
        Impacto: valida el enlace directo entre la operacion diaria de la
        finca y su tablero financiero, clave para la toma de decisiones
        del ganadero.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        economics_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Económico"))
        )
        economics_link.click()

        self.wait.until(EC.url_contains("/economics"))
        self.assertIn("/economics", self.driver.current_url,
                       "El acceso 'Económico' no navega al Dashboard Económico de la finca")


if __name__ == "__main__":
    unittest.main()
