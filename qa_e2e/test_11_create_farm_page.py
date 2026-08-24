# -*- coding: utf-8 -*-
"""
test_11_create_farm_page.py
-------------------------------
VISTA: CreateFarmPage (ruta protegida "/farms/new")

QUE HACE ESTE ARCHIVO:
Automatiza el formulario de registro de una nueva finca (wizard por
pasos), usando los localizadores By.ID definidos en CreateFarmPage.tsx:
"name", "address", "department_id", "total_area", "purpose_id" y
"farm_identifier".

IMPACTO PARA EL PROYECTO:
Registrar una finca es el primer paso obligatorio antes de poder usar
cualquier otro modulo (bovinos, empleados, lotes, alimentacion, etc.). Si
este formulario falla, el usuario queda completamente bloqueado y no
puede aprovechar ninguna otra funcionalidad de BoviTrack.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestCreateFarmPage(BaseTest):

    def test_next_step_button_disabled_with_required_fields_empty(self):
        """
        CASO DE USO 1 (validacion por pasos): con el primer paso del
        formulario vacio (nombre, direccion, departamento), el boton
        "Siguiente" no debe permitir avanzar al segundo paso.
        Impacto: evita que se cree una finca con datos de ubicacion
        incompletos, lo que afectaria reportes geograficos y filtros del
        sistema mas adelante.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/new")

        self.wait.until(EC.presence_of_element_located((By.ID, "name")))

        next_button = self.driver.find_element(
            By.XPATH, "//button[@type='button' and contains(., 'Siguiente')]"
        )
        self.assertFalse(
            next_button.is_enabled(),
            "El botón 'Siguiente' no debería habilitarse con el primer paso vacío",
        )

    def test_farm_name_field_accepts_and_reflects_typed_value(self):
        """
        CASO DE USO 2: el campo "Nombre de la finca" (By.ID: name) debe
        aceptar texto y reflejarlo correctamente en su atributo "value".
        Impacto: valida la interaccion basica de entrada de datos, punto
        de partida de toda la informacion que se guardara para esta finca.
        """
        self.login()
        self.driver.get(f"{config.BASE_URL}/farms/new")

        name_field = self.wait.until(EC.presence_of_element_located((By.ID, "name")))
        farm_name = "Hacienda QA Automatizada"
        name_field.send_keys(farm_name)

        actual_value = name_field.get_attribute("value")
        self.assertEqual(
            actual_value, farm_name,
            "El campo de nombre de finca no refleja el texto ingresado",
        )


if __name__ == "__main__":
    unittest.main()
