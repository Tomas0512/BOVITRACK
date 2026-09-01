# 🔌 Despliegue e Infraestructura BoviTrack

> Guía para exponer el proyecto de forma remota (sustentación/demo) y conocer la
> alternativa de infraestructura gestionada (Supabase). El entorno de desarrollo
> usa Docker Compose; aquí se documenta cómo darlo a conocer en línea de forma
> segura sin comprometer secretos.

---

## 1. Asegurar el entorno antes de exponerlo

Antes de compartir el sistema, aplicar estos puntos (ver `README.md` y `docs/STACK_TECNOLOGICO.md`):

- **Puertos vinculados a `127.0.0.1`** (`docker-compose.yml`): el frontend, backend y mailpit
  solo se acceden de forma local. Esto reduce la superficie de exposición.
- **CORS restringido** (`be/app/main.py`): en producción solo se permite el `FRONTEND_URL`
  configurado; en desarrollo, `localhost`/`127.0.0.1`.
- **Credenciales** en `.env` (raíz) y NO en el repositorio (`.env` está en `.gitignore`).
- `.env.example` contiene solo valores ilustrativos — **nunca** usarlos en producción.

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
