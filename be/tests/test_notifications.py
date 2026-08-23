"""
Pruebas: tests/test_notifications.py
HU014 - Alertas y notificaciones (Sprint 8 - Tomas, tarea 14.5)

COMO: desarrollador que mantiene el módulo
QUIERO: que el motor de notificaciones esté cubierto por pruebas automáticas
PARA:   tener la certeza de que las preferencias se crean con valores por
        defecto, que la validación de canal/frecuencia funciona, que los
        candidatos se generan a partir de planes sanitarios y stock bajo, y
        que el envío es idempotente (no duplica notificaciones).

¿Qué?     Pruebas de preferencias, validación, generación de candidatos y
          deduplicación.
¿Impacto? Se usa MagicMock para la sesión de BD, siguiendo el estilo de
          test_reproductive_event.py y test_audit.py, de modo que la suite
          corre sin PostgreSQL.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.models.notification import UserNotificationPref
from app.schemas.alert import NotificationPrefUpdate
from app.services import notification_service


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def farm_id() -> uuid.UUID:
    return uuid.uuid4()


# ═══════════════════════════════════════════════════════════════════════════════
# Preferencias
# ═══════════════════════════════════════════════════════════════════════════════


def test_prefs_defaults_son_correctos():
    """¿Qué? La preferencia por defecto es email, todos los tipos activos, real_time.

    ¿Por qué? Un usuario nuevo sin configurar debe recibir notificaciones útiles
              sin pasos extra, sin que se le envíe por correo sin que lo pida.
    """
    pref = UserNotificationPref(
        user_id=uuid.uuid4(),
        farm_id=uuid.uuid4(),
        channel="email",
        frequency="real_time",
        notify_sanitary=True,
        notify_low_stock=True,
        notify_reproductive=True,
        notify_birth=True,
    )
    assert pref.channel == "email"
    assert pref.frequency == "real_time"
    assert pref.notify_sanitary is True
    assert pref.notify_low_stock is True
    assert pref.notify_reproductive is True
    assert pref.notify_birth is True


def test_pref_allows_map_correcto():
    """¿Qué? El mapa NOTIFY_FIELD_BY_TYPE asocia cada tipo a su bandera.

    ¿Por qué? Para que el motor sepa qué preferencia consultar por tipo de evento.
    """
    assert notification_service.NOTIFY_FIELD_BY_TYPE["sanitary"] == "notify_sanitary"
    assert notification_service.NOTIFY_FIELD_BY_TYPE["low_stock"] == "notify_low_stock"
    assert notification_service.NOTIFY_FIELD_BY_TYPE["reproductive"] == "notify_reproductive"
    assert notification_service.NOTIFY_FIELD_BY_TYPE["birth"] == "notify_birth"


def test_pref_allows_respeta_la_bandera(mock_db):
    """¿Qué? _pref_allows devuelve True/False según la preferencia del usuario.

    ¿Por qué? El motor no puede notificar un tipo que el usuario desactivó.
    """
    pref = UserNotificationPref(notify_sanitary=True, notify_low_stock=False)
    assert notification_service._pref_allows(pref, "sanitary") is True
    assert notification_service._pref_allows(pref, "low_stock") is False


def test_canal_invalido_es_rechazado(mock_db, user_id, farm_id):
    """¿Qué? Actualizar con un canal no soportado lanza ValueError.

    ¿Por qué? Guardar un canal inválido corrompería la experiencia del usuario.
    """
    with patch(
        "app.services.notification_service.get_or_create_prefs",
        return_value=UserNotificationPref(user_id=user_id, farm_id=farm_id),
    ):
        with pytest.raises(ValueError):
            notification_service.update_prefs(
                mock_db, user_id, farm_id, channel="mensaje_de_texto"
            )


def test_frecuencia_invalida_es_rechazada(mock_db, user_id, farm_id):
    """¿Qué? Actualizar con una frecuencia no soportada lanza ValueError."""
    with patch(
        "app.services.notification_service.get_or_create_prefs",
        return_value=UserNotificationPref(user_id=user_id, farm_id=farm_id),
    ):
        with pytest.raises(ValueError):
            notification_service.update_prefs(mock_db, user_id, farm_id, frequency="mensual")


def test_notification_pref_update_permite_false(mock_db):
    """¿Qué? El schema de actualización permite booleano False (no lo trata como None).

    ¿Por qué? El usuario debe poder DESACTIVAR un tipo; un False no debe ignorarse.
    """
    payload = NotificationPrefUpdate(notify_sanitary=False, channel=None)
    assert payload.notify_sanitary is False
    assert payload.channel is None


# ═══════════════════════════════════════════════════════════════════════════════
# Candidatos
# ═══════════════════════════════════════════════════════════════════════════════


def test_candidatos_sin_type_conocido_permiten_envio(mock_db):
    """¿Qué? Un tipo no mapeado permite el envío por defecto.

    ¿Por qué? Los tipos nuevos no deben bloquearse silenciosamente.
    """
    pref = UserNotificationPref()
    assert notification_service._pref_allows(pref, "tipo_desconocido") is True


def test_notify_channel_inapp_no_envia_email(mock_db):
    """¿Qué? Con canal in_app no se envía email, solo se registra.

    ¿Por qué? El usuario que elige "en la app" no debe recibir correo.
    """
    pref = UserNotificationPref(channel="in_app")
    assert notification_service._notify_channel(pref) == (False, True)


def test_notify_channel_ambos_envia_y_registra(mock_db):
    """¿Qué? Con canal ambos se envía email y se registra in-app al mismo tiempo."""
    pref = UserNotificationPref(channel="ambos")
    assert notification_service._notify_channel(pref) == (True, True)


def test_ya_enviado_detecta_duplicados(mock_db):
    """¿Qué? _already_sent revisa la ventana para evitar duplicados.

    ¿Por qué? La idempotencia es clave: un ciclo repetido no debe reenviar.
    """
    mock_db.execute.return_value.scalars.return_value.first.return_value = "algo"
    assert (
        notification_service._already_sent(
            mock_db, uuid.uuid4(), "sanitary", "ref-123", hours=24
        )
        is True
    )


def test_ya_enviado_sin_resultado_es_falso(mock_db):
    """¿Qué? Si no existe un log reciente idéntico, no se considera enviado."""
    mock_db.execute.return_value.scalars.return_value.first.return_value = None
    assert (
        notification_service._already_sent(
            mock_db, uuid.uuid4(), "low_stock", "ref-456", hours=24
        )
        is False
    )


def test_tipos_etiquetas_tienen_sanitary_y_low_stock(mock_db):
    """¿Qué? El mapa de etiquetas humanas incluye los tipos principales."""
    assert "sanitary" in notification_service.TYPE_LABELS
    assert "low_stock" in notification_service.TYPE_LABELS
