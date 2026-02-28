"""
Módulo: main.py
Descripción: Punto de entrada de la aplicación FastAPI — BoviTrack.
¿Para qué? Configura la app FastAPI: CORS, lifespan (conexión BD), routers.
¿Impacto? Toda petición HTTP pasa por aquí. Si CORS está mal configurado,
           el frontend no puede comunicarse con el backend.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.auth import router as auth_router


# ── Lifespan (arranque y apagado) ─────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Se ejecuta al arrancar y al apagar la aplicación."""
    print("🚀 BoviTrack API iniciando...")
    yield
    print("🛑 BoviTrack API detenida")


# ── Instancia de la app ──────────────────────────
app = FastAPI(
    title="BoviTrack API",
    description="API para el sistema de gestión ganadera BoviTrack",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────
app.include_router(auth_router)


# ── Health check ──────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"message": "BoviTrack API funcionando ✅"}
