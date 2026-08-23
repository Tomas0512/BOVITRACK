# -*- coding: utf-8 -*-
"""
test_06_reset_password_page.py
----------------------------------
VISTA: ResetPasswordPage (ruta "/reset-password")

QUE HACE ESTE ARCHIVO:
Verifica el formulario de restablecimiento de contraseña, al que se llega
con un token en el query param (?token=xxx) enviado por correo desde
ForgotPasswordPage. Usa los localizadores By.ID sobre "password" y
"confirmPassword".

IMPACTO PARA EL PROYECTO:
Cierra el ciclo de recuperacion de cuenta. Si el boton de envio permitiera
una contraseña que no cumple los requisitos minimos (8 caracteres,
mayuscula, minuscula, numero, caracter especial segun la barra de
fortaleza del formulario), se debilitaria la seguridad de las cuentas de
todos los ganaderos que usen esta funcionalidad.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestResetPasswordPage(BaseTest):

    def test_missing_token_shows_invalid_link_message(self):
        """
        CASO DE USO 1 (camino negativo): al entrar SIN el parametro
        "token" en la URL, la vista debe mostrar "Enlace inválido" en
        lugar del formulario de restablecimiento.
        Impacto: evita que un usuario intente restablecer una contraseña
        sin haber pasado por el flujo legitimo de "Olvidé mi contraseña".
        """
        self.driver.get(f"{config.BASE_URL}/reset-password")

        invalid_link_heading = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Enlace inválido')]"))
        )
        self.assertTrue(invalid_link_heading.is_displayed(),
                         "No se muestra 'Enlace inválido' al faltar el token en la URL")

    def test_submit_button_disabled_with_weak_or_mismatched_password(self):
        """
        CASO DE USO 2 (validacion de negocio): con un token presente pero
        una contraseña que NO cumple los requisitos minimos o que no
        coincide con su confirmacion, el boton de envio debe permanecer
        deshabilitado.
        Impacto: es la ultima barrera antes de guardar una contraseña
        debil en el sistema; si fallara, se comprometeria la seguridad de
        la cuenta del usuario que la restablece.
        """
        self.driver.get(f"{config.BASE_URL}/reset-password?token=token-de-prueba-qa")

        password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_field.send_keys("abc")  # Deliberadamente debil y corta.
        self.driver.find_element(By.ID, "confirmPassword").send_keys("no-coincide")

        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertFalse(
            submit_button.is_enabled(),
            "El boton de restablecer contraseña deberia estar deshabilitado con datos invalidos",
        )


if __name__ == "__main__":
    unittest.main()
