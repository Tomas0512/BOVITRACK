# Extra Changes (outside sprint backlog)

This file tracks any changes made outside the Sprint Backlog to avoid
confusion during Sprint Reviews. Each entry includes date, description,
affected files, and reason.

---

## [2026-06-15] Backend: requirements.txt → pyproject.toml

**Reason:** Modernize dependency management to PEP 621 format.

- Removed `be/requirements.txt`
- Created `be/pyproject.toml` with pinned dependencies in PEP 621 format
- Updated `be/Dockerfile`: `pip install -r requirements.txt` → `pip install .`

## [2026-06-15] Backend: DANE departments & cities seed

**Reason:** Connect department/city selects in frontend to DANE official data.

- Expanded `be/seed_departments.py` with all 32 Colombian departments and ~1100 municipalities with DANE codes
- Added endpoint `GET /farms/departments/{department_id}/cities` in `be/app/routers/farms.py`
- Added `CityOption` schema in `be/app/schemas/farm.py`

## [2026-06-15] Frontend: Emojis → lucide-react icons

**Reason:** Replace emoji characters with SVG icons using the already-installed lucide-react library for consistent rendering across all browsers/devices.

Files modified (15):
- `fe/src/pages/DashboardPage.tsx` — 👋 removed, 🐄 → Tractor
- `fe/src/pages/ForgotPasswordPage.tsx` — 🔑 → Key, ✉️ → Mail
- `fe/src/pages/FarmDetailPage.tsx` — ⚠️ → AlertTriangle, 🐄 → Tractor
- `fe/src/pages/ResetPasswordPage.tsx` — ⚠️ → AlertTriangle, 🔒 → Lock, 🙈/👁️ → EyeOff/Eye
- `fe/src/pages/InvitedRegisterPage.tsx` — ⚠️ → AlertTriangle
- `fe/src/pages/BovineDetailPage.tsx` — ♂ → Mars, ♀ → Venus
- `fe/src/components/bovines/TreatmentList.tsx` — 💉 → Syringe
- `fe/src/components/bovines/FoodList.tsx` — 🌾 → Sprout
- `fe/src/components/bovines/SanitaryPlanList.tsx` — 🔴 → AlertTriangle
- `fe/src/components/layout/AlertBanner.tsx` — 🔴 → Circle, ⚠️ → AlertTriangle
- `fe/src/components/audit/AuditLogList.tsx` — 🗂️ → FileText
- `fe/src/components/paddocks/PaddockList.tsx` — ⚠ → AlertTriangle
- `fe/src/components/food/FoodList.tsx` — ⚠️ → AlertTriangle (×2)
- `fe/src/App.test.tsx` — Updated test to match new content

## [2026-06-15] Frontend: Form validation & modal conversion

**Reason:** Improve UX with proper form validation (required fields, maxLength, character counters, disabled submit until complete) and convert inline forms to modal with overlay.

Files modified (8):
- `fe/src/pages/CreateFarmPage.tsx` — maxLength + character counters + required validation
- `fe/src/pages/LoginPage.tsx` — maxLength + required validation
- `fe/src/pages/RegisterPage.tsx` — maxLength + required validation + isFormComplete
- `fe/src/components/bovines/BovineFormModal.tsx` — maxLength + isFormComplete
- `fe/src/components/bovines/ReproductiveTimeline.tsx` — Inline → Modal overlay + isFormComplete
- `fe/src/components/bovines/WeightHistory.tsx` — Inline → Modal overlay + isFormComplete
- `fe/src/components/food/FoodFormModal.tsx` — maxLength + isFormComplete
- `fe/src/components/paddocks/PaddockFormModal.tsx` — maxLength + isFormComplete
- `fe/src/components/land_plots/LandPlotFormModal.tsx` — maxLength + isFormComplete
- `fe/src/components/employees/AssignEmployeeModal.tsx` — maxLength + isFormComplete + required

## [2026-06-15] Frontend: Added lucide-react dependency

**Reason:** Required for emoji replacement (above).

- `fe/package.json` — added lucide-react
- `fe/pnpm-lock.yaml` — updated lockfile

## [2026-06-15] Backend: Seed permissions — added economica, reproductivo, sanitario

**Reason:** New modules (HU007 calves, HU010 economics) and existing modules
(reproductivo, sanitario) were missing from the permissions seed migration,
causing 403 errors on their endpoints.

- Added `economica`, `reproductivo`, `sanitario` to `MODULES` list
- Added corresponding CRUD permissions for all 4 roles (Administrador,
  Capataz, Veterinario, Empleado)

## [2026-06-15] Frontend: EconomicDashboard page

**Reason:** HU010.4 — Dashboard económico con filtros y gráficos.

- `fe/src/pages/EconomicDashboard.tsx` — Nueva página con Recharts
- `fe/src/App.tsx` — Ruta `/farms/:farmId/economics`
- `fe/src/pages/FarmDetailPage.tsx` — Botón de navegación "Económico"
- `fe/src/api/economics.ts` — Cliente API (creado previamente)

---

## [2026-06-17] Frontend: Dark/light mode toggle

**Reason:** Improve UX with theme toggle support across the entire app.

- Created `fe/src/context/ThemeContext.tsx` — ThemeProvider with dark/light detection
- Created `fe/src/components/layout/ThemeToggle.tsx` — Sun/Moon toggle button
- Updated `fe/src/index.css` — CSS variables with `@custom-variant dark` and `.dark` class selector
- Integrated into `Header.tsx` and all public pages

## [2026-06-17] Backend: SMTP + Resend email

**Reason:** Email sending for password reset, invitations and notifications.

- `be/app/config.py` — Added `SMTP_HOST`, `SMTP_PORT`, `SMTP_USE_TLS`, `RESEND_API_KEY` config
- `be/app/utils/email.py` — SMTP sending (Mailpit dev), Resend API fallback, console fallback
- `docker-compose.yml` — Added Mailpit service (SMTP + web UI on port 8025)

## [2026-06-17] Source: Spanish → English comments

**Reason:** Standardize all source code comments to English across the codebase.

- Converted all `¿Qué?`/`¿Para qué?`/`¿Impacto?` comments to `What?`/`Why?`/`Impact?`
- Affected: 19+ files across `fe/src`, `be/app`, `docker-compose.yml`, Dockerfiles, `.env.example`, `alembic/env.py`

## [2026-06-17] Frontend: Multi-step form pagination (9 forms)

**Reason:** All forms with >5 fields need step navigation (Next/Back) instead of scrolling.

- `fe/src/pages/RegisterPage.tsx` — 3 steps (Datos personales, Contacto y seguridad, Finalizar)
- `fe/src/pages/InvitedRegisterPage.tsx` — 3 steps
- `fe/src/pages/CreateFarmPage.tsx` — 3 steps + "Otro" city selector
- `fe/src/pages/FarmDetailPage.tsx` — 2 steps inline edit
- `fe/src/components/bovines/BovineFormModal.tsx` — 3 steps (14 campos)
- `fe/src/components/movements/MovementFormModal.tsx` — 3 steps (11 campos)
- `fe/src/components/food/FoodFormModal.tsx` — 3 steps (8 campos)
- `fe/src/components/paddocks/PaddockFormModal.tsx` — 2 steps (6-8 campos)
- `fe/src/components/land_plots/LandPlotFormModal.tsx` — 2 steps (6 campos)

## [2026-06-17] Backend: Admin deletion protection

**Reason:** Prevent the last active administrator from being removed or deactivated in a farm.

- `be/app/services/employee_service.py` — Added `_last_admin_check()` raises HTTP 400
- `fe/src/components/employees/EmployeeList.tsx` — Shows actual backend error message

## [2026-06-17] Frontend: Role-based dashboard

**Reason:** Non-admin users should not see "Crear Finca" button or empty-state prompts.

- `fe/src/pages/DashboardPage.tsx` — Conditionally hides admin-only UI elements

## [2026-06-17] Test data seed script

**Reason:** Create representative demo data for final presentation walkthrough.

- `be/seed_test_data.py` — Creates demo user (admin@bovitrack.com / Demo1234!), farm, land plots, paddocks, bovines, food, stock movements

## [2026-06-17] Mobile app improvements

**Reason:** Align mobile app color palette and theme with web version.

- `mobile/src/theme/colors.ts` — Updated to #59930a primary
- `mobile/src/theme/ThemeContext.tsx` — Dark/light mode with `useTheme()` hook
- Added inline validation to LoginScreen, RegisterScreen, ForgotPasswordScreen, ResetPasswordScreen
- Added theme toggle buttons to multiple screens

## [2026-06-17] Build fixes

**Reason:** Fix TypeScript compilation errors and Python import errors.

- `be/app/services/food_service.py` — Added `from decimal import Decimal`
- `be/app/services/report_service.py` — Removed invalid `DocumentTemplate` import
- `be/entrypoint.sh` — CRLF → LF conversion
- `be/Dockerfile` — Added `mkdir -p /app/storage/documents`
- `fe/src/pages/ReportsPage.tsx` — Removed unused `Download` import
- `fe/src/components/food/InventoryDashboard.tsx` — Fixed `listStockMovements` call signature
