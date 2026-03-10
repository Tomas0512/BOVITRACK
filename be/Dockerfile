# ── Imagen del Backend BoviTrack (FastAPI) ───────────────────
#
# ¿Qué?    Multi-stage build con dos etapas: builder y runtime.
# ¿Para?   La etapa builder compila dependencias con gcc;
#           la etapa runtime es una imagen mínima sin herramientas de compilación.
# ¿Impacto? Sin multi-stage, gcc y libpq-dev quedan en la imagen final:
#           ~100 MB extra, mayor superficie de ataque, herramientas de
#           compilación disponibles si hay un exploit en la app.

# ── Builder: compila e instala dependencias Python ────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# gcc y libpq-dev: solo necesarios en esta etapa para compilar extensiones C.
# NO llegan a la imagen final.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# --prefix=/install: instala paquetes en directorio aislado para
# poder copiarlos limpiamente a la etapa runtime.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime: imagen mínima sin herramientas de compilación ────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copiar únicamente los paquetes Python instalados (sin gcc, sin libpq-dev).
# psycopg2-binary bundlea libpq internamente → no se necesita libpq5 en runtime.
COPY --from=builder /install /usr/local

# ¿Qué?    Usuario del sistema sin privilegios para ejecutar la app.
# ¿Para?   Principio de mínimo privilegio.
# ¿Impacto? Sin esto, la app corre como root dentro del contenedor.
#           Si hay un exploit, el atacante obtiene root en el contenedor,
#           facilitando escape al host o movimiento lateral.
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# --chown: asigna ownership en la misma instrucción COPY (evita capa extra).
COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

# ¿Qué?    Health check que verifica que FastAPI responde en el endpoint raíz.
# ¿Para?   Docker (y orquestadores como Swarm/Kubernetes) usan este estado
#           para decidir si el contenedor está sano antes de enviarle tráfico.
# ¿Impacto? Sin HEALTHCHECK, Docker reporta el contenedor como "running" aunque
#           uvicorn haya crasheado o la app esté colgada.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
