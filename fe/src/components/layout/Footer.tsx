/**
 * Archivo: components/layout/Footer.tsx
 * Descripción: Footer principal de BoviTrack.
 * ¿Para qué? Mostrar información de contacto, derechos reservados y enlaces legales.
 */

import { Link } from "react-router-dom";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary px-8 py-2.5 text-cream">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4">
        <p className="text-xs leading-snug text-cream">
          &copy; {currentYear} BoviTrack. Todos los derechos reservados.
        </p>
        <p className="text-xs leading-snug text-cream">
          <a href="/contacto" className="text-cream no-underline hover:text-white">Contáctanos</a>
          &nbsp;|&nbsp; +57 300 123 4567
        </p>
        <p className="text-xs leading-snug text-cream">
          <Link to="/terms" className="text-cream no-underline hover:text-white">Términos y condiciones</Link>
          &nbsp;·&nbsp;
          <Link to="/privacy" className="text-cream no-underline hover:text-white">Política de privacidad</Link>
        </p>
      </div>
    </footer>
  );
}

