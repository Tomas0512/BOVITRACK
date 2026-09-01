# -*- coding: utf-8 -*-
"""
test_16_verify_email_page.py
---------------------------------
VISTA: VerifyEmailPage (ruta publica "/verify-email")

QUE HACE ESTE ARCHIVO:
Verifica la pagina de confirmacion de correo (R34). Como la verificacion
solo muestra exito con un token REAL (valido en la base de datos) y un test
E2E no puede generarlo desde la interfaz, esta prueba valida el caso
determinista: al entrar sin token (o con un token invalido) la pagina debe
mostrar el mensaje de enlace invalido, confirmando que la vista existe y
maneja correctamente el error.

IMPACTO PARA EL PROYECTO:
La confirmacion por correo es parte del flujo de registro (R34). Este test
garantiza que la ruta /verify-email esta disponible y que no rompe cuando
falta el token, evitando una pantalla en blanco o un error no controlado.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestVerifyEmailPage(BaseTest):

    def test_missing_token_shows_invalid_link_message(self):
        """
        CASO DE USO 1 (camino negativo / determinista): al entrar a
        /verify-email sin token en la URL, la pagina debe mostrar el
        mensaje de enlace invalido ("No se pudo verificar" / "invalido").
        Impacto: valida que la vista existe y que el error se controla.
        """
        self.driver.get(f"{config.BASE_URL}/verify-email")

        error = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(., 'No se pudo verificar')]"))
        )
        self.assertTrue(error.is_displayed(),
                        "No aparece el mensaje de enlace inválido en /verify-email")


if __name__ == "__main__":
    unittest.main()
