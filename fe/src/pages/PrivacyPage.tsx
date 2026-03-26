/*
 * Archivo: pages/PrivacyPage.tsx
 * ¿Qué? Página estática de política de privacidad y tratamiento de datos.
 * ¿Para qué? Cumplir con la Ley 1581 de 2012 (Habeas Data) y el
 *            Decreto 1377 de 2013 que reglamenta el tratamiento de datos
 *            personales en Colombia.
 * ¿Impacto? Sin esta página, el sistema no cumpliría con la normatividad
 *           colombiana sobre protección de datos personales.
 */

export default function PrivacyPage() {
  return (
    // ¿Qué? Contenedor con fondo claro y ancho máximo para legibilidad.
    // ¿Para qué? Las páginas legales deben ser fáciles de leer.
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-12">
        {/* ¿Qué? Título principal — un solo <h1> por página (SEO + accesibilidad). */}
        <h1 className="mb-8 text-3xl font-bold text-emerald-800">
          Política de Privacidad y Tratamiento de Datos Personales
        </h1>
        <p className="mb-4 text-sm text-gray-500">
          Última actualización: marzo de 2026
        </p>

        <div className="space-y-6 text-gray-700 leading-relaxed">
          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">1. Responsable del tratamiento</h2>
            <p>
              BoviTrack, proyecto educativo desarrollado en el marco del Servicio Nacional de
              Aprendizaje (SENA), es responsable del tratamiento de los datos personales
              recopilados a través de esta plataforma.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">2. Datos que recopilamos</h2>
            <p>Recopilamos los siguientes datos personales:</p>
            <ul className="ml-6 mt-2 list-disc space-y-1">
              <li><strong>Datos de identificación:</strong> nombre completo, número de documento.</li>
              <li><strong>Datos de contacto:</strong> dirección de correo electrónico.</li>
              <li><strong>Datos de acceso:</strong> contraseña (almacenada de forma cifrada con bcrypt).</li>
              <li><strong>Datos operativos:</strong> información sobre fincas, bovinos, producción y tareas.</li>
              <li><strong>Datos de auditoría:</strong> fechas de registro, acciones realizadas en el sistema.</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">3. Finalidad del tratamiento</h2>
            <p>Los datos personales son utilizados para:</p>
            <ul className="ml-6 mt-2 list-disc space-y-1">
              <li>Gestionar la cuenta del usuario y autenticar su identidad.</li>
              <li>Proveer las funcionalidades del sistema de gestión ganadera.</li>
              <li>Enviar comunicaciones relacionadas con el servicio (verificación de cuenta, recuperación de contraseña).</li>
              <li>Generar reportes y estadísticas de la actividad ganadera del usuario.</li>
              <li>Cumplir con obligaciones legales y normativas aplicables.</li>
            </ul>
          </section>

          {/* ¿Qué? Sección de derechos del titular según Ley 1581/2012.
              ¿Para qué? Informar al usuario sobre sus derechos ARCO.
              ¿Impacto? Obligatorio por ley — la SIC puede sancionar si no se informa. */}
          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">4. Derechos del titular</h2>
            <p>
              De conformidad con la Ley 1581 de 2012, el titular de los datos tiene derecho a:
            </p>
            <ul className="ml-6 mt-2 list-disc space-y-1">
              <li><strong>Conocer:</strong> acceder a sus datos personales almacenados.</li>
              <li><strong>Actualizar:</strong> rectificar datos inexactos o incompletos.</li>
              <li><strong>Eliminar:</strong> solicitar la supresión de sus datos cuando no exista obligación legal de conservarlos.</li>
              <li><strong>Revocar:</strong> revocar la autorización otorgada para el tratamiento.</li>
              <li><strong>Presentar quejas:</strong> ante la Superintendencia de Industria y Comercio (SIC).</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">5. Medidas de seguridad</h2>
            <p>Implementamos las siguientes medidas para proteger los datos:</p>
            <ul className="ml-6 mt-2 list-disc space-y-1">
              <li>Cifrado de contraseñas con bcrypt.</li>
              <li>Autenticación mediante tokens JWT con expiración.</li>
              <li>Rate limiting para prevenir ataques de fuerza bruta.</li>
              <li>Cabeceras de seguridad HTTP (X-Content-Type-Options, X-Frame-Options, etc.).</li>
              <li>Auditoría de acciones críticas con registro de fecha y hora.</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">6. Transferencia de datos</h2>
            <p>
              Los datos personales no serán transferidos a terceros sin el consentimiento
              previo del titular, salvo cuando exista una obligación legal o judicial que así
              lo requiera.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">7. Conservación de datos</h2>
            <p>
              Los datos personales se conservarán mientras la cuenta del usuario esté activa
              y durante el tiempo necesario para cumplir con las finalidades descritas.
              Al eliminar la cuenta, los datos serán desactivados (soft delete) y podrán
              ser eliminados definitivamente tras un período de 30 días.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">8. Modificaciones</h2>
            <p>
              Esta política puede ser actualizada en cualquier momento. Los cambios serán
              comunicados a través de la plataforma. La fecha de última actualización se
              indica al inicio de este documento.
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">9. Contacto</h2>
            <p>
              Para ejercer sus derechos o realizar consultas sobre el tratamiento de datos,
              puede comunicarse al correo electrónico:
              <span className="font-medium text-emerald-700"> soporte@bovitrack.co</span>
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-xl font-semibold text-gray-800">10. Marco normativo</h2>
            <p>
              Esta política se rige por la normatividad colombiana vigente, en particular:
            </p>
            <ul className="ml-6 mt-2 list-disc space-y-1">
              <li>Ley 1581 de 2012 — Régimen General de Protección de Datos Personales.</li>
              <li>Decreto 1377 de 2013 — Reglamentario de la Ley 1581 de 2012.</li>
              <li>Ley 527 de 1999 — Acceso y uso de mensajes de datos y comercio electrónico.</li>
            </ul>
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
