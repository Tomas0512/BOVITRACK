# Informe de Análisis Estático de Código — BoviTrack

## Evidencia individual — Camilo

**Guía de Aprendizaje N.º 08 — Análisis Estático del Código y Calidad de Software**

| | |
|---|---|
| Programa de formación | Análisis y Desarrollo de Software (ADSO) |
| Ficha | 228118 |
| Competencia | Construcción de una solución informática para el control de procesos organizacionales |
| Actividad | AP04 — Construir e integrar módulos de software según requerimientos |
| Aprendiz | **Camilo** |
| Instructor | Cristian González |
| Fecha | 25 de noviembre de 2026 |

| Dato técnico | Valor |
|---|---|
| Proyecto | BOVITRACK |
| Repositorio | https://github.com/Tomas0512/BOVITRACK |
| Herramienta | SonarQube Cloud (SonarCloud) |
| Project key | `BOVITRACK_TOMAS1594` |
| Organización | `tomas0512` |
| Dashboard | https://sonarcloud.io/summary/overall/?id=BOVITRACK_TOMAS1594 |
| Método de análisis | CI-based (GitHub Actions) |

---

## 1. Aporte individual

Además de las tres vulnerabilidades asignadas, me correspondió **montar la
integración de SonarCloud** con GitHub Actions para todo el equipo y corregir
los bugs y code smells que exige el mínimo del taller.

| Aporte | Detalle |
|---|---|
| Integración | `sonar-project.properties` y `.github/workflows/sonarcloud.yml` |
| Vulnerabilidades | **V1** (Blocker), **V2** (Critical), **V8** (Major) |
| Bugs | **B1** — 3 issues `typescript:S3923` |
| Code Smells | **C3** — 24 issues `typescript:S7773` |

---

## 2. Integración de la herramienta

El análisis se automatizó para que cada `push` a `main` y cada Pull Request
disparen una inspección completa sin intervención manual.

**`sonar-project.properties`**

```properties
sonar.projectKey=BOVITRACK_TOMAS1594
sonar.organization=tomas0512
sonar.projectName=BOVITRACK

sonar.sources=be/app,fe/src,mobile/src,db
sonar.tests=be/tests
sonar.test.inclusions=**/*.test.ts,**/*.test.tsx
sonar.exclusions=**/node_modules/**,**/dist/**,**/build/**,**/coverage/**,**/__pycache__/**,**/.venv/**,**/assets/**,**/*.min.js,**/*.lock

sonar.python.version=3.12
sonar.sourceEncoding=UTF-8
```

**`.github/workflows/sonarcloud.yml`** (fragmento)

```yaml
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: SonarCloud Scan
        uses: SonarSource/sonarqube-scan-action@2f77a1ec69fb1d595b06f35ab27e97605bdef703 # v5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**Tres decisiones técnicas que no venían en el material de apoyo:**

1. Se usó `sonarqube-scan-action@v5` en lugar de `sonarcloud-github-action@master`,
   porque este último está **deprecado** por SonarSource.
2. Hubo que **desactivar el *Automatic Analysis*** en SonarCloud. Los dos
   métodos son mutuamente excluyentes: con el automático activo, el pipeline
   falla con *"You are running CI analysis while Automatic Analysis is enabled"*.
3. Las pruebas se declaran con `sonar.tests` para que sus reglas no se mezclen
   con las del código de producción ni inflen la deuda técnica.

---

## 3. Escaneo inicial: línea base

Análisis del commit `8305de9`, 25/11/2026 02:06 UTC. Estado **antes** de
cualquier refactorización.

![Dashboard inicial de SonarCloud con el Quality Gate en estado Failed](img/01-dashboard-inicial-quality-gate.png)

*Figura 1 — Quality Gate **Failed** sobre el commit `8305de96`. La condición
incumplida es Security Rating sobre código nuevo: obtenida **C**, requerida **A**.*

![Listado de issues ordenado por prioridad](img/02-issues-inicial-top-issues.png)

*Figura 2 — **237 issues**, esfuerzo estimado **3 días y 6 horas**. Encabezan la
lista mis tres hallazgos, los tres en estado `Open`.*

![Listado de issues filtrado por cualidad Security](img/03-issues-inicial-seguridad.png)

*Figura 3 — Filtro **Security**: **29 issues**, esfuerzo **1 día y 4 horas**.*

| Métrica | Valor | Calificación |
|---|---|---|
| Quality Gate | **Failed** | — |
| Seguridad | 29 issues | **E** |
| Fiabilidad | 208 issues | **C** |
| Mantenibilidad | 39 issues | **A** |
| Líneas de código | 32 373 | — |
| Cobertura | 0.0 % | — |
| Duplicación | 2.9 % sobre 42 000 líneas | — |

| Tipo | Cantidad | Severidades |
|---|---:|---|
| Code Smells | 170 | 1 Critical, 145 Major, 24 Minor |
| Bugs | 38 | 38 Major |
| Vulnerabilidades | 29 | 1 Blocker, 1 Critical, 21 Major, 6 Minor |

---

## 4. Matriz de mis hallazgos

| # | Tipo | Severidad | Regla | Archivo | Línea | Descripción | Esfuerzo |
|---|---|---|---|---|---|---|---|
| V1 | Vulnerabilidad | **BLOCKER** | `secrets:S6698` | `be/ver_bd.py` | 4 | Cadena de conexión con usuario y contraseña de PostgreSQL escritos en el código. Cualquiera que clone el repositorio obtiene credenciales válidas. | 30 min |
| V2 | Vulnerabilidad | **CRITICAL** | `docker:S6470` | `be/Dockerfile` | 51 | `COPY . .` copia el contexto completo a la imagen publicada, incluidos `.env`, claves, `.git`, scripts de semilla y la suite de tests. | 20 min |
| V8 | Vulnerabilidad | **MAJOR** | `githubactions:S7637` | `.github/workflows/sonarcloud.yml` | 45 | La acción se referencia por etiqueta móvil en vez de por SHA completo. | 30 min |
| B1 | Bug | **MAJOR** ×3 | `typescript:S3923` | `fe/src/components/bovines/BovineList.tsx` | 530, 542, 555 | Operador ternario que devuelve el mismo valor en ambas ramas: condición muerta. | 15 min c/u |
| C3 | Code Smell | **MINOR** ×24 | `typescript:S7773` | 13 archivos de `fe/src` | varias | Funciones numéricas globales en lugar de las del objeto `Number`. | 2 min c/u |

---

## 5. Refactorización: antes y después

### V1 — Credenciales de PostgreSQL en el código

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

**Criterio.** No inventé un mecanismo nuevo de configuración. El repositorio ya
leía `DATABASE_URL` del entorno en `be/check_tables.py` y en `be/app/config.py`;
la corrección alinea este script con el patrón que el proyecto ya usaba.
Un hallazgo Blocker en un repositorio **público** es el de mayor urgencia: la
credencial queda en el historial de Git aunque después se borre el archivo.

### V2 — Copia recursiva del contexto de build

**Antes** — `be/Dockerfile:51`

```dockerfile
COPY --chown=appuser:appgroup . .
```

**Después**

```dockerfile
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini entrypoint.sh ./
```

**Criterio.** El proyecto ya tenía `be/.dockerignore`, pero una lista de
exclusión es frágil: basta con que alguien agregue un archivo y no la
actualice. Declarar explícitamente lo que entra invierte la lógica — lo que no
se nombra, no viaja.

> **Nota de honestidad técnica.** Mi primera versión de esta corrección
> mantenía `--chown=appuser:appgroup`, y eso **introdujo un hallazgo nuevo**
> (`docker:S6504`, Minor): si el usuario de ejecución es dueño del código,
> puede reescribir la aplicación. Lo detectó el propio SonarCloud en el
> análisis siguiente y lo corrigió Edwin en su iteración. Queda registrado
> porque ilustra para qué sirve el análisis continuo: una corrección también
> se audita.

### V8 — Acción de GitHub sin fijar

**Antes** — `.github/workflows/sonarcloud.yml:45`

```yaml
uses: SonarSource/sonarqube-scan-action@v5
```

**Después**

```yaml
uses: SonarSource/sonarqube-scan-action@2f77a1ec69fb1d595b06f35ab27e97605bdef703 # v5
```

**Criterio.** Una etiqueta de Git es móvil: quien controle ese repositorio
puede reapuntarla a otro commit. Como esta acción recibe `SONAR_TOKEN` y lee
todo el código fuente, un cambio así se ejecutaría con acceso al secreto. El
comentario `# v5` conserva la legibilidad.

### B1 — Condición que devuelve siempre lo mismo

**Antes** — `BovineList.tsx:530, 542, 555`

```ts
connector: next.length > 0 ? "AND" : "AND",
```

**Después**

```ts
connector: "AND",
```

**Criterio.** Antes de tocar el código verifiqué qué hacía realmente el campo
`connector`. En `bovineColumns.ts`, la función `matchesConditions()` **ignora el
conector de la primera condición** (`if (!started) result = r`), y en
`AdvancedFiltersPanel.tsx` el selector de la primera fila está deshabilitado y
fijo en `"AND"` (`disabled={idx === 0}`).

Es decir, `"AND"` es el valor por defecto correcto, y el usuario sí puede
cambiar el de las condiciones siguientes a `"OR"` desde la interfaz. **El
defecto no era una pérdida de funcionalidad**, sino una condición muerta que se
evaluaba sin que su resultado pudiera cambiar nunca. El comportamiento
observable del filtro es idéntico.

### C3 — Funciones numéricas globales

**Antes** (24 ocurrencias en 13 archivos)

```ts
onChange={(e) => set("area", parseFloat(e.target.value) || 0)}
if (isNaN(weightKg) || weightKg <= 0) { ... }
```

**Después**

```ts
onChange={(e) => set("area", Number.parseFloat(e.target.value) || 0)}
if (Number.isNaN(weightKg) || weightKg <= 0) { ... }
```

**Criterio.** `Number.parseFloat` y `Number.parseInt` son las mismas funciones
que las globales, pero no dependen del objeto global, lo que evita sombreado
accidental. `Number.isNaN` **sí difiere** de `isNaN`: la global convierte su
argumento antes de comparar, de modo que `isNaN("texto")` es `true` y
`Number.isNaN("texto")` es `false`. Verifiqué el único punto afectado
(`CalfList.tsx:185`): el argumento ya era el resultado de un `parseFloat`, es
decir un `number`, por lo que ambas se comportan igual y el cambio es seguro.

---

## 6. Verificación ejecutada

No basta con que SonarCloud cierre el hallazgo: hay que comprobar que la
funcionalidad no cambió.

**Backend** (imagen construida con `be/Dockerfile`)

```
docker build                      → correcto
ls -A /app                        → alembic  alembic.ini  app  entrypoint.sh  storage
python -c "import app.main"       → OK
ver_bd.py sin DATABASE_URL        → aborta con exit 1 y mensaje explícito
```

**Frontend** (etapa *builder* de `fe/Dockerfile`)

| Comprobación | Resultado |
|---|---|
| `pnpm build` (tsc + Vite) | correcto |
| `pnpm lint` (ESLint) | 7 problemas |
| `pnpm test` (Vitest) | **43 pruebas, 43 pasan** |

Los 7 problemas de ESLint son **preexistentes**: ejecuté el mismo linter sobre
`main` sin mis cambios y el resultado fue idéntico. Ninguno afecta a los
archivos que modifiqué.

---

## 7. Impacto medido

| Métrica | Antes (`8305de9`) | Después (`0149226`) | Variación |
|---|---:|---:|---|
| **Security Rating** | **E** | **C** | **▲ 2 niveles** |
| Vulnerabilidades | 29 | 27 | −2 |
| Bugs | 38 | **35** | **−3** |
| Code Smells | 170 | **146** | **−24** |
| Esfuerzo de remediación de seguridad | 720 min | 660 min | −60 min |
| Deuda técnica (`sqale_index`) | 898 min | **850 min** | −48 min |

**Lectura de estas cifras.** El resultado relevante de mi iteración de
seguridad no es el volumen sino la **gravedad**: se cerraron el único Blocker y
el único Critical del proyecto. La calificación de seguridad la determina
siempre la vulnerabilidad más grave abierta, así que al desaparecer esas dos el
peor caso restante pasó a ser Major y el rating subió de **E a C**.

El conteo baja en 2 y no en 3 porque V8 estaba en el workflow que yo mismo creé
en el commit anterior: no formaba parte de la línea base del proyecto.

Las tres vulnerabilidades, la regla `typescript:S3923` y la regla
`typescript:S7773` quedaron en estado `CLOSED / FIXED` con **0 issues
abiertos**, verificado vía API de SonarCloud.

---

## 8. Conclusiones

1. **El análisis estático encuentra lo que la revisión humana pasa por alto.**
   Las credenciales de `ver_bd.py` llevaban meses en un repositorio público y
   nadie las había notado.
2. **La herramienta también audita su propia integración.** El hallazgo V8
   estaba en el workflow que acababa de escribir.
3. **Una corrección puede introducir un hallazgo nuevo.** Mi primer arreglo de
   V2 generó `docker:S6504`. Sin análisis continuo, ese retroceso habría pasado
   inadvertido.
4. **Verificar es parte de corregir.** En B1 y en C3 la lectura del código
   evitó dos errores: habría descrito mal el defecto del filtro y habría
   cambiado `isNaN` por `Number.isNaN` sin comprobar que son distintas.

---

## 9. Trazabilidad

| Commit | Contenido |
|---|---|
| `8305de9` | Integración de SonarCloud (línea base) |
| `17f08c8` | Corrección de V1, V2 y V8 |
| `0149226` | Corrección de B1 y C3 |

Cada commit disparó su propio análisis, visible en el historial de *Activity*
del proyecto en SonarCloud y en la pestaña *Actions* del repositorio.
