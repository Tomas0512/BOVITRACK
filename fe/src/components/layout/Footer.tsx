/**
 * Archivo: components/layout/Footer.tsx
 * Descripción: Footer principal de BoviTrack.
 * ¿Para qué? Mostrar información de contacto, derechos reservados y enlaces legales.
 */

import "./Footer.css";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer__container">
        <p className="footer__text">
          &copy; {currentYear} BoviTrack. Todos los derechos reservados.
        </p>
        <p className="footer__link">
          <a href="/contacto">Contáctanos</a> &nbsp;|&nbsp; +57 300 123 4567
        </p>
        <p className="footer__link">
          Términos y condiciones &nbsp;·&nbsp; Política de privacidad
        </p>
      </div>
    </footer>
  );
}
