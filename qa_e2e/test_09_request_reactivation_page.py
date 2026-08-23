# -*- coding: utf-8 -*-
"""
test_09_request_reactivation_page.py
----------------------------------------
VISTA: RequestReactivationPage (ruta "/request-reactivation")

QUE HACE ESTE ARCHIVO:
Verifica el formulario que permite a un usuario con cuenta desactivada
solicitar su reactivacion a un administrador. Como el campo de correo no
expone un atributo "id" propio, se usa By.CSS_SELECTOR sobre el atributo
"type" del input, ilustrando el uso de esta estrategia cuando ID no esta
disponible (tal como indica la Regla de Oro de la guia).

IMPACTO PARA EL PROYECTO:
Es el unico camino de recuperacion para cuentas bloqueadas/desactivadas
por un administrador (por ejemplo, tras baja de un empleado). Si falla,
un usuario legitimo queda sin forma de recuperar el acceso sin
intervencion manual directa en la base de datos.
"""

import json
import unittest
import urllib.request
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from base_test import BaseTest


class TestRequestReactivationPage(BaseTest):

    def _reject_pending_requests(self):
        """
        Limpieza de estado: el backend rechaza con 400 una nueva solicitud
        si el usuario ya tiene otra PENDIENTE ("Ya existe una solicitud de
        reactivación pendiente"). Para que este caso de uso sea repetible,
        se inicia sesion como admin via API y se rechazan las solicitudes
        pendientes del usuario desactivado antes de enviar la nueva.
        """
        login_data = json.dumps({
            "email": config.TEST_EMAIL,
            "password": config.TEST_PASSWORD,
        }).encode()
        req = urllib.request.Request(
            f"{config.API_URL}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            token = json.load(resp)["access_token"]

        auth_headers = {"Authorization": f"Bearer {token}"}
        req = urllib.request.Request(
            f"{config.API_URL}/api/v1/admin/reactivation-requests",
            headers=auth_headers,
        )
        with urllib.request.urlopen(req) as resp:
            pending = json.load(resp)

        for item in pending:
            if item.get("user_email") == config.INACTIVE_USER_EMAIL:
                reject = urllib.request.Request(
                    f"{config.API_URL}/api/v1/admin/reactivation-requests/{item['id']}/reject",
                    data=b"",
                    method="POST",
                    headers=auth_headers,
                )
                urllib.request.urlopen(reject)

    def test_valid_email_submission_shows_success_message(self):
        """
        CASO DE USO 1 (camino feliz): al enviar el correo de una cuenta
        DESACTIVADA, la vista debe mostrar "Solicitud enviada".
        Impacto: confirma al usuario que su peticion llegara a un
        administrador, evitando reintentos duplicados innecesarios.

        Nota: se usa INACTIVE_USER_EMAIL y no TEST_EMAIL porque el backend
        rechaza con 400 ("La cuenta ya está activa") las solicitudes de
        reactivacion para cuentas activas — comportamiento correcto que
        este caso de uso no ejercita.
        """
        self._reject_pending_requests()
        self.driver.get(f"{config.BASE_URL}/request-reactivation")

        email_field = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        email_field.send_keys(config.INACTIVE_USER_EMAIL)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        success_heading = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(., 'Solicitud enviada')]"))
        )
        self.assertTrue(success_heading.is_displayed(),
                         "No se muestra confirmación tras enviar la solicitud de reactivación")

    def test_submit_button_disabled_when_email_is_empty(self):
        """
        CASO DE USO 2 (validacion de campo obligatorio): el boton
        "Enviar solicitud" debe permanecer deshabilitado mientras el
        campo de correo este vacio.
        Impacto: evita solicitudes de reactivacion sin un correo al cual
        el administrador pueda responder o identificar la cuenta.
        """
        self.driver.get(f"{config.BASE_URL}/request-reactivation")

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        self.assertFalse(
            submit_button.is_enabled(),
            "El botón 'Enviar solicitud' no debería habilitarse sin un correo diligenciado",
        )


if __name__ == "__main__":
    unittest.main()
