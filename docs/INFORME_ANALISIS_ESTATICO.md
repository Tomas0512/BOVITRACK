# Informe de Análisis Estático de Código — BoviTrack

**Guía de Aprendizaje N.º 08 — Análisis Estático del Código y Calidad de Software**
Programa: Análisis y Desarrollo de Software (ADSO) — Ficha 228118

| Dato | Valor |
|---|---|
| Proyecto | BOVITRACK |
| Repositorio | https://github.com/Tomas0512/BOVITRACK |
| Herramienta | SonarQube Cloud (SonarCloud) |
| Project key | `BOVITRACK_TOMAS1594` |
| Organización | `tomas0512` |
| Dashboard | https://sonarcloud.io/summary/overall/?id=BOVITRACK_TOMAS1594 |
| Método de análisis | CI-based (GitHub Actions) |
| Commit analizado | `8305de9` (rama `main`) |
| Fecha del análisis base | 25 de noviembre de 2026 |

---

## 1. Integración realizada

El análisis se automatizó mediante GitHub Actions, de modo que cada `push` a
`main` y cada Pull Request disparan una inspección completa sin intervención
manual.

**Archivos agregados al repositorio:**

| Archivo | Función |
|---|---|
| `sonar-project.properties` | Declara la clave del proyecto, la organización, las fuentes de los tres frentes del monorepo y separa las pruebas del código de producción. |
| `.github/workflows/sonarcloud.yml` | Ejecuta `SonarSource/sonarqube-scan-action@v5` con `fetch-depth: 0`, usando el secret `SONAR_TOKEN`. |

**Decisiones técnicas documentadas:**

1. Se usó `sonarqube-scan-action@v5` en lugar del `sonarcloud-github-action@master`
   del material de apoyo, porque este último está deprecado por SonarSource.
2. Se desactivó el *Automatic Analysis* en SonarCloud. Los dos métodos son
   mutuamente excluyentes: dejarlo activo hace fallar el pipeline con el error
   *"You are running CI analysis while Automatic Analysis is enabled"*.
3. Las pruebas (`be/tests`, `**/*.test.ts(x)`) se declaran con `sonar.tests` para
   que no contaminen las métricas de deuda técnica del código de producción.

---

## 2. Métricas del escaneo inicial (línea base)

> Estado del proyecto **antes** de cualquier refactorización.

| Métrica | Valor | Calificación |
|---|---|---|
| **Quality Gate** | **Failed** | — |
| Seguridad | 29 issues | **E** |
| Fiabilidad | 216 issues | **C** |
| Mantenibilidad | 39 issues | **A** |
| Cobertura de pruebas | 0.0 % sobre 9 900 líneas | — |
| Código duplicado | 2.9 % sobre 42 000 líneas | — |
| Security Hotspots | 0 | — |
| **Deuda técnica total** | **1 888 minutos ≈ 31,5 horas** | — |

**Clasificación clásica de los 245 hallazgos:**

| Tipo | Cantidad | Severidades |
|---|---|---|
| Code Smells | 170 | mayoría Major, 10 Minor |
| Bugs | 46 | 46 Major |
| Vulnerabilidades | 29 | 1 Blocker, 1 Critical, 22 Major, 5 Minor |

**Distribución por área del monorepo:**

| Área | Bugs | Vulnerabilidades | Code Smells |
|---|---:|---:|---:|
| `fe/src` | 38 | 7 | 165 |
| `be/seed_test_data.py` | 0 | 10 | 1 |
| `fe/coverage` *(artefacto generado)* | 6 | 0 | 0 |
| `be/Dockerfile` | 0 | 5 | 0 |
| `mobile/src` | 0 | 0 | 4 |
| `qa_e2e/config.py` | 0 | 2 | 0 |
| `fe/Dockerfile` | 0 | 2 | 0 |
| `be/app` | 2 | 0 | 0 |
| `be/ver_bd.py` | 0 | 1 | 0 |
| `db/Dockerfile` | 0 | 1 | 0 |

---

## 3. Matriz de hallazgos seleccionados

Selección de **12 hallazgos** que supera el mínimo exigido por la guía
(≥ 2 Code Smells, ≥ 2 Bugs, ≥ 1 Vulnerabilidad) y cubre las 3 vulnerabilidades
por integrante.

### 3.1 Vulnerabilidades

| # | Severidad | Regla | Archivo | Línea | Descripción | Esfuerzo |
|---|---|---|---|---|---|---|
| V1 | **BLOCKER** | `secrets:S6698` | `be/ver_bd.py` | 4 | Cadena de conexión con usuario y contraseña de PostgreSQL escritos directamente en el código (`bovitrack_user:bovitrack_pass`). Cualquiera que clone el repositorio obtiene credenciales válidas. | 30 min |
| V2 | **CRITICAL** | `docker:S6470` | `be/Dockerfile` | 51 | `COPY --chown=appuser:appgroup . .` copia el contexto completo a la imagen. Sin un `.dockerignore` estricto, archivos como `.env`, claves o la carpeta `.git` terminan dentro del contenedor publicado. | 20 min |
| V3 | **MAJOR** | `tssecurity:S7044` | `fe/src/api/alerts.ts` | 120, 130 | *API Traversal*: `farmId` y `notificationId` se interpolan sin codificar en la ruta de la petición. Un valor con `../` permite alcanzar endpoints distintos del previsto. | 30 min c/u |
| V4 | **MINOR** | `tssecurity:S8476` | `fe/src/api/alerts.ts` | 120, 130 | *Client-Side Request Forgery* sobre las mismas dos líneas: entrada no saneada que determina el destino de la petición. | 20 min c/u |
| V5 | **MINOR** | `tssecurity:S8475` | `fe/src/context/FarmContext.tsx` | 39 | *Browser Storage Poisoning*: `localStorage.setItem(STORAGE_KEY, id)` persiste un identificador no validado que luego se reutiliza como `farmId` en las llamadas a la API. | 20 min |
| V6 | **MAJOR** | `python:S2068` | `qa_e2e/config.py` | 34, 39 | Contraseñas de prueba en texto plano (`TEST_PASSWORD`, `INVALID_PASSWORD`) versionadas en el repositorio. | 30 min c/u |
| V7 | **MAJOR** | `python:S2245` | `be/seed_test_data.py` | 371, 436, 549 y 7 más | Uso de `random` (generador pseudoaleatorio no criptográfico) en 10 puntos del script de datos semilla. | 10 min c/u |
| V8 | **MAJOR** | `githubactions:S7637` | `.github/workflows/sonarcloud.yml` | 45 | La acción se referencia por etiqueta (`@v5`) y no por SHA completo. Un atacante que comprometa el repositorio de la acción podría reescribir la etiqueta. | 30 min |

### 3.2 Bugs

| # | Severidad | Regla | Archivo | Línea | Descripción | Esfuerzo |
|---|---|---|---|---|---|---|
| B1 | **MAJOR** | `typescript:S3923` | `fe/src/components/bovines/BovineList.tsx` | 530, 542, 555 | `connector: next.length > 0 ? "AND" : "AND"` — el operador ternario devuelve el mismo valor en ambas ramas. La intención era `"AND"` / `"OR"`; tal como está, el filtro avanzado nunca puede construir una condición `OR`. | 15 min c/u |
| B2 | **MAJOR** | `pythonbugs:S2583` | `be/app/services/invitation_service.py` | 184, 185 | `datetime.now(...) if data.accept_terms else None` — la condición siempre evalúa a verdadero porque el esquema de entrada ya obliga a que el valor sea `True`. La rama `else` es código muerto. | 15 min c/u |
| B3 | **MAJOR** | `typescript:S9383` | `fe/src/components/paddocks/LandMap.tsx` y 34 archivos más | 81 y otros | Promesas sin `await`, sin `.catch()` ni marcado con `void`. Un rechazo en cualquiera de estas 35 llamadas produce un *unhandled rejection* silencioso: la operación falla sin que el usuario reciba aviso. | 5 min c/u |

### 3.3 Code Smells

| # | Severidad | Regla | Archivo | Línea | Descripción | Esfuerzo |
|---|---|---|---|---|---|---|
| C1 | **MAJOR** | `typescript:S8786` | `fe/src/pages/RegisterPage.tsx`, `LoginPage.tsx`, `ForgotPasswordPage.tsx`, `mobile/src/screens/auth/*` | 68, 104, 178, 37, 62, 25, 29, 45 | Expresión regular de validación de correo `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` con rendimiento superlineal por *backtracking*. Repetida en 8 lugares: además de ser ReDoS, es duplicación de una regla de negocio. | 20 min c/u |
| C2 | **MAJOR** | `typescript:S6853` | `fe/src/components/layout/AppLayout.tsx` y otros | 304, 309, 314 y 78 más | 81 etiquetas `<label>` sin asociar a su control. Es el hallazgo más numeroso del proyecto y afecta la accesibilidad de todos los formularios. | 5 min c/u |
| C3 | **MAJOR** | `typescript:S6848` | `fe/src/components/bovines/AdvancedFiltersPanel.tsx`, `BovineList.tsx` | 79, 852, 895 y 3 más | Elementos no interactivos (`<div>`, `<span>`) usados como botones, sin `role` ni soporte de teclado. | 5 min c/u |
| C4 | **MINOR** | `typescript:S7773` | `fe/src/components/layout/AppLayout.tsx` y otros | 332 y 16 más | Uso de las funciones globales `parseFloat`, `parseInt` e `isNaN` en lugar de `Number.parseFloat`, `Number.parseInt` y `Number.isNaN`. | 2 min c/u |
| C5 | — | *(hallazgo de configuración)* | `fe/coverage/` | — | La carpeta de reportes de cobertura está versionada en Git (12 archivos generados). Produjo 6 bugs falsos en el análisis automático previo y no debería estar en el repositorio. | — |

---

## 4. Observación metodológica: falsos positivos

La regla `typescript:S2068` ("Review this potentially hard-coded password") marcó
`fe/src/pages/RegisterPage.tsx:70` y `fe/src/pages/InvitedRegisterPage.tsx:69`.
Al inspeccionar el código, esas líneas son:

```ts
if (!formData.password) newErrors.password = "Obligatorio";
```

No hay credencial alguna: la regla reacciona a la asignación de un literal a una
variable cuyo nombre contiene `password`. Es un **falso positivo**, y la acción
correcta en SonarCloud no es modificar el código, sino marcar el issue como
*False Positive* con su justificación escrita.

Esto ilustra un principio del Aseguramiento de la Calidad: el análisis estático
asiste al criterio del desarrollador, no lo sustituye. Refactorizar código
correcto solo para silenciar una regla introduce riesgo sin aportar valor.

---

## 5. Hallazgos por integrante

> Reparto propuesto de las 3 vulnerabilidades por persona que exige la actividad.
> **Pendiente de confirmación con el grupo.**

| Integrante | Hallazgos asignados | Justificación |
|---|---|---|
| *(por definir)* | V1, V2, V8 | Infraestructura y secretos: credenciales en código, Dockerfile y pipeline. |
| *(por definir)* | V3, V4, V5 | Seguridad del frontend: entrada no saneada en rutas de API y almacenamiento del navegador. |
| *(por definir)* | V6, V7, C1 | Credenciales de prueba, aleatoriedad no criptográfica y ReDoS en la validación de correo. |

---

## 6. Refactorización: primera iteración (V1, V2, V8)

Commit `17f08c8` — análisis #2 sobre `main`.
Las tres vulnerabilidades quedaron en estado `CLOSED / FIXED` en SonarCloud.

### V1 — Credenciales de PostgreSQL en código (`secrets:S6698`, BLOCKER)

**Antes** — `be/ver_bd.py:4`

```python
"""Script temporal para ver las tablas y datos de la BD."""
import psycopg2

conn = psycopg2.connect("postgresql://bovitrack_user:bovitrack_pass@localhost:5432/bovitrack_db")
```

**Después**

```python
import os
import sys

import psycopg2

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    sys.exit(
        "Falta la variable de entorno DATABASE_URL.\n"
        "Ejemplo:  DATABASE_URL=postgresql://usuario:clave@localhost:5432/bovitrack_db python ver_bd.py"
    )

conn = psycopg2.connect(database_url)
```

*Criterio aplicado:* no se inventó un mecanismo nuevo de configuración. El
repositorio ya leía `DATABASE_URL` del entorno en `be/check_tables.py` y en
`be/app/config.py`; la corrección alinea este script con ese patrón existente.

### V2 — Copia recursiva del contexto de build (`docker:S6470`, CRITICAL)

**Antes** — `be/Dockerfile:51`

```dockerfile
COPY --chown=appuser:appgroup . .
```

**Después**

```dockerfile
COPY --chown=appuser:appgroup app ./app
COPY --chown=appuser:appgroup alembic ./alembic
COPY --chown=appuser:appgroup alembic.ini entrypoint.sh ./
```

*Criterio aplicado:* el proyecto ya tenía `be/.dockerignore`, pero una lista de
exclusión es frágil —basta con que alguien agregue un archivo y no la
actualice—. Declarar explícitamente lo que entra invierte la lógica: lo que no
se nombra, no viaja. Los scripts `seed_*.py`, `ver_bd.py`, `check_tables.py` y
la carpeta `tests/` dejaron de empaquetarse en la imagen de producción.

**Verificación ejecutada:**

```
$ docker build -t bovitrack-be .          → build correcto
$ docker run ... ls -A /app               → alembic  alembic.ini  app  entrypoint.sh  storage
$ docker run ... python -c "import app.main"  → app.main OK
```

### V8 — Acción de GitHub sin fijar (`githubactions:S7637`, MAJOR)

**Antes** — `.github/workflows/sonarcloud.yml:45`

```yaml
uses: SonarSource/sonarqube-scan-action@v5
```

**Después**

```yaml
uses: SonarSource/sonarqube-scan-action@2f77a1ec69fb1d595b06f35ab27e97605bdef703 # v5
```

*Criterio aplicado:* una etiqueta de Git es móvil y quien controle ese
repositorio puede reapuntarla a otro commit. Como esta acción recibe
`SONAR_TOKEN` y lee todo el código fuente, un cambio así se ejecutaría aquí con
acceso al secret. El comentario `# v5` conserva la legibilidad.

### Impacto medido

| Métrica | Antes (`8305de9`) | Después (`17f08c8`) | Variación |
|---|---:|---:|---|
| **Security Rating** | **E** | **C** | ▲ 2 niveles |
| Vulnerabilidades | 29 | 27 | −2 |
| Bugs | 46 | 38 | −8 |
| Code Smells | 170 | 170 | = |
| **Deuda técnica** | **1 888 min** | **898 min** | **−52 %** |
| Quality Gate | Failed | Failed | sin cambio |

El salto de **E a C** en seguridad se explica porque la calificación la
determina la vulnerabilidad más grave abierta: al cerrarse el único Blocker y el
único Critical del proyecto, el peor caso restante pasa a ser Major.

La reducción de bugs y de deuda técnica es mayor que las tres correcciones por
sí solas: al dejar de indexarse los archivos generados de `fe/coverage/`, que el
análisis automático previo había incluido, sus hallazgos se cerraron también.

El Quality Gate sigue en *Failed* porque su condición es *Security Rating on New
Code > 1*, es decir, exige calificación **A** sobre el código nuevo. Alcanzarla
requiere resolver las vulnerabilidades restantes.

---

## 7. Estado

- [x] Integración de SonarCloud con GitHub Actions
- [x] Escaneo inicial y captura de la línea base
- [x] Matriz de hallazgos
- [x] Refactorización — iteración 1: V1, V2, V8 (3 vulnerabilidades)
- [ ] Refactorización — iteración 2: V3, V4, V5
- [ ] Refactorización — iteración 3: V6, V7, C1
- [ ] Corrección de bugs B1 y B2
- [ ] Marcado de falsos positivos (`typescript:S2068`)
- [ ] Re-escaneo hasta Quality Gate *Passed*
