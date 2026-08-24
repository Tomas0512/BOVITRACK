# Suite de Pruebas Selenium — Proyecto BoviTrack (SENA, Clase 8)

Automatización web con **Selenium WebDriver + Python** para el punto 3.4
de la guía de aprendizaje (Taller Práctico). Vive en la carpeta
`qa_e2e/` de la raíz del repositorio. Cubre **15 vistas** del frontend de
BoviTrack con **2 casos de uso por vista** (30 pruebas en total), usando
las estrategias de localización **ID, CSS Selector y XPath** exigidas en
la guía, y genera un **screenshot de evidencia por cada prueba**
(`_OK` si pasa, `_FAIL` si falla) en `qa_e2e/screenshots/`.

## Estructura de archivos

| Archivo | Vista cubierta | Ruta |
|---|---|---|
| `config.py` | Configuración centralizada (URL, credenciales, screenshots) | — |
| `base_test.py` | Clase base: setUp/tearDown del driver + login reutilizable + captura de evidencia | — |
| `test_01_home_page.py` | HomePage | `/` |
| `test_02_login_page.py` | LoginPage | `/login` |
| `test_03_register_page.py` | RegisterPage | `/register` |
| `test_04_invited_register_page.py` | InvitedRegisterPage | `/register/invitation` |
| `test_05_forgot_password_page.py` | ForgotPasswordPage | `/forgot-password` |
| `test_06_reset_password_page.py` | ResetPasswordPage | `/reset-password` |
| `test_07_terms_page.py` | TermsPage | `/terms` |
| `test_08_privacy_page.py` | PrivacyPage | `/privacy` |
| `test_09_request_reactivation_page.py` | RequestReactivationPage | `/request-reactivation` |
| `test_10_dashboard_page.py` | DashboardPage (protegida) | `/dashboard` |
| `test_11_create_farm_page.py` | CreateFarmPage (protegida) | `/farms/new` |
| `test_12_farm_detail_page.py` | FarmDetailPage (protegida) | `/farms/:farmId` |
| `test_13_bovine_detail_page.py` | BovineDetailPage (protegida) | `/farms/:farmId/bovines/:bovineId` |
| `test_14_economic_dashboard_page.py` | EconomicDashboard (protegida) | `/farms/:farmId/economics` |
| `test_15_reports_page.py` | ReportsPage (protegida) | `/farms/:farmId/reports` |

## 1. Requisitos previos

```bash
pip install -r requirements.txt
```

Selenium 4 detecta e instala automáticamente el ChromeDriver correcto
(Selenium Manager), como se explica en la sección 3.3 de la guía.

## 2. Levantar el proyecto BoviTrack localmente

Las pruebas necesitan el **frontend corriendo** (y el backend + base de
datos para las vistas protegidas). Desde la raíz del repo:

```bash
docker-compose up
```

Verifica en qué puerto queda expuesto el frontend (`fe`) y ajústalo en
`config.py` → `BASE_URL` si no es `http://localhost:5173`.

## 3. Preparar datos de prueba (¡IMPORTANTE!)

Antes de ejecutar la suite, edita `config.py`:

- `TEST_EMAIL` / `TEST_PASSWORD`: credenciales de un usuario **real y
  activo** en tu base de datos (créalo con `be/seed_test_data.py` o
  regístralo manualmente).
- `TEST_FARM_ID` / `TEST_BOVINE_ID`: **UUIDs reales** de una finca y un
  bovino que ya existan en tu base de datos (los IDs en BoviTrack son
  UUID, no números consecutivos — cópialos desde `be/seed_test_data.py`
  o consultando la tabla `farms`), para que las vistas de detalle
  (12, 13, 14 y 15) tengan datos que mostrar.

Sin estos datos, las pruebas de las vistas protegidas (10 a 15) fallarán
por no encontrar los recursos esperados — esto es esperado y normal en un
entorno sin datos semilla.

## 4. Ejecutar las pruebas

Un archivo individual (una vista):
```bash
python -m unittest test_02_login_page.py -v
```

Toda la suite (15 vistas / 30 casos):
```bash
python run_all_tests.py
```

## 5. Evidencia gráfica (screenshots)

Al finalizar **cada prueba**, `base_test.py` guarda automáticamente una
captura del estado final del navegador en `qa_e2e/screenshots/`:

```
test_login_valid_credentials_redirects_to_dashboard_OK_20260820_193000.png
test_login_invalid_credentials_shows_error_and_blocks_access_FAIL_20260820_193105.png
```

- `_OK` = prueba exitosa, `_FAIL` = prueba fallida (requisito de la guía:
  "Capturar una evidencia gráfica del resultado final de la prueba").
- Para capturar solo los fallos, pon `SCREENSHOT_ON_SUCCESS = False` en
  `config.py`.

## 6. Notas de diseño (por qué se hizo así)

- **`unittest`**: se usó el framework estándar de Python para poder
  escribir **clases de prueba** (`TestCase`), tal como pide el
  enunciado del punto 3.4 ("Deben crear clases de prueba automatizada").
- **`base_test.py`**: evita repetir 15 veces el mismo código de
  apertura/cierre de navegador, login y captura de evidencia
  (principio DRY).
- **Esperas explícitas (`WebDriverWait`)** en vez de `time.sleep()` fijo:
  hacen las pruebas más rápidas y más estables frente a los tiempos de
  respuesta variables del backend (FastAPI).
- **Localizadores**: se priorizó `By.ID` cuando el campo lo tenía
  disponible en el código fuente (formularios de Login, Registro, Crear
  finca, etc.), y se usó `By.XPATH` relativo por texto visible o
  `By.CSS_SELECTOR` cuando el elemento no exponía un `id` único (botones
  de acción, pestañas, enlaces del header) — siguiendo la Regla de Oro
  de la guía: **ID > CSS Selector > XPath relativo**, evitando siempre
  XPath absoluto.
- **`test_03_register_page.py` (wizard)**: el registro real es un
  formulario de 3 pasos; el botón `submit` solo existe en el último paso.
  Los casos navegan el wizard con el botón "Siguiente" y validan los
  errores visibles ("Obligatorio", "No coinciden") tal como los renderiza
  `RegisterPage.tsx`.
- Algunos locators basados en texto visible (ej. `contains(., 'Generar')`)
  dependen de los textos actuales de la interfaz; si el equipo de
  frontend cambia esos textos, se recomienda agregar atributos
  `data-testid` a los componentes para hacer las pruebas más robustas a
  futuro.
