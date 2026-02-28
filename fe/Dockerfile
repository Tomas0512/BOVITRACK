# ── Imagen del Frontend BoviTrack (React + Vite) ─────
# Desarrollo: ejecuta pnpm dev en el puerto 5173.

FROM node:20-alpine

WORKDIR /app

# Habilitar pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copiar archivos de dependencias primero (cache de Docker)
COPY package.json pnpm-lock.yaml ./

# Instalar dependencias
RUN pnpm install --frozen-lockfile

# Copiar el resto del código fuente
COPY . .

# Puerto del frontend (Vite dev server)
EXPOSE 5173

# Comando de arranque — servidor de desarrollo
CMD ["pnpm", "dev", "--host"]
