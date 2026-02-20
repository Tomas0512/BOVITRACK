"""
Módulo: main.py
Descripción: Punto de entrada de la aplicación FastAPI — BoviTrack.
"""

from fastapi import FastAPI

app = FastAPI(
    title="BoviTrack API",
    description="API para el sistema de gestión ganadera BoviTrack",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "BoviTrack API funcionando ✅"}
