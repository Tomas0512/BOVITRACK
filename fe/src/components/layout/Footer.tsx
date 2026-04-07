/**
 * Archivo: components/layout/Footer.tsx
 * Descripción: Footer principal de BoviTrack.
 * ¿Para qué? Mostrar información de contacto, derechos reservados y enlaces legales.
 */

import { Link } from "react-router-dom";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-primary px-8 py-4 text-cream">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4">
        <p className="text-xs leading-snug text-cream/80">
          &copy; {currentYear} BoviTrack. Todos los derechos reservados.
        </p>
        <p className="text-xs leading-snug text-cream/80">
          <a href="/contacto" className="text-cream/80 no-underline hover:text-white">Contáctanos</a>
          &nbsp;|&nbsp; +573158874910
        </p>
        <p className="text-xs leading-snug text-cream/80">
          <Link to="/terms" className="text-cream/80 no-underline hover:text-white">Términos y condiciones</Link>
          &nbsp;·&nbsp;
          <Link to="/privacy" className="text-cream/80 no-underline hover:text-white">Política de privacidad</Link>
        </p>
      </div>
    </footer>
  );
}

