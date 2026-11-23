"""
Módulo: main.py
Descripción: Punto de entrada de la aplicación FastAPI — BoviTrack.
¿Para qué? Configura la app FastAPI: CORS, lifespan (conexión BD), routers,
           rate limiting, security headers.
¿Impacto? Toda petición HTTP pasa por aquí.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.modules.identity import api_router as identity_router  # auth + cuenta propia (capa base)
from app.modules.team import api_router as team_router  # empleados, invitaciones y reactivación
from app.modules.farms import api_router as farms_router  # fincas, catálogos, potreros y lotes
from app.modules.livestock import api_router as livestock_router  # bovinos, pesajes, terneros, movimientos
from app.modules.health import api_router as health_router  # tratamientos + planes sanitarios
from app.modules.milk_production import api_router as milk_production_router
from app.modules.inventory import api_router as food_router
from app.modules.tasks import api_router as tasks_router  # Módulo piloto (monolito modular)
from app.modules.reports import api_router as reports_router
from app.modules.reproduction import api_router as reproductive_events_router
from app.modules.notifications import api_router as alerts_router
from app.modules.economics import api_router as economics_router
from app.modules.documents import api_router as documents_router
from app.modules.audit import api_router as audit_router  # HU015: auditoría (sistema y por finca)
from app.core.limiter import limiter


# ── Logging ────────────────────────────────────────
# ¿Para qué? Mostrar en consola/logs los mensajes INFO del backend (incluidos
# los del envío de email), para depurar si un correo se envió o falló.
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# ── Lifespan (arranque y apagado) ─────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Se ejecuta al arrancar y al apagar la aplicación.

    Arranca la tarea programada de notificaciones (módulo notifications) y la
    detiene al apagar. Con NOTIFICATIONS_INTERVAL_MINUTES=0 no se arranca.
    """
    from app.modules.notifications import start_notification_scheduler

    print("🚀 BoviTrack API iniciando...")
    scheduler = start_notification_scheduler(settings.NOTIFICATIONS_INTERVAL_MINUTES)
    yield
    if scheduler is not None:
        scheduler.cancel()
    print("🛑 BoviTrack API detenida")


# ── Swagger condicional ──────────────────────────
_is_production = settings.ENVIRONMENT == "production"

app = FastAPI(
    title="BoviTrack API",
    description="API para el sistema de gestión ganadera BoviTrack",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if _is_production else "/docs",
    redoc_url=None if _is_production else "/redoc",
    # Sin esto, /openapi.json seguía describiendo toda la API en producción.
    openapi_url=None if _is_production else "/openapi.json",
)

# ── Rate limiter ──────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Errores de dominio ────────────────────────────
# ¿Para qué? Los servicios lanzan errores de app.shared.exceptions (sin conocer
# HTTP) y aquí se traducen a códigos de estado. Ver app/core/error_handlers.py.
register_error_handlers(app)

# ── CORS ──────────────────────────────────────────
_origins = {settings.FRONTEND_URL.rstrip("/")}
if settings.ENVIRONMENT != "production":
    # En desarrollo, aceptar localhost/127.0.0.1 para evitar bloqueos por origen.
    _origins.update(
        {
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            # Expo Web (Metro bundler)
            "http://localhost:8081",
            "http://127.0.0.1:8081",
            "http://localhost:19006",
            "http://127.0.0.1:19006",
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Security headers ─────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if "server" in response.headers:
        del response.headers["server"]
    return response


# ── Routers ───────────────────────────────────────
app.include_router(identity_router)
app.include_router(team_router)
app.include_router(farms_router)
app.include_router(livestock_router)
app.include_router(health_router)
app.include_router(milk_production_router)
app.include_router(food_router)
app.include_router(tasks_router)
app.include_router(reports_router)
app.include_router(reproductive_events_router)
app.include_router(alerts_router)
app.include_router(economics_router)  # HU010: Información económica
app.include_router(documents_router)  # HU012: Gestión de documentos
app.include_router(audit_router)  # HU015: Auditoría del sistema (filtros y exportación)


# ── Health check ──────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"message": "BoviTrack API funcionando ✅"}
