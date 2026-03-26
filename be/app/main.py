"""
Módulo: main.py
Descripción: Punto de entrada de la aplicación FastAPI — BoviTrack.
¿Para qué? Configura la app FastAPI: CORS, lifespan (conexión BD), routers,
           rate limiting, security headers.
¿Impacto? Toda petición HTTP pasa por aquí.
"""

from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.farms import router as farms_router
from app.routers.bovines import router as bovines_router
from app.routers.treatments import router as treatments_router
from app.routers.milk_production import router as milk_production_router
from app.routers.food import router as food_router
from app.routers.tasks import router as tasks_router
from app.routers.paddocks import router as paddocks_router
from app.routers.reports import router as reports_router
from app.utils.limiter import limiter


# ── Lifespan (arranque y apagado) ─────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Se ejecuta al arrancar y al apagar la aplicación."""
    print("🚀 BoviTrack API iniciando...")
    yield
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
)

# ── Rate limiter ──────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
        }
    )

parsed_frontend = urlparse(settings.FRONTEND_URL)
if parsed_frontend.hostname == "localhost" and parsed_frontend.port:
    _origins.add(f"{parsed_frontend.scheme}://127.0.0.1:{parsed_frontend.port}")
elif parsed_frontend.hostname == "127.0.0.1" and parsed_frontend.port:
    _origins.add(f"{parsed_frontend.scheme}://localhost:{parsed_frontend.port}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
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
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(farms_router)
app.include_router(bovines_router)
app.include_router(treatments_router)
app.include_router(milk_production_router)
app.include_router(food_router)
app.include_router(tasks_router)
app.include_router(paddocks_router)
app.include_router(reports_router)


# ── Health check ──────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"message": "BoviTrack API funcionando ✅"}
