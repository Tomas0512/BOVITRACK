/**
 * Archivo: components/layout/Header.tsx
 * Descripción: Header principal de BoviTrack.
 * ¿Para qué? Mostrar el logo a la izquierda y un botón de acción a la derecha.
 */

import { Link } from "react-router-dom";
import "./Header.css";

interface HeaderProps {
  /** Texto del botón de acción (ej: "Iniciar sesión", "Registrarse") */
  actionLabel: string;
  /** Ruta a la que navega el botón de acción */
  actionTo: string;
}

export function Header({ actionLabel, actionTo }: HeaderProps) {
  return (
    <header className="header">
      <div className="header__container">
        <Link to="/" className="header__logo">
          <img src="/Logo_BoviTrack.png" alt="BoviTrack" className="header__logo-img" />
        </Link>

        <Link to={actionTo} className="header__action-btn">
          {actionLabel}
        </Link>
      </div>
    </header>
  );
}
