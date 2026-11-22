// API pública de la feature identity: sesión, guards de rutas y pantallas de acceso.
// Otras partes de la app importan SOLO desde "@/features/identity".

// Sesión (proveedor, hook y aviso de inactividad)
export { AuthProvider } from "./session/AuthContext";
export { useAuth } from "./session/useAuth";
export { default as SessionGuard } from "./session/SessionGuard";

// Guards de rutas
export { default as ProtectedRoute } from "./components/ProtectedRoute";
export { default as RequireRole } from "./components/RequireRole";

// Pantallas públicas de acceso
export { LoginPage } from "./pages/LoginPage";
export { RegisterPage } from "./pages/RegisterPage";
export { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
export { ResetPasswordPage } from "./pages/ResetPasswordPage";
export { default as VerifyEmailPage } from "./pages/VerifyEmailPage";

// Cuenta propia (el menú de usuario del layout ofrece "eliminar cuenta")
export { deleteAccount } from "./api";
export type { UserResponse } from "./types";
