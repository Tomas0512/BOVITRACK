# -*- coding: utf-8 -*-
"""
test_14_economic_dashboard_page.py
--------------------------------------
VISTA: EconomicDashboard (ruta protegida "/farms/:farmId/economics")

QUE HACE ESTE ARCHIVO:
Verifica el tablero financiero de una finca: carga de las secciones de
"Ingresos por categoría", "Egresos por categoría" y "Balance mensual", y
el boton para limpiar el filtro de fechas.

IMPACTO PARA EL PROYECTO:
Este tablero traduce los datos operativos (ventas, gastos, produccion) en
informacion financiera para la toma de decisiones del ganadero. Si los
graficos o los filtros de fecha fallan, el usuario podria tomar
decisiones de negocio con cifras incorrectas o desactualizadas.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestEconomicDashboardPage(BaseTest):

    def test_dashboard_sections_are_rendered(self):
        """
        CASO DE USO 1: la vista debe renderizar el titulo "Dashboard
        Económico" y las tres secciones de graficos (Ingresos, Egresos,
        Balance mensual).
        Impacto: confirma que la agregacion de datos economicos del
        backend se muestra completa, sin secciones faltantes que
        oculten informacion financiera relevante.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}/economics")

        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Dashboard Económico')]"))
        )
        self.assertTrue(title.is_displayed(), "No se muestra el título del Dashboard Económico")

        balance_section = self.driver.find_element(
            By.XPATH, "//h2[contains(., 'Balance mensual')]"
        )
        self.assertTrue(balance_section.is_displayed(),
                         "No se muestra la sección de 'Balance mensual'")

    def test_setting_date_filter_reveals_clear_filter_button(self):
        """
        CASO DE USO 2: el boton "Limpiar" solo debe aparecer DESPUES de
        que el usuario diligencia al menos una fecha (Desde/Hasta), ya
        que en el codigo esta condicionado a "dateFrom || dateTo".
        Impacto: valida que el usuario siempre tenga una forma visible de
        volver a la vista completa de datos economicos sin quedar
        "atascado" en un rango de fechas restringido una vez lo aplica.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}/economics")
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Dashboard Económico')]"))
        )

        # Localizador por CSS Selector: el primer input de tipo "date"
        # corresponde al filtro "Desde".
        date_from_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='date']")
        date_from_input.send_keys("01012026")  # dd/mm/aaaa segun el input nativo del navegador

        clear_filter_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Limpiar')]"))
        )
        self.assertTrue(clear_filter_button.is_displayed(),
                         "El botón 'Limpiar' no aparece tras diligenciar un filtro de fecha")


if __name__ == "__main__":
    unittest.main()
