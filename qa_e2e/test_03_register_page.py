# -*- coding: utf-8 -*-
"""
test_03_register_page.py
--------------------------
VISTA: RegisterPage (ruta "/register")

QUE HACE ESTE ARCHIVO:
Prueba el formulario de registro de nuevos usuarios. En BoviTrack el
registro es un WIZARD de 3 pasos (ver RegisterPage.tsx):
  Paso 0 "Datos personales":     firstName, lastName, documentType,
                                 documentNumber.
  Paso 1 "Contacto y seguridad": email, phone, password, confirmPassword.
  Paso 2 "Finalizar":            checkboxes acceptTerms/acceptDataPolicy
                                 y el boton final de registro.

IMPORTANTE: el boton type='submit' SOLO existe en el paso 2; en los pasos
0 y 1 la navegacion se hace con el boton "Siguiente" (type='button'), que
dispara la validacion por paso (validateStep). Por eso los casos de este
archivo navegan el wizard real en lugar de asumir un formulario unico.

IMPACTO PARA EL PROYECTO:
El registro es el punto de entrada de TODO nuevo cliente (ganadero) al
sistema. Un error aqui (por ejemplo, permitir contrasenas que no
coinciden) compromete directamente la calidad de los datos de cuenta y
la seguridad del usuario final.
"""

import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import config
from base_test import BaseTest


class TestRegisterPage(BaseTest):

    # Localizadores reutilizables del wizard (XPath relativo por texto,
    # ya que estos botones/mensajes no exponen un id unico).
    NEXT_BUTTON = (By.XPATH, "//button[contains(., 'Siguiente')]")
    FIRST_NAME_ERROR = (
        By.XPATH,
        "//span[contains(@class, 'text-red-600') and contains(., 'Obligatorio')]",
    )
    CONFIRM_PASSWORD_ERROR = (
        By.XPATH,
        "//span[contains(@class, 'text-red-600') and contains(., 'No coinciden')]",
    )

    def _fill_step_0(self):
        """
        Diligencia el paso 0 "Datos personales" con datos validos y avanza
        al paso 1. Usa By.ID para los campos y la clase Select para el
        <select> de tipo de documento (su valor inicial es "" y
        validateStep lo exige como obligatorio).
        """
        self.driver.find_element(By.ID, "firstName").send_keys("Aprendiz")
        self.driver.find_element(By.ID, "lastName").send_keys("SENA")
        Select(self.driver.find_element(By.ID, "documentType")).select_by_value("CC")
        self.driver.find_element(By.ID, "documentNumber").send_keys("1000000000")
        self.driver.find_element(*self.NEXT_BUTTON).click()
        # Espera a que el paso 1 este renderizado antes de interactuar.
        self.wait.until(EC.presence_of_element_located((By.ID, "email")))

    def test_password_mismatch_blocks_advancing_and_shows_error(self):
        """
        CASO DE USO 1 (validacion de negocio): si "password" y
        "confirmPassword" no coinciden, el wizard NO debe avanzar al paso 2
        y debe mostrar el error "No coinciden" junto al campo.
        Impacto: evita que un usuario quede con una contrasena que el
        mismo no conoce por un error de digitacion, lo que generaria
        tickets de soporte y bloqueos de cuenta innecesarios.
        """
        self.driver.get(f"{config.BASE_URL}/register")
        self.wait.until(EC.presence_of_element_located((By.ID, "firstName")))
        self._fill_step_0()

        # Paso 1: cada contrasena cumple las reglas individualmente, pero
        # son DIFERENTES entre si (el caso que validateStep debe rechazar).
        self.driver.find_element(By.ID, "email").send_keys(
            "qa_mismatch@bovitrack.com"
        )
        self.driver.find_element(By.ID, "phone").send_keys("3001234567")
        self.driver.find_element(By.ID, "password").send_keys("ClaveSegura123!")
        self.driver.find_element(By.ID, "confirmPassword").send_keys(
            "ClaveDiferente456!"
        )
        self.driver.find_element(*self.NEXT_BUTTON).click()

        # Asercion 1: el mensaje "No coinciden" se muestra en pantalla.
        mismatch_error = self.wait.until(
            EC.visibility_of_element_located(self.CONFIRM_PASSWORD_ERROR)
        )
        self.assertTrue(
            mismatch_error.is_displayed(),
            "No se muestra el error 'No coinciden' con contrasenas distintas",
        )

        # Asercion 2: seguimos en el paso 1 (el campo email sigue visible)
        # y el boton submit del paso 2 aun NO existe en el DOM.
        self.assertTrue(
            self.driver.find_element(By.ID, "email").is_displayed(),
            "El wizard avanzo de paso aunque las contrasenas no coinciden",
        )
        self.assertEqual(
            len(self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")),
            0,
            "El boton de registro final esta accesible sin validar las contrasenas",
        )

    def test_empty_required_fields_block_advancing_from_step_0(self):
        """
        CASO DE USO 2 (validacion de campos obligatorios): al pulsar
        "Siguiente" sin diligenciar el paso 0, el wizard NO avanza y marca
        los campos con el error "Obligatorio".
        Impacto: protege la integridad de los datos de usuarios; evita
        registros incompletos que luego fallarian en otras vistas que
        dependen de esta informacion (ej. contacto por telefono/email).
        """
        self.driver.get(f"{config.BASE_URL}/register")
        self.wait.until(EC.presence_of_element_located((By.ID, "firstName")))

        # Intento de avanzar con todo vacio: validateStep(0) debe fallar.
        self.driver.find_element(*self.NEXT_BUTTON).click()

        required_error = self.wait.until(
            EC.visibility_of_element_located(self.FIRST_NAME_ERROR)
        )
        self.assertTrue(
            required_error.is_displayed(),
            "No se muestra el error 'Obligatorio' en campos vacios del paso 1",
        )
        # El paso 2 nunca se renderizo: el campo email no debe existir.
        self.assertEqual(
            len(self.driver.find_elements(By.ID, "email")),
            0,
            "El wizard permitio avanzar con campos obligatorios vacios",
        )


if __name__ == "__main__":
    unittest.main()
