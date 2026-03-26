/*
 * Archivo: pages/TermsPage.tsx
 * ¿Qué? Página estática de términos y condiciones de uso de BoviTrack.
 * ¿Para qué? Cumplir con el requisito legal de la rúbrica y las leyes
 *            colombianas (Ley 527/1999, Ley 1480/2011, Ley 1581/2012).
 * ¿Impacto? Sin esta página, los enlaces del footer serían anclas vacías
 *           y la rúbrica sancionaría la ausencia de páginas legales.
 */

export default function TermsPage() {
  return (
    // ¿Qué? Contenedor principal con fondo claro y ancho máximo para legibilidad.
    // ¿Para qué? Las páginas legales deben tener buen contraste y tipografía legible.
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-12">
        {/* ¿Qué? Título principal de la página legal. */}
        {/* ¿Impacto? Un solo <h1> por página — buena práctica SEO y accesibilidad. */}
        <h1 className="mb-8 text-3xl font-bold text-emerald-800">
          Términos y Condiciones de Uso
        </h1>
        <p className="mb-4 text-sm text-gray-500">
          Última actualización: marzo de 2026
        </p>

        <div className="space-y-6 text-gray-700 leading-relaxed">
          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">1. Aceptación de los términos</h2>
            <p>
              Al registrarse y utilizar la plataforma BoviTrack, el usuario acepta en su totalidad
              los presentes términos y condiciones. Si no está de acuerdo con alguno de ellos,
              deberá abstenerse de utilizar el servicio.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">2. Descripción del servicio</h2>
            <p>
              BoviTrack es un sistema de gestión ganadera que permite registrar, monitorear y
              administrar fincas, bovinos, producción lechera, tratamientos sanitarios,
              inventario de alimentos, potreros y tareas operativas. El servicio se ofrece
              con fines educativos en el marco del SENA.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">3. Registro y cuenta de usuario</h2>
            <p>
              Para acceder a las funcionalidades de BoviTrack, el usuario debe crear una cuenta
              proporcionando información veraz y actualizada. El usuario es responsable de
              mantener la confidencialidad de sus credenciales de acceso.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">4. Uso adecuado</h2>
            <p>El usuario se compromete a:</p>
            <ul className="ml-6 mt-2 list-disc space-y-1">
              <li>No utilizar el sistema para fines ilegales o no autorizados.</li>
              <li>No intentar acceder a cuentas o datos de otros usuarios.</li>
              <li>No realizar ingeniería inversa ni intentar vulnerar la seguridad del sistema.</li>
              <li>Proporcionar información veraz sobre sus fincas y animales.</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">5. Propiedad intelectual</h2>
            <p>
              El código fuente, diseño, logotipos y contenido de BoviTrack son propiedad del
              equipo de desarrollo y están protegidos por las leyes de propiedad intelectual
              colombianas (Ley 23 de 1982 y Decisión Andina 351 de 1993).
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">6. Limitación de responsabilidad</h2>
            <p>
              BoviTrack se proporciona "tal cual" con fines educativos. No se garantiza la
              disponibilidad ininterrumpida del servicio ni la ausencia de errores. El equipo
              de desarrollo no será responsable por pérdidas derivadas del uso del sistema.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">7. Modificaciones</h2>
            <p>
              Nos reservamos el derecho de modificar estos términos en cualquier momento.
              Los cambios serán efectivos desde su publicación en esta página. El uso
              continuado del servicio implica la aceptación de los términos actualizados.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">8. Legislación aplicable</h2>
            <p>
              Estos términos se rigen por las leyes de la República de Colombia, incluyendo
              la Ley 527 de 1999 (comercio electrónico), la Ley 1480 de 2011 (Estatuto del
              Consumidor) y la Ley 1581 de 2012 (protección de datos personales).
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">9. Contacto</h2>
            <p>
              Para consultas sobre estos términos, puede comunicarse al correo electrónico:
              <span className="font-medium text-emerald-700"> soporte@bovitrack.co</span>
            </p>
          </section>
        </div>

        {/* ¿Qué? Footer de la página legal con crédito institucional. */}
        <div className="mt-10 border-t pt-6 text-center text-sm text-gray-400">
          Proyecto educativo — SENA · {new Date().getFullYear()}
        </div>
      </div>
    </div>
  );
}
