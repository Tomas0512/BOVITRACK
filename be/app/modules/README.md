# `app/modules` — Módulos de dominio

BoviTrack es un **monolito modular con capas**: se despliega como una sola aplicación, pero por dentro está dividida en módulos por dominio, y cada módulo tiene sus propias capas.

## Estructura de un módulo

```
app/modules/<modulo>/
├── __init__.py      API pública: exporta `api_router` y los schemas que otros necesiten
├── router.py        Capa HTTP: valida la entrada, exige permisos, llama al servicio y arma la respuesta
├── dependencies.py  Composición: arma el servicio por request y conecta colaboradores de otros dominios
├── service.py       Reglas de negocio; lanza errores de app.shared.exceptions
├── schemas.py       Contrato de entrada y salida (Pydantic)
├── repository.py    Acceso a datos (SQLAlchemy); el servicio no escribe consultas
├── models.py        Tablas ORM del módulo
└── README.md        Responde las 6 preguntas de arquitectura (plantilla abajo)
```

**Dirección de las dependencias:** `router → dependencies → service → schemas → repository → models`. Una capa nunca importa a la de arriba.

**El servicio no importa FastAPI, SQLAlchemy ni código de otros dominios.** Lo que necesita de otro dominio (p. ej. "¿este bovino es de esta finca?") lo declara como una interfaz (`Protocol`) y `dependencies.py` le entrega la implementación real. Así se puede probar con colaboradores falsos, sin base de datos.

**Por qué `api_router` y no `router`:** `from app.modules.x import router` es ambiguo, porque `router` es también el nombre del submódulo `router.py`. Con un nombre propio, import-linter puede distinguir la API pública de los internos.

**Ejemplo de referencia:** el módulo `tasks` (piloto de la Parte 2).

## Reglas entre módulos

1. Un módulo solo usa a otro a través de lo que exporta en su `__init__.py`.
2. Nunca se importa el `repository` ni el `router` de otro módulo.
3. Entre módulos solo viajan schemas, IDs y errores de dominio. Ni sesiones abiertas a mitad de una transacción ajena ni `HTTPException`.
4. `HTTPException` solo existe en `router.py`. Los servicios lanzan errores de dominio y `app/core/error_handlers.py` los traduce.
5. Las reglas se verifican con **import-linter** (`lint-imports`). Un contrato roto hace fallar el chequeo.

## Plantilla de `README.md` para cada módulo

```markdown
# Módulo `<nombre>`

Endpoints: `/api/v1/...`
Tablas: `...`

| Concepto | Respuesta |
|---|---|
| **Responsabilidad** — ¿De qué se encarga? | |
| **Cohesión** — ¿Sus tareas persiguen un mismo propósito? | |
| **Acoplamiento** — ¿Cuánto debe cambiar si otro componente cambia? | De qué módulos depende y por qué. |
| **Contrato** — ¿Qué garantiza? | Entradas, salidas y errores de cada operación pública. |
| **Abstracción** — ¿Qué necesita conocer el consumidor? | Qué expone `__init__.py` y qué queda oculto. |
| **Frontera arquitectónica** — ¿Qué puede atravesar este límite? | |
```
