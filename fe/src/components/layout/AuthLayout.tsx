/**
 * Archivo: components/layout/AuthLayout.tsx
 * Descripción: Layout para páginas de autenticación (registro, login, etc.).
 * ¿Para qué? Envolver las páginas de auth con Header + Footer + diseño centrado.
 */

import { Header } from "./Header";
import { Footer } from "./Footer";
import "./AuthLayout.css";

interface AuthLayoutProps {
  children: React.ReactNode;
  /** Texto del botón en el Header */
  headerActionLabel: string;
  /** Ruta del botón en el Header */
  headerActionTo: string;
}

export function AuthLayout({ children, headerActionLabel, headerActionTo }: AuthLayoutProps) {
  return (
    <div className="auth-layout">
      <Header actionLabel={headerActionLabel} actionTo={headerActionTo} />
      <main className="auth-layout__main">{children}</main>
      <Footer />
    </div>
  );
}
