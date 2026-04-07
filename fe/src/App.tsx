/*
 * App.tsx
 * Componente raíz de BoviTrack. Define el enrutador principal.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./components/layout/AppLayout";

import HomePage from "./pages/HomePage";
import { RegisterPage } from "./pages/RegisterPage";
import { LoginPage } from "./pages/LoginPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import DashboardPage from "./pages/DashboardPage";
import CreateFarmPage from "./pages/CreateFarmPage";
import FarmDetailPage from "./pages/FarmDetailPage";
import BovineDetailPage from "./pages/BovineDetailPage";
import TermsPage from "./pages/TermsPage";
import PrivacyPage from "./pages/PrivacyPage";
import { InvitedRegisterPage } from "./pages/InvitedRegisterPage";
import RequestReactivationPage from "./pages/RequestReactivationPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Públicas */}
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/register/invitation" element={<InvitedRegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/request-reactivation" element={<RequestReactivationPage />} />

          {/* Protegidas */}
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/farms/new" element={<CreateFarmPage />} />
            <Route path="/farms/:farmId" element={<FarmDetailPage />} />
            <Route path="/farms/:farmId/bovines/:bovineId" element={<BovineDetailPage />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;

