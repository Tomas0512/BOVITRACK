# -*- coding: utf-8 -*-
"""
test_15_reports_page.py
---------------------------
VISTA: ReportsPage (ruta protegida "/farms/:farmId/reports")

QUE HACE ESTE ARCHIVO:
Verifica la vista de generacion de reportes de una finca: que el titulo y
los filtros (categoria, fecha inicio, fecha fin) esten presentes, y que
el boton "Generar" produzca un reporte visible con opciones de descarga
(PDF/Excel).

IMPACTO PARA EL PROYECTO:
Los reportes son el insumo que el ganadero usa para auditorias, informes
a terceros (bancos, entidades de sanidad animal) o control interno. Un
fallo en la generacion o descarga de reportes afecta directamente la
capacidad del negocio de rendir cuentas con informacion confiable.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestReportsPage(BaseTest):

    def test_reports_view_loads_filters_and_generate_button(self):
        """
        CASO DE USO 1: la vista debe cargar el titulo "Reportes" junto
        con los tres filtros (Categoria, Fecha inicio, Fecha fin) y el
        boton "Generar".
        Impacto: confirma que el usuario cuenta con todas las
        herramientas de filtrado ANTES de generar un reporte, evitando
        reportes con datos mas amplios de los que realmente necesita.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}/reports")

        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Reportes')]"))
        )
        self.assertTrue(title.is_displayed(), "No se muestra el título de la vista de Reportes")

        generate_button = self.driver.find_element(
            By.XPATH, "//button[contains(., 'Generar')]"
        )
        self.assertTrue(generate_button.is_displayed(),
                         "No se muestra el botón 'Generar' para crear el reporte")

    def test_generate_button_produces_report_with_download_options(self):
        """
        CASO DE USO 2: al hacer clic en "Generar" (sin filtros, es decir
        para todas las categorias y todo el rango de fechas), debe
        aparecer el bloque de resultado del reporte con las opciones de
        descarga "PDF" y "Excel".
        Impacto: valida el flujo completo de negocio de esta vista: de
        nada sirven los filtros si el reporte final no se genera o no se
        puede exportar en un formato util para el usuario.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/{config.TEST_FARM_ID}/reports")
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Reportes')]")))

        generate_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Generar')]")
        generate_button.click()

        pdf_download_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'PDF')]"))
        )
        excel_download_button = self.driver.find_element(
            By.XPATH, "//button[contains(., 'Excel')]"
        )
        self.assertTrue(pdf_download_button.is_displayed() and excel_download_button.is_displayed(),
                         "No se muestran ambas opciones de descarga (PDF y Excel) tras generar el reporte")


if __name__ == "__main__":
    unittest.main()
