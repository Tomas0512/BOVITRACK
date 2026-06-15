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

## [2026-06-15] Backend: Implement email sending (SMTP + Resend + Mailpit)

**Reason:** Password reset, email verification, and farm invitation emails were
stubbed out (console-only). Users never received emails.

- `be/app/config.py` — replaced `MAIL_SERVER`/`MAIL_PORT`/`MAIL_USERNAME`/`MAIL_PASSWORD`/`MAIL_FROM`/`MAIL_FROM_NAME` with `SMTP_HOST`/`SMTP_PORT`/`SMTP_USERNAME`/`SMTP_PASSWORD` + `RESEND_API_KEY`/`RESEND_FROM_EMAIL`/`RESEND_FROM_NAME`
- `be/app/utils/email.py` — rewrote 3 functions (password reset, email verification, farm invitation) with:
  - Priority 1: SMTP via stdlib `smtplib` (Mailpit in Docker dev)
  - Priority 2: Resend API via `resend` SDK
  - Priority 3: Fallback to console logging
  - HTML email templates with CTA button + direct link
- `be/pyproject.toml` — replaced `aiosmtplib` with `resend==2.25.0`
- `docker-compose.yml` — added `mailpit` service (ports 8025 Web UI + 1025 SMTP); added `SMTP_HOST=mailpit` and `SMTP_PORT=1025` to backend environment
- `be/.env.example` — added `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `RESEND_FROM_NAME`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`

## [2026-06-15] Frontend: Unify color palette with mobile app

**Reason:** Web and mobile had completely divergent color palettes. Matched web theme
to the mobile app's forest green (`#2D6A4F`) palette for brand consistency.

- `fe/src/index.css` — replaced `@theme` block with 18 colors matching mobile palette (primary, primary-dark, primary-light, secondary, secondary-light, background, surface, surface-alt, text-primary, text-secondary, text-muted, error, error-light, success, success-light, warning, warning-light, border, border-focus); removed cream/accent colors; changed body bg from `bg-surface` to `bg-background`
- `fe/src/components/layout/AppLayout.tsx` — `bg-cream` → `bg-background`
- `fe/src/components/layout/Footer.tsx` — `text-cream` → `text-white` / `text-white/70`
- `fe/src/pages/HomePage.tsx` — `via-cream/60 to-accent/30` → `via-background to-secondary-light/30`; `bg-cream/40` → `bg-surface-alt`; `text-cream/90` → `text-white/90`; `hover:bg-cream` → `hover:bg-surface-alt`
