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
