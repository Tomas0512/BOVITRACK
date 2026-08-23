# -*- coding: utf-8 -*-
"""
test_07_terms_page.py
------------------------
VISTA: TermsPage (ruta "/terms")

QUE HACE ESTE ARCHIVO:
Verifica que la pagina de Terminos y Condiciones cargue con su titulo
principal y todas sus secciones numeradas (1 a 9), ya que este texto
legal es referenciado desde el checkbox "acceptTerms" del formulario de
registro.

IMPACTO PARA EL PROYECTO:
Es un documento con validez legal/contractual. Si esta pagina no carga o
esta incompleta, el consentimiento que el usuario da al marcar
"Acepto los Términos y Condiciones" en el registro pierde respaldo, lo
que representa un riesgo legal y de cumplimiento para la empresa.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestTermsPage(BaseTest):

    def test_page_title_is_displayed(self):
        """
        CASO DE USO 1: el encabezado principal (h1) de la pagina debe ser
        visible al cargar la ruta "/terms".
        Impacto: confirma que la ruta publica de terminos es accesible
        directamente por URL, como se enlaza desde el registro.
        """
        self.driver.get(f"{config.BASE_URL}/terms")

        title = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertTrue(title.is_displayed(), "El titulo de Términos y Condiciones no es visible")

    def test_all_nine_sections_are_present(self):
        """
        CASO DE USO 2: el documento debe contener las 9 secciones
        numeradas definidas en TermsPage.tsx (Aceptación, Descripción del
        servicio, Registro, Uso adecuado, Propiedad intelectual,
        Limitación de responsabilidad, Modificaciones, Legislación
        aplicable y Contacto).
        Impacto: detecta si, por un error de despliegue o edicion del
        contenido, se elimina o rompe accidentalmente una seccion legal
        completa del documento.
        """
        self.driver.get(f"{config.BASE_URL}/terms")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        # Localizador por CSS Selector: todos los <h2> dentro del <main>,
        # que corresponden a cada seccion numerada del documento.
        section_headings = self.driver.find_elements(By.CSS_SELECTOR, "main h2")
        self.assertEqual(
            len(section_headings), 9,
            f"Se esperaban 9 secciones en Términos y Condiciones, se encontraron {len(section_headings)}",
        )


if __name__ == "__main__":
    unittest.main()
