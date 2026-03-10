# ── Imagen del Frontend BoviTrack (React + Vite → nginx) ──────
#
# ¿Qué?    Multi-stage build: Node/pnpm compila el proyecto React,
#           nginx:alpine sirve los estáticos resultantes.
# ¿Para?   Vite Dev Server NO es apto para producción: sin compresión,
#           sin caché HTTP, sin minificado, consumo de CPU innecesario.
#           nginx sirve estáticos de forma eficiente y hace de proxy
#           inverso hacia el backend (ver nginx.conf).
# ¿Impacto? La imagen final pasa de ~400 MB (Node) a ~23 MB (nginx:alpine).
#           Menos superficie de ataque, arranque más rápido, requests más rápidos.

# ── Builder: compila el proyecto React ────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

# ¿Qué?    VITE_API_URL como ARG de build (no como ENV en runtime).
# ¿Para?   Vite embebe en el bundle JS las variables VITE_* en tiempo
#           de compilación (no existen en el navegador como env vars).
# ¿Impacto? Si se pasa como variable de entorno de runtime, el frontend
#           no la ve. El valor /api/v1 funciona porque nginx proxia /api/
#           al backend dentro de la red Docker.
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

RUN pnpm build

# ── Runtime: nginx sirve los estáticos compilados ─────────────
FROM nginx:alpine AS runtime

# Copiar únicamente el output de compilación (dist/), sin node_modules ni fuentes.
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx.conf configura la SPA (fallback a index.html) y el proxy /api/ → be:8000.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
