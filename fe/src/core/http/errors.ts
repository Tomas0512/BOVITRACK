/**
 * ¿Qué?     Extrae el mensaje de error que devolvió el backend.
 * ¿Para qué? Mostrarle al usuario el motivo real ("El nombre debe tener al
 *            menos 2 caracteres") en vez de un genérico "No se pudo guardar".
 * ¿Impacto?  El interceptor de `api/axios.ts` ya lee `detail` de la respuesta
 *            y rechaza con un `Error`, así que el mensaje viaja en
 *            `err.message`, NO en `err.response.data.detail`. Buscarlo en el
 *            sitio equivocado devuelve undefined y se pierde la explicación.
 */
/** Pydantic antepone "Value error, " a los mensajes de sus validadores. */
const limpiar = (msg: string): string => msg.replace(/(^|\.\s*)Value error,\s*/g, "$1").trim();

export function getApiErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof Error && err.message) return limpiar(err.message);

  // Respaldo por si alguna llamada no pasa por el interceptor.
  if (err && typeof err === "object") {
    const axiosErr = err as { response?: { data?: { detail?: unknown } } };
    const detail = axiosErr.response?.data?.detail;
    if (typeof detail === "string" && detail) return limpiar(detail);
    if (Array.isArray(detail)) {
      const msgs = (detail as { msg?: string }[]).map((d) => d.msg).filter(Boolean);
      if (msgs.length) return limpiar(msgs.join(". "));
    }
  }
  return fallback;
}
