/**
 * Archivo: components/layout/Header.tsx
 * Descripción: Header principal de BoviTrack.
 * ¿Para qué? Mostrar el logo a la izquierda y un botón de acción a la derecha.
 */

import { Link } from "react-router-dom";

interface HeaderProps {
  /** Texto del botón de acción (ej: "Iniciar sesión", "Registrarse") */
  actionLabel?: string;
  /** Ruta a la que navega el botón de acción */
  actionTo?: string;
}

export function Header({ actionLabel, actionTo }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 border-b-2 border-primary-light bg-white px-8">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between">
        <Link to="/" className="flex items-center hover:opacity-85">
          <img src="/Logo_BoviTrack.png" alt="BoviTrack" className="h-13 w-auto object-contain" />
        </Link>

        {actionLabel && actionTo ? (
          <Link
            to={actionTo}
            className="inline-flex items-center rounded-lg bg-primary px-6 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary-light"
          >
            {actionLabel}
          </Link>
        ) : (
          <nav className="flex items-center gap-3">
            <Link
              to="/login"
              className="inline-flex items-center rounded-lg border-2 border-primary px-5 py-2 text-sm font-semibold text-primary transition-colors hover:bg-primary hover:text-white"
            >
              Iniciar sesión
            </Link>
            <Link
              to="/register"
              className="inline-flex items-center rounded-lg bg-primary px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary-light"
            >
              Registrarse
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}
