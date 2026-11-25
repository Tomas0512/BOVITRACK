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

Medidas tomadas del análisis del commit `8305de9` (25/11/2026, 02:06 UTC).

### Evidencia: dashboard inicial

![Dashboard inicial de SonarCloud: Quality Gate en estado Failed sobre el commit 8305de96](img/01-dashboard-inicial-quality-gate.png)

*Figura 1 — Quality Gate **Failed** sobre el commit `8305de96`. La condición
incumplida es Security Rating sobre código nuevo: calificación obtenida **C**,
requerida **A**. El proyecto declara 32 000 líneas de código.*

![Listado de issues en SonarCloud filtrado por severidad Blocker, High y Medium](img/02-issues-inicial-top-issues.png)

*Figura 2 — Pestaña Issues: **237 issues en total**, 235 priorizados, con un
esfuerzo estimado de **3 días y 6 horas**. Encabezan la lista los tres
hallazgos corregidos en la iteración 1, todos en estado `Open`: el Blocker de
`be/ver_bd.py` (L4), el High de `.github/workflows/sonarcloud.yml` (L45) y el
High de `be/Dockerfile` (L51).*

![Listado de issues filtrado por cualidad de software Security, mostrando 29 issues](img/03-issues-inicial-seguridad.png)

*Figura 3 — Filtro por cualidad **Security**: **29 issues** con un esfuerzo de
**1 día y 4 horas**. Se aprecian los mismos tres hallazgos abiertos y, a
continuación, el *Client-Side Request Forgery* de `fe/src/api/alerts.ts`.*

| Métrica | Valor | Calificación |
|---|---|---|
| **Quality Gate** | **Failed** | — |
| Seguridad | 29 issues abiertos | **E** |
| Fiabilidad | 208 issues abiertos | **C** |
| Mantenibilidad | 39 issues abiertos | **A** |
| Líneas de código (ncloc) | 32 373 | — |
| Cobertura de pruebas | 0.0 % sobre 9 900 líneas | — |
| Código duplicado | 2.9 % sobre 42 000 líneas | — |
| Security Hotspots | 0 | — |

> Los conteos de Seguridad, Fiabilidad y Mantenibilidad corresponden a la
> taxonomía de *software qualities* de SonarCloud. Un mismo issue puede
> impactar más de una cualidad, por lo que su suma no equivale al total.

**Clasificación clásica — 237 issues abiertos:**

| Tipo | Cantidad | Severidades |
|---|---:|---|
| Code Smells | 170 | 1 Critical, 145 Major, 24 Minor |
| Bugs | 38 | 38 Major |
| Vulnerabilidades | 29 | 1 Blocker, 1 Critical, 21 Major, 6 Minor |

**Esfuerzo de remediación estimado por SonarCloud:**

| Concepto | Minutos |
|---|---:|
| Deuda técnica (`sqale_index`, solo Code Smells) | 898 |
| Esfuerzo de remediación de seguridad | 720 |
| Esfuerzo de remediación de fiabilidad | 220 |
| **Total** | **1 838 min ≈ 30,6 horas** |

> SonarCloud reserva el término *deuda técnica* para el esfuerzo de los Code
> Smells únicamente; bugs y vulnerabilidades se contabilizan en métricas
> aparte. El informe distingue las tres para no inflar la cifra.

**Distribución por área del monorepo:**

| Área | Bugs | Vulnerabilidades | Code Smells |
|---|---:|---:|---:|
| `fe/src` | 38 | 7 | 165 |
| `be/seed_test_data.py` | 0 | 10 | 1 |
| `be/Dockerfile` | 0 | 6 | 0 |
| `mobile/src` | 0 | 0 | 4 |
| `qa_e2e/config.py` | 0 | 2 | 0 |
| `fe/Dockerfile` | 0 | 2 | 0 |
| `db/Dockerfile` | 0 | 1 | 0 |
| `be/ver_bd.py` | 0 | 1 | 0 |
| `.github/workflows` | 0 | 1 | 0 |

---

## 3. Matriz de hallazgos seleccionados

Selección de **15 hallazgos** que supera el mínimo exigido por la guía
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
| B1 | **MAJOR** | `typescript:S3923` | `fe/src/components/bovines/BovineList.tsx` | 530, 542, 555 | `connector: prev.length > 0 ? "AND" : "AND"` — el operador ternario devuelve el mismo valor en ambas ramas, por lo que la condición es código muerto: se evalúa `prev.length` en cada llamada sin que el resultado pueda cambiar. Repetido en los tres puntos donde se añade una condición al filtro avanzado. | 15 min c/u |
| B2 | **MAJOR** | `typescript:S9383` | `fe/src/components/paddocks/LandMap.tsx` y otros | 81 y 34 más | Promesas sin `await`, sin `.catch()` ni marcado con `void`. Un rechazo en cualquiera de estas 35 llamadas produce un *unhandled rejection* silencioso: la operación falla sin que el usuario reciba aviso. | 5 min c/u |

### 3.3 Code Smells

| # | Severidad | Regla | Archivo | Línea | Descripción | Esfuerzo |
|---|---|---|---|---|---|---|
| C1 | **MAJOR** | `typescript:S8786` | `fe/src/pages/RegisterPage.tsx`, `LoginPage.tsx`, `ForgotPasswordPage.tsx`, `mobile/src/screens/auth/*` | 68, 104, 178, 37, 62, 25, 29, 45 | Expresión regular de validación de correo `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` con rendimiento superlineal por *backtracking*. Repetida en 8 lugares: además de ser ReDoS, es duplicación de una regla de negocio. | 20 min c/u |
| C2 | **MAJOR** | `typescript:S6853` | `fe/src/components/layout/AppLayout.tsx` y otros | 304, 309, 314 y 119 más | **122 etiquetas `<label>` sin asociar a su control.** Es el hallazgo más numeroso del proyecto —el 52 % de todos los issues abiertos— y afecta la accesibilidad de todos los formularios. | 5 min c/u |
| C3 | **MINOR** | `typescript:S7773` | `fe/src/components/layout/AppLayout.tsx` y otros | 332 y 23 más | 24 usos de las funciones globales `parseFloat`, `parseInt` e `isNaN` en lugar de `Number.parseFloat`, `Number.parseInt` y `Number.isNaN`. | 2 min c/u |
| C4 | **MAJOR** | `typescript:S6848` | `fe/src/components/bovines/AdvancedFiltersPanel.tsx`, `BovineList.tsx` | 79, 852, 895 y 7 más | 10 elementos no interactivos (`<div>`, `<span>`) usados como botones, sin `role` ni soporte de teclado. | 5 min c/u |
| C5 | — | *(hallazgo de configuración, no reportado por Sonar)* | `fe/coverage/` | — | La carpeta de reportes de cobertura está versionada en Git (12 archivos generados). Quedó fuera del alcance del análisis gracias a las exclusiones configuradas, pero no debería estar en el repositorio. | — |

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
| **Security Rating** | **E** | **C** | **▲ 2 niveles** |
| Vulnerabilidades abiertas | 29 | 27 | −2 |
| Esfuerzo de remediación de seguridad | 720 min | 660 min | −60 min |
| Bugs | 38 | 38 | = |
| Code Smells | 170 | 170 | = |
| Deuda técnica (`sqale_index`) | 898 min | 898 min | = |
| Reliability Rating | C | C | = |
| Quality Gate | Failed | Failed | sin cambio |

**Lectura honesta de estas cifras.** El resultado relevante de esta iteración no
es el volumen, sino la **gravedad**: se cerraron el único Blocker y el único
Critical del proyecto. La calificación de seguridad la determina siempre la
vulnerabilidad más grave abierta, de modo que al desaparecer esas dos el peor
caso restante pasa a ser Major y el rating sube de **E a C**. Dos issues menos
sobre 29 es un 7 % del conteo, pero significa que ya no hay credenciales
válidas ni riesgo de filtración de secretos en la imagen de producción.

Las tres vulnerabilidades corregidas son `CLOSED / FIXED` en SonarCloud,
verificadas una por una vía API.

El conteo de vulnerabilidades baja en 2 y no en 3 porque V8 estaba en el
workflow que creamos nosotros en el commit anterior: no formaba parte de la
línea base del proyecto original.

Bugs, Code Smells y deuda técnica no se mueven, y es lo esperado: ninguna de las
tres correcciones tocó esas categorías. Se corregirán en las iteraciones
siguientes.

El Quality Gate sigue en *Failed* porque su condición es *Security Rating on New
Code > 1*, es decir, exige calificación **A** sobre el código nuevo. Alcanzarla
requiere cerrar las vulnerabilidades Major restantes.

---

## 7. Refactorización: segunda iteración (B1, C3)

Commit `0149226` — análisis #5 sobre `main`.
Ambas reglas quedaron en **0 issues abiertos**.

### B1 — Condición que devuelve siempre lo mismo (`typescript:S3923`, MAJOR ×3)

**Antes** — `fe/src/components/bovines/BovineList.tsx:530, 542, 555`

```ts
next = next.concat([{
  id: Math.random().toString(36).slice(2),
  connector: next.length > 0 ? "AND" : "AND",
  field,
  op: defaultOpForType(f?.type ?? "text"),
  value,
}]);
```

**Después**

```ts
next = next.concat([{
  id: Math.random().toString(36).slice(2),
  connector: "AND",
  field,
  op: defaultOpForType(f?.type ?? "text"),
  value,
}]);
```

*Criterio aplicado:* antes de tocar el código se verificó qué hacía realmente
el campo `connector`. En `bovineColumns.ts`, la función `matchesConditions()`
**ignora el conector de la primera condición** (`if (!started) result = r`), y
en `AdvancedFiltersPanel.tsx` el selector de la primera fila aparece
deshabilitado y fijo en `"AND"` (`disabled={idx === 0}`). Es decir, `"AND"` es
el valor por defecto correcto para toda condición nueva, y el usuario puede
cambiar el de las siguientes a `"OR"` desde la interfaz.

El defecto, por tanto, **no era una pérdida de funcionalidad**: era una
condición muerta que se evaluaba en cada llamada sin que su resultado pudiera
cambiar nunca. La corrección elimina la evaluación inútil y deja explícita la
intención. El comportamiento observable del filtro es idéntico.

### C3 — Funciones numéricas globales (`typescript:S7773`, MINOR ×24)

**Antes** — 13 archivos de `fe/src`

```ts
onChange={(e) => set("area", parseFloat(e.target.value) || 0)}
onChange={(e) => set("max_capacity", parseInt(e.target.value) || 1)}
if (isNaN(weightKg) || weightKg <= 0) { ... }
```

**Después**

```ts
onChange={(e) => set("area", Number.parseFloat(e.target.value) || 0)}
onChange={(e) => set("max_capacity", Number.parseInt(e.target.value) || 1)}
if (Number.isNaN(weightKg) || weightKg <= 0) { ... }
```

*Criterio aplicado:* `Number.parseFloat` y `Number.parseInt` son exactamente las
mismas funciones que las globales, pero no dependen del objeto global, lo que
evita que un identificador local las sombree por accidente y deja explícita la
intención numérica. `Number.isNaN` sí difiere de la global `isNaN`: esta última
convierte su argumento antes de comparar, de modo que `isNaN("texto")` es
`true` mientras que `Number.isNaN("texto")` es `false`. En el único punto
afectado (`CalfList.tsx:185`) el argumento ya era el resultado de
`Number.parseFloat`, es decir un `number`, por lo que ambas se comportan igual
y el cambio es seguro.

### Verificación ejecutada

Sobre la etapa *builder* de `fe/Dockerfile`, que instala las dependencias con
el lockfile exacto:

| Comprobación | Resultado |
|---|---|
| `pnpm build` (tsc + Vite) | correcto |
| `pnpm lint` (ESLint) | 7 problemas (4 errores, 3 avisos) |
| `pnpm test` (Vitest) | **43 pruebas, 43 pasan** |

Los 7 problemas de ESLint son **preexistentes**: se ejecutó el mismo linter
sobre `main` sin estos cambios y el resultado fue idéntico. Ninguno afecta a
los archivos modificados. Se dejan constar sin corregir porque pertenecen a
otras reglas (`react-hooks/set-state-in-effect`, `react-refresh/only-export-components`)
y no forman parte de los hallazgos de esta iteración.

### Impacto medido

| Métrica | Antes (`ab2b907`) | Después (`0149226`) | Variación |
|---|---:|---:|---|
| Bugs | 38 | **35** | **−3** |
| Code Smells | 170 | **146** | **−24** |
| Deuda técnica (`sqale_index`) | 898 min | **850 min** | −48 min |
| Vulnerabilidades | 27 | 27 | = |
| Security Rating | C | C | = |
| Reliability Rating | C | C | = |
| Quality Gate | Failed | Failed | sin cambio |

`typescript:S3923` y `typescript:S7773` quedan ambas en **0 issues abiertos**,
verificado vía API.

El *Reliability Rating* permanece en **C** porque la calificación la determina
el peor bug abierto y los 35 restantes siguen siendo de severidad Major, en su
mayoría promesas sin gestionar (`typescript:S9383`, hallazgo B2).

Con esta iteración se cumple el mínimo exigido por la guía: **2 Code Smells, 2
Bugs y 1 Vulnerabilidad** corregidos. El total acumulado es de 3
vulnerabilidades, 3 bugs y 24 code smells.

---

## 8. Estado

- [x] Integración de SonarCloud con GitHub Actions
- [x] Escaneo inicial y captura de la línea base
- [x] Matriz de hallazgos
- [x] Refactorización — iteración 1: V1, V2, V8 (3 vulnerabilidades)
- [x] Refactorización — iteración 2: B1 (3 bugs) y C3 (24 code smells)
- [x] **Mínimo exigido por la guía cumplido** (≥ 2 Code Smells, ≥ 2 Bugs, ≥ 1 Vulnerabilidad)
- [ ] Refactorización — iteración 3: V3, V4, V5 (seguridad del frontend)
- [ ] Refactorización — iteración 4: V6, V7, C1
- [ ] Corrección del bug B2 (35 promesas sin gestionar)
- [ ] Marcado de falsos positivos (`typescript:S2068`)
- [ ] Datos de identificación y reparto por integrante (sección 5)
- [ ] Captura del dashboard final y exportación a PDF
- [ ] Re-escaneo hasta Quality Gate *Passed*
