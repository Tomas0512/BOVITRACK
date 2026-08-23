# -*- coding: utf-8 -*-
"""
test_08_privacy_page.py
--------------------------
VISTA: PrivacyPage (ruta "/privacy")

QUE HACE ESTE ARCHIVO:
Verifica que la Politica de Tratamiento de Datos Personales cargue
correctamente con sus 10 secciones (definidas en PrivacyPage.tsx), ya que
esta pagina respalda el checkbox "acceptDataPolicy" del formulario de
registro.

IMPACTO PARA EL PROYECTO:
En Colombia el tratamiento de datos personales esta regulado por la
Ley 1581 de 2012 (habeas data). Si esta politica no es accesible o esta
incompleta, la empresa podria incumplir requisitos legales de
transparencia frente a los datos que BoviTrack recolecta de sus usuarios.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestPrivacyPage(BaseTest):

    def test_page_title_is_displayed(self):
        """
        CASO DE USO 1: el encabezado principal (h1) debe ser visible al
        cargar la ruta "/privacy".
        Impacto: confirma que la politica de privacidad es accesible de
        forma independiente, sin necesidad de haber iniciado sesion.
        """
        self.driver.get(f"{config.BASE_URL}/privacy")

        title = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertTrue(title.is_displayed(), "El titulo de la Política de Privacidad no es visible")

    def test_all_ten_sections_are_present(self):
        """
        CASO DE USO 2: el documento debe contener las 10 secciones
        numeradas (Responsable del tratamiento, Datos recopilados,
        Finalidad, Derechos del titular, Medidas de seguridad,
        Transferencia de datos, Conservación, Modificaciones, Contacto y
        Marco normativo).
        Impacto: detecta ediciones accidentales que eliminen contenido
        legalmente requerido de la politica de datos personales.
        """
        self.driver.get(f"{config.BASE_URL}/privacy")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        section_headings = self.driver.find_elements(By.CSS_SELECTOR, "main h2")
        self.assertEqual(
            len(section_headings), 10,
            f"Se esperaban 10 secciones en Política de Privacidad, se encontraron {len(section_headings)}",
        )


if __name__ == "__main__":
    unittest.main()
