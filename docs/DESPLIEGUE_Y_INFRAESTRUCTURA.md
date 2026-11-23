# 🔌 Despliegue e Infraestructura BoviTrack

> Guía para exponer el proyecto de forma remota (sustentación/demo) y conocer la
> alternativa de infraestructura gestionada (Supabase). El entorno de desarrollo
> usa Docker Compose; aquí se documenta cómo darlo a conocer en línea de forma
> segura sin comprometer secretos.

---

## 1. Asegurar el entorno antes de exponerlo

Antes de compartir el sistema, aplicar estos puntos (ver `README.md` y `docs/STACK_TECNOLOGICO.md`):

- **Puertos vinculados a `127.0.0.1`** (`docker-compose.yml`): la BD, el backend y el frontend
  solo se acceden de forma local. Esto reduce la superficie de exposición.
- **CORS restringido** (`be/app/main.py`): en producción solo se permite el `FRONTEND_URL`
  configurado; en desarrollo, `localhost`/`127.0.0.1`.
- **Credenciales** en `.env` (raíz) y NO en el repositorio (`.env` y `.env.*` están en `.gitignore`).
- `.env.example` contiene solo valores ilustrativos — **nunca** usarlos en producción.

---

## 1.1 Desarrollo vs. producción (Parte 5 del refactor)

Hay **dos** archivos de Compose:

| | `docker-compose.yml` (desarrollo) | `docker-compose.prod.yml` (producción) |
|---|---|---|
| Backend | código montado (`./be:/app`) y `--reload` | imagen construida, sin `--reload`, `WEB_CONCURRENCY` workers |
| `ENVIRONMENT` | `development` | `production` (fijo) |
| Documentación de la API | `/docs`, `/redoc`, `/openapi.json` | **apagadas** (404) |
| Puertos publicados | db, be y fe en `127.0.0.1` | **solo nginx** (`HTTP_BIND:HTTP_PORT`, por defecto `127.0.0.1:8080`) |
| Documentos subidos | `be/storage/` del equipo | volumen `documents` (sobrevive a recrear contenedores) |
| Variables | `.env` | `.env.production`; si falta una obligatoria, Compose no arranca |

**Desplegar en un servidor:**

```bash
cp .env.example .env.production      # completar con valores REALES (secretos nuevos)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.production ps    # todo "healthy"
docker compose -f docker-compose.prod.yml --env-file .env.production logs be
```

En `.env.production` son obligatorias: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `SECRET_KEY`
(mínimo 32 caracteres), `FRONTEND_URL` (la URL pública con `https://`) y `EMAIL_BACKEND`.

**La API se niega a arrancar en producción** (y el log dice por qué) si:
- `EMAIL_BACKEND` no es `smtp` ni `resend` (con `log`, los enlaces de recuperación de contraseña quedarían en los logs y nadie recibiría los correos);
- `EMAIL_BACKEND=smtp` sin `SMTP_HOST`, o `resend` sin `RESEND_API_KEY`;
- `RATE_LIMIT_ENABLED` está en `false`.

**Lo que hace el contenedor al arrancar** (`be/entrypoint.sh`): aplica las migraciones de Alembic y, solo si salen bien,
arranca uvicorn. Si una migración falla, el contenedor se detiene en vez de servir con un esquema viejo.

**IP real del cliente:** nginx sobrescribe `X-Forwarded-For` con la IP que ve, y uvicorn (`--proxy-headers`) la usa.
Así el límite de intentos de login es **por usuario** y no compartido por todos. Si delante de nginx hay otro proxy
(Cloudflare, Caddy), nginx verá la IP de ese proxy: hay que configurar `real_ip` en nginx para ese caso.

**HTTPS:** nginx escucha en HTTP. Delante debe ir un proxy con TLS (Caddy, Cloudflare Tunnel — sección 2 —, el
balanceador del proveedor…) apuntando a `HTTP_BIND:HTTP_PORT`.

**Respaldo:** los datos están en los volúmenes `bovitrack-prod_pgdata` (BD) y `bovitrack-prod_documents` (archivos).
Respaldar la BD con `docker compose -f docker-compose.prod.yml exec db pg_dump -U <usuario> <bd> > respaldo.sql`.

**Limitaciones conocidas** (para la Parte 6):
- El bloqueo por intentos de login vive en memoria: con `WEB_CONCURRENCY` > 1 cada proceso lleva su propia cuenta.
- Las migraciones corren al arrancar: con varias réplicas de la API habría que correrlas una sola vez, aparte.

---

## 2. Exponer localmente con un túnel (Cloudflare Tunnel)

La opción más rápida y sin necesidad de subir a un hosting es crear un túnel seguro
desde la máquina hacia Internet, que enruta las peticiones a `http://localhost:5173`
(frontend) o `http://localhost:8000` (backend).

### Requisitos
- Una cuenta gratuita de Cloudflare.
- `cloudflared` instalado en la máquina donde corre Docker.

### Paso a paso (túnel rápido, sin dominio propio)
```bash
cloudflared tunnel --url http://localhost:5173
```
Cloudflare genera una URL pública aleatoria (`https://<hash>.trycloudflare.com`)
que reenvía al frontend. Nginx (contenedor `fe`) proxia `/api` al backend
internamente, así que la demo completa funciona a través de una sola URL.

### Alternativa con dominio propio (recomendado para sustentación)
1. Añadir el dominio en el dashboard de Cloudflare (Zero Trust → Networks → Tunnels).
2. Crear `access` del túnel apuntando a la app local:
   ```yaml
   # cloudflared/config.example.yml
   tunnel: <TUNNEL_ID>
   credentials-file: /home/cloudflared/.cloudflared/<TUNNEL_ID>.json
   ingress:
     - hostname: demo.bovitrack.com
       service: http://localhost:5173
     - service: http_status:404
   ```
3. Ejecutar:
   ```bash
   cloudflared tunnel run demo.bovitrack.com
   ```

> ⚠️ **Seguridad:** al exponer en Internet, el acceso queda abierto a terceros.
> Para la demo, evitar publicar datos sensibles reales o proteger con un
> `Access` / contraseña de Cloudflare.

---

## 3. Salud y registros al acceder en línea

```bash
# Estado de los contenedores
docker compose ps

# Logs del backend (migraciones, correo, errores)
docker compose logs be

# Recrear contenedores tras cambios en docker-compose.yml
docker compose up -d --build
```

---

## 4. Alternativa con infraestructura gestionada (Supabase)

Supabase ofrece PostgreSQL gestionado + Autenticación + Storage + API, lo cual
reemplaza el `db` y parte de la lógica de autenticación del stack actual.

### Qué se puede migrar
| Capa actual | Reemplazo en Supabase |
|-------------|------------------------|
| PostgreSQL (Docker) | Supabase PostgreSQL (proyecto en la nube) |
| JWT propio | Supabase Auth (tokens de Supabase) |
| Files/Documentos | Supabase Storage |
| Realtime/Alertas | Supabase Realtime (opcional) |

### Pasos sintéticos
1. Crear un proyecto en [supabase.com](https://supabase.com) (gratuito).
2. Copiar la `DATABASE_URL` de **Project Settings → Database → Connection string**
   (usar el endpoint de pooler/conexión directa).
3. Ajustar variables en `.env`:
   ```
   DATABASE_URL=postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres
   SECRET_KEY=<valor de alta entropía>
   ```
4. Correr migraciones: `cd be && alembic upgrade head`
5. (Opcional) Autenticación por Supabase: adaptar `be/app/routers/auth.py` y el
   flujo móvil para validar con el proyecto de Supabase.

> Supabase es la alternativa "todo en uno" para dejar de depender de realizar el
> despliegue manual. Para el entorno académico, Docker + Cloudflare Tunnel suele
> ser suficiente y más simple de sustentar.

---

## 5. Checklist antes de la sustentación

- [ ] `docker compose up -d --build` levanta sin errores.
- [ ] Migraciones de Alembic aplicadas (`alembic upgrade head`).
- [ ] Frontend (`:5173`), Swagger (`:8000/docs`) y Mailpit (`:8025`) accesibles localmente.
- [ ] `.env` con credenciales reales y **no commiteado**.
- [ ] Usuario demo creado (`be/seed_test_data.py`).
- [ ] (Si se expone en línea) Túnel Cloudflare funcionando y URL verificada.
- [ ] (Opcional) Supabase configurado si se quiere infraestructura gestionada.
