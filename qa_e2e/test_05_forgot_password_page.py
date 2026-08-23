# -*- coding: utf-8 -*-
"""
test_05_forgot_password_page.py
----------------------------------
VISTA: ForgotPasswordPage (ruta "/forgot-password")

QUE HACE ESTE ARCHIVO:
Verifica el flujo de solicitud de recuperacion de contraseña: el usuario
ingresa su correo y el sistema debe confirmar visualmente que la
solicitud fue procesada (envio de correo con enlace de restablecimiento).

IMPACTO PARA EL PROYECTO:
Es la unica via de recuperacion de acceso cuando un ganadero olvida su
contraseña. Si esta vista falla, el usuario queda bloqueado del sistema
de forma permanente (sin poder registrar produccion, sanidad, etc.) hasta
que soporte tecnico intervenga manualmente.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestForgotPasswordPage(BaseTest):

    def test_valid_email_shows_confirmation_message(self):
        """
        CASO DE USO 1 (camino feliz): al enviar un correo con formato
        valido, la vista debe mostrar un mensaje de confirmacion de envio.
        Impacto: confirma al usuario que su solicitud fue recibida,
        evitando que reintente multiples veces o abra tickets de soporte
        innecesarios pensando que el formulario no funciono.
        """
        self.driver.get(f"{config.BASE_URL}/forgot-password")

        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(config.TEST_EMAIL)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Tras el envio, la vista reemplaza el formulario por la pantalla
        # de confirmacion con el titulo "¡Correo enviado!" (ver
        # ForgotPasswordPage.tsx). Se usa XPath relativo filtrando por
        # texto porque ese encabezado no tiene un ID/clase unico expuesto.
        confirmation_heading = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h2[contains(., 'Correo enviado')]")
            )
        )
        self.assertTrue(confirmation_heading.is_displayed(),
                         "No se muestra confirmacion tras solicitar recuperacion de clave")

    def test_empty_email_is_blocked_by_required_validation(self):
        """
        CASO DE USO 2 (validacion de campo obligatorio): el formulario
        NO debe poder enviarse con el campo de correo vacio.
        Impacto: evita solicitudes de recuperacion invalidas que
        generarian ruido/errores en el backend de envio de correos.
        """
        self.driver.get(f"{config.BASE_URL}/forgot-password")

        email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))

        # El atributo HTML5 "required" es la primera linea de defensa;
        # se valida consultando la propiedad de validez nativa del campo.
        is_valid = self.driver.execute_script(
            "return arguments[0].checkValidity();", email_field
        )
        self.assertFalse(is_valid, "El campo de correo no deberia ser valido si esta vacio")


if __name__ == "__main__":
    unittest.main()
