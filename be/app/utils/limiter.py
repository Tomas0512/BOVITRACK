from app.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

# ¿Por qué `enabled` es configurable? Los límites (5/min en login, 3/min en
# recuperación) protegen la API en producción, pero impiden correr la suite
# E2E completa (qa_e2e), que inicia sesión ~15 veces en pocos minutos.
# RATE_LIMIT_ENABLED=false se usa SOLO en desarrollo/QA local (docker-compose).
limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
)
