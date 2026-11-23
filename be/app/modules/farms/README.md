# Módulo `farms` — Fincas, lotes, potreros y catálogos

**Endpoints:**
- `/api/v1/farms`: catálogos (`/departments`, `/departments/{id}/cities`, `/purposes`), crear (`POST ""`, y `POST /bulk` con reporte por fila), listar, consultar, actualizar y desactivar fincas.
- `/api/v1/farms/{farm_id}/land-plots`: CRUD de lotes (al crear un lote se crean también sus potreros).
- `/api/v1/farms/{farm_id}/paddocks`: CRUD de potreros, con los animales que hay en cada uno.

**Tablas propias:** `farm`, `land_plot`, `paddock`, `paddock_herd`, `department`, `city` y `purpose`.
**Permisos:** fincas y lotes usan `fincas:*`; potreros usan `potreros:*`.

| Archivo | Responsabilidad |
|---|---|
| `__init__.py` | API pública: `api_router` y los puertos para otros módulos. |
| `router/` | `farms.py`, `land_plots.py` y `paddocks.py`, unidos en `router`. |
| `dependencies.py` | Arma los servicios y los puertos. Es el único archivo que conoce a identity. |
| `service/farms.py` | `FarmService` (reglas de la finca) y `CatalogService`. |
| `service/land_plots.py` | Lote con sus potreros en una sola transacción, nombres únicos y desactivación en cascada. |
| `service/paddocks.py` | Reglas de rotación y la respuesta con los animales de cada potrero. |
| `service/scope.py` | `FarmScopeService`: ¿este bovino, lote o persona es de la finca? |
| `repository.py` | Consultas, incluido el modelo de lectura de los animales por potrero. |
| `schemas/`, `models/` | Fincas y catálogos, lotes, potreros. |

## Conceptos de arquitectura

| Concepto | Respuesta para `farms` |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | Del **lugar**: la finca, cómo se divide (finca → lote → potrero) y los catálogos geográficos. También responde *"¿esto pertenece a esta finca?"* para toda la app. |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | Sí: el espacio físico de la finca. La membresía (quién trabaja ahí y con qué rol) es de identity, y los animales son de livestock. Farms solo los consulta. |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | Farms usa **solo** a identity (capa inferior). Pide la membresía del creador y la lista de fincas de un usuario por puertos, sin escribir en `user_farm`. No importa livestock: los animales de un potrero se leen de la tabla `bovine` por el esquema (modelo de lectura), y quien valida un bovino le inyecta el buscador de livestock. La finca y el potrero ya no tienen relación ORM hacia el bovino. Que farms no cargue otros módulos lo prueba `test_farms_only_loads_identity_and_boots_like_uvicorn`. |
| **Contrato** — ¿Qué garantiza? | Identificador de finca único y nombre único por municipio → `409`. El creador queda como Administrador **en la misma transacción**. Solo el dueño o un miembro activo ven la finca (`403`). Nombres de lote y de potrero únicos por finca → `409`. Un potrero cuelga de un lote activo de la misma finca y no supera su capacidad ni su área → `422`. Un lote nunca se queda sin potreros activos → `400`. La carga masiva responde `200` con `total`, `created`, `failed`, las fincas creadas (`items`) y los errores por fila (`row`, `farm_identifier`, `error`); un campo con formato inválido rechaza toda la petición con `422` e indica la fila (`items.N`). El alcance de finca responde `400` con el mismo mensaje de antes. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Un módulo pide `farms.build_farm_scope_checker(db, find_bovine=...)` y llama `check(farm_id, land_plot_id=...)`. No sabe que hay un cruce con el dueño y con identity. Igual con `build_land_plot_lookup`, `build_paddock_lookup` (devuelve un `PaddockRef`, nunca el modelo ORM) y la búsqueda por nombre de la importación CSV. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | Hacia afuera: puertos y `api_router` (team pide el nombre de la finca con `build_farm_name_lookup`). Hacia adentro: identity, solo por su API pública. Lo verifica import-linter: farms está entre livestock e identity en *"capas de módulos"*. |

## Bugs corregidos en 3e-3

| # | Antes | Ahora |
|---|---|---|
| 17 | `DELETE` de un lote daba **500**: el servicio recorría `lp.paddocks`, una relación que el modelo nunca tuvo. | Desactiva el lote y todos sus potreros. |
| 18 | Crear o renombrar un potrero con un nombre repetido en la finca daba **500** (chocaba con `uq_paddock_farm_name`). | `409 "Ya existe un potrero llamado '…' en esta finca"`. |
| 19 | Crear o renombrar una finca con el mismo nombre en el mismo departamento y municipio daba **500** (`uq_farm_name_location`). | `409 "Ya existe una finca con ese nombre en ese municipio"`. |

**Cambio de contrato (decisión del usuario):** `POST /api/v1/farms/bulk` ya no responde `201` con una lista: responde `200` con un **reporte por fila**, igual que la importación CSV de bovinos. Antes, si la tercera finca fallaba, las dos primeras quedaban creadas y el cliente solo recibía el error. Ahora cada finca es su propia transacción, las válidas se crean, y las que fallan (identificador o nombre repetidos, también dentro de la misma lista) se reportan con su fila y su motivo. La web no usaba este endpoint.

Además, crear una finca, un potrero o actualizar una finca, un lote o un potrero ahora guarda el cambio y su auditoría **en una sola transacción**. Antes eran dos commits.
