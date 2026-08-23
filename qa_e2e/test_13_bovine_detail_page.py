# -*- coding: utf-8 -*-
"""
test_13_bovine_detail_page.py
---------------------------------
VISTA: BovineDetailPage (ruta protegida "/farms/:farmId/bovines/:bovineId")

QUE HACE ESTE ARCHIVO:
Verifica el detalle de un bovino especifico, incluyendo su sistema de
pestañas (tabs): "general", "productivo", "reproductivo" y "sanitario"
(definidas como constante TABS en BovineDetailPage.tsx). Requiere un
bovino real de pruebas (config.TEST_BOVINE_ID) dentro de la finca de
pruebas (config.TEST_FARM_ID).

IMPACTO PARA EL PROYECTO:
Esta es la vista con la informacion mas critica del negocio: el historial
completo de cada animal del hato (peso, salud, reproduccion, produccion).
Un fallo en el cambio de pestañas dejaria informacion vital inaccesible
para el ganadero en el momento de tomar decisiones sanitarias o de venta.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestBovineDetailPage(BaseTest):

    def test_general_tab_data_section_loads_by_default(self):
        """
        CASO DE USO 1: al abrir el detalle de un bovino, la pestaña
        "Datos generales" debe estar activa y visible por defecto (es el
        estado inicial de activeTab en el componente).
        Impacto: confirma que la informacion basica del animal (ID,
        genealogia) es lo primero que ve el usuario, sin pasos extra.
        """
        self.login()
        self.driver.get(
            f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}/bovines/{config.TEST_BOVINE_ID}"
        )

        general_section = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Datos generales')]"))
        )
        self.assertTrue(general_section.is_displayed(),
                         "La sección 'Datos generales' no se muestra por defecto")

    def test_switching_to_sanitario_tab_updates_active_view(self):
        """
        CASO DE USO 2: al hacer clic en la pestaña "Sanitario", la vista
        debe cambiar de contenido (deja de mostrarse "Datos generales").
        Impacto: valida la navegacion por pestañas, mecanismo con el que
        el usuario consulta el historial de vacunas y tratamientos, clave
        para la sanidad del hato.
        """
        self.login()
        self.driver.get(
            f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}/bovines/{config.TEST_BOVINE_ID}"
        )
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Datos generales')]")))

        # Localizador por XPath relativo filtrando por texto del boton de
        # la pestaña, ya que las pestañas no exponen un ID individual.
        sanitario_tab = self.driver.find_element(
            By.XPATH, "//button[contains(., 'Sanitario')]"
        )
        sanitario_tab.click()

        # Tras el cambio de pestaña, la sección "Datos generales" ya no
        # debería estar presente en el DOM (se desmonta al cambiar de tab).
        general_sections = self.driver.find_elements(
            By.XPATH, "//h2[contains(., 'Datos generales')]"
        )
        self.assertEqual(
            len(general_sections), 0,
            "La pestaña 'Sanitario' no reemplazó el contenido de 'Datos generales'",
        )


if __name__ == "__main__":
    unittest.main()
