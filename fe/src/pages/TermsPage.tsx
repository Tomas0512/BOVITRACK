/*
 * Archivo: pages/TermsPage.tsx
 * What? Página estática de términos y condiciones de uso de BoviTrack.
 * Why? Cumplir con el requisito legal de la rúbrica y las leyes
 *            colombianas (Ley 527/1999, Ley 1480/2011, Ley 1581/2012).
 * Impact? Sin esta página, los enlaces del footer serían anclas vacías
 *           y la rúbrica sancionaría la ausencia de páginas legales.
 */

import { Header } from "../components/layout/Header";
import { Footer } from "../components/layout/Footer";

export default function TermsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 bg-surface-alt">
        <div className="mx-auto max-w-3xl px-4 py-12">
          <h1 className="mb-8 text-3xl font-bold text-emerald-800">
            Términos y Condiciones de Uso
          </h1>
          <p className="mb-4 text-sm text-text-secondary">
            Última actualización: marzo de 2026
          </p>

          <div className="space-y-6 text-text-secondary leading-relaxed">
            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">1. Aceptación de los términos</h2>
              <p>
                Al registrarse y utilizar la plataforma BoviTrack, el usuario acepta en su totalidad
                los presentes términos y condiciones. Si no está de acuerdo con alguno de ellos,
                deberá abstenerse de utilizar el servicio.
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">2. Descripción del servicio</h2>
              <p>
                BoviTrack es un sistema de gestión ganadera que permite registrar, monitorear y
                administrar fincas, bovinos, producción lechera, tratamientos sanitarios,
                inventario de alimentos, potreros y tareas operativas. El servicio se ofrece
                con fines educativos en el marco del SENA.
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">3. Registro y cuenta de usuario</h2>
              <p>
                Para acceder a las funcionalidades de BoviTrack, el usuario debe crear una cuenta
                proporcionando información veraz y actualizada. El usuario es responsable de
                mantener la confidencialidad de sus credenciales de acceso.
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">4. Uso adecuado</h2>
              <p>El usuario se compromete a:</p>
              <ul className="ml-6 mt-2 list-disc space-y-1">
                <li>No utilizar el sistema para fines ilegales o no autorizados.</li>
                <li>No intentar acceder a cuentas o datos de otros usuarios.</li>
                <li>No realizar ingeniería inversa ni intentar vulnerar la seguridad del sistema.</li>
                <li>Proporcionar información veraz sobre sus fincas y animales.</li>
              </ul>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">5. Propiedad intelectual</h2>
              <p>
                El código fuente, diseño, logotipos y contenido de BoviTrack son propiedad del
                equipo de desarrollo y están protegidos por las leyes de propiedad intelectual
                colombianas (Ley 23 de 1982 y Decisión Andina 351 de 1993).
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">6. Limitación de responsabilidad</h2>
              <p>
                BoviTrack se proporciona "tal cual" con fines educativos. No se garantiza la
                disponibilidad ininterrumpida del servicio ni la ausencia de errores. El equipo
                de desarrollo no será responsable por pérdidas derivadas del uso del sistema.
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">7. Modificaciones</h2>
              <p>
                Nos reservamos el derecho de modificar estos términos en cualquier momento.
                Los cambios serán efectivos desde su publicación en esta página. El uso
                continuado del servicio implica la aceptación de los términos actualizados.
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">8. Legislación aplicable</h2>
              <p>
                Estos términos se rigen por las leyes de la República de Colombia, incluyendo
                la Ley 527 de 1999 (comercio electrónico), la Ley 1480 de 2011 (Estatuto del
                Consumidor) y la Ley 1581 de 2012 (protección de datos personales).
              </p>
            </section>

            <section>
              <h2 className="mb-2 text-xl font-semibold text-text-primary">9. Contacto</h2>
              <p>
                Para consultas sobre estos términos, puede comunicarse al correo electrónico:
                <span className="font-medium text-emerald-700"> soporte@bovitrack.co</span>
              </p>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
