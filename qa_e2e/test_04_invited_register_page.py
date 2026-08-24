# -*- coding: utf-8 -*-
"""
test_04_invited_register_page.py
-----------------------------------
VISTA: InvitedRegisterPage (ruta "/register/invitation")

QUE HACE ESTE ARCHIVO:
Verifica el flujo de registro por invitacion, usado cuando un
administrador de finca invita a un empleado a unirse a BoviTrack. Esta
vista depende de un token de invitacion recibido por query param/URL.

IMPACTO PARA EL PROYECTO:
Es el mecanismo que permite escalar el uso de la plataforma dentro de una
misma finca (varios empleados con acceso). Si un token invalido llegara a
aceptarse, se rompe el control de acceso por invitacion; si un token
valido fuera rechazado, se bloquea la incorporacion de nuevo personal.
"""

import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestInvitedRegisterPage(BaseTest):

    def test_invalid_invitation_token_shows_error_message(self):
        """
        CASO DE USO 1 (camino negativo): al ingresar con un token de
        invitacion inexistente o expirado, la vista debe mostrar el
        mensaje "Invitación no válida" en lugar del formulario.
        Impacto: evita que cualquier persona con una URL manipulada
        pueda registrarse sin haber sido invitada realmente.
        """
        self.driver.get(f"{config.BASE_URL}/register/invitation?token=token-invalido-qa")

        error_heading = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h2[contains(., 'Invitación no válida')]")
            )
        )
        self.assertTrue(
            error_heading.is_displayed(),
            "No se muestra el mensaje de invitación no válida con un token incorrecto",
        )

    def test_invalid_invitation_page_offers_link_back_to_login(self):
        """
        CASO DE USO 2: cuando la invitacion no es valida, la vista debe
        ofrecer una salida clara al usuario (enlace de regreso a Login).
        Impacto: mejora la experiencia de usuario ante un error, evitando
        que la persona quede "atrapada" en una pantalla sin salida.
        """
        self.driver.get(f"{config.BASE_URL}/register/invitation?token=token-invalido-qa")

        back_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Ir a iniciar sesión"))
        )
        back_link.click()
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", self.driver.current_url,
                       "El enlace de la invitación inválida no regresa a /login")


if __name__ == "__main__":
    unittest.main()
