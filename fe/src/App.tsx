/*
 * App.tsx
 * ¿Qué? Componente raíz de Bovitrack. Define el enrutador principal.
 * ¿Para qué? Centralizar el routing de la app. Cada página se añade aquí.
 * ¿Impacto? Sin este componente, React no sabe qué renderizar.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { RegisterPage } from "./pages/RegisterPage";
import { LoginPage } from "./pages/LoginPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Registro */}
        <Route path="/register" element={<RegisterPage />} />

        {/* Login */}
        <Route path="/login" element={<LoginPage />} />

        {/* Recuperar contraseña */}
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />

        {/* Restablecer contraseña (con token) */}
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* Redirige la raíz al registro por ahora */}
        <Route path="/" element={<Navigate to="/register" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
