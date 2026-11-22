/*
 * App.tsx
 * Componente raíz de BoviTrack. Define el enrutador principal.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import {
  AuthProvider,
  ForgotPasswordPage,
  LoginPage,
  ProtectedRoute,
  RegisterPage,
  RequireRole,
  ResetPasswordPage,
  VerifyEmailPage,
} from "@/features/identity";
import { ThemeProvider } from "@/shared/theme";
import { FarmProvider, CreateFarmPage } from "@/features/farms";
import AppLayout from "./layout/AppLayout";

import HomePage from "./pages/HomePage";
import DashboardPage from "./pages/DashboardPage";
import FarmDetailPage from "./pages/FarmDetailPage";
import BovineDetailPage from "./pages/BovineDetailPage";
import { EconomicDashboard } from "@/features/economics";
import { ReportsPage } from "@/features/reports";
import { AuditPage } from "@/features/audit";  // HU015: Auditoria del sistema
import { AlertasPage } from "@/features/notifications";  // HU014: Alertas y notificaciones
import TermsPage from "./pages/TermsPage";
import PrivacyPage from "./pages/PrivacyPage";
import { InvitedRegisterPage, ReactivationRequestsPage, RequestReactivationPage } from "@/features/team";

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
      <AuthProvider>
        <Routes>
          {/* Públicas */}
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/register/invitation" element={<InvitedRegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/request-reactivation" element={<RequestReactivationPage />} />

          {/* Protegidas */}
          <Route element={<ProtectedRoute><FarmProvider><AppLayout /></FarmProvider></ProtectedRoute>}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/farms/new" element={<CreateFarmPage />} />
            <Route path="/farms/:farmId" element={<FarmDetailPage />} />
            <Route path="/farms/:farmId/bovines/:bovineId" element={<BovineDetailPage />} />
            <Route path="/farms/:farmId/economics" element={<EconomicDashboard />} />
            <Route path="/farms/:farmId/reports" element={<ReportsPage />} />
            {/*
              HU014 - Alertas y notificaciones (Sprint 8 - Tomas)

              COMO: miembro de la finca
              QUIERO: una ruta para configurar mis preferencias de notificación
                      y ver el historial de alertas de la finca
              PARA:   que la finca no dependa de avisos externos y pueda saber
                      a tiempo qué tratamientos vencen o qué insumos faltan.
            */}
            <Route path="/farms/:farmId/alerts" element={<AlertasPage />} />
            {/*
              HU015 - Revision de auditorias del sistema (Sprint 8 - Camilo)

              COMO: Administrador del sistema
              QUIERO: una ruta propia para la auditoria, fuera del detalle de finca
              PARA:   poder revisar en una sola pantalla la actividad de todas
                      mis fincas y llegar directo con un enlace.
            */}
            <Route path="/audit" element={<RequireRole role="Administrador"><AuditPage /></RequireRole>} />
            {/*
              Moderación de reactivaciones de cuenta

              COMO: Administrador de una finca
              QUIERO: aprobar o rechazar las solicitudes de reactivación
              PARA:   que alguien de mi equipo recupere el acceso sin tocar la BD.
              (El backend limita la lista a personas de mis fincas.)
            */}
            <Route path="/admin/reactivations" element={<RequireRole role="Administrador"><ReactivationRequestsPage /></RequireRole>} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;

