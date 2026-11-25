// ══════════════════════════════════════════════════════════════
// Validación de parámetros que se insertan en rutas de la API
//
// What?    Comprueba que un identificador tenga forma de UUID antes de
//          interpolarlo en la URL de una petición.
// ¿Para?   Codificar con encodeURIComponent impide romper la ruta, pero no
//          impide que un valor de origen no confiable decida a qué recurso
//          se apunta. Validar contra una lista blanca de formato sí: lo que
//          no es un UUID no llega a construir una URL.
// Impact?  La validación falla cerrada (lanza) en lugar de emitir una
//          petición a una ruta imprevista. Todos los identificadores de
//          BoviTrack son UUID en la base de datos (ver be/app/models/), así
//          que ningún valor legítimo es rechazado.
// ══════════════════════════════════════════════════════════════

// Patrón de longitud fija y sin alternativas: no tiene retroceso
// (backtracking), por lo que no es vulnerable a ReDoS.
const UUID_PATTERN =
  /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

/**
 * Devuelve el identificador listo para usarse como segmento de ruta.
 * Lanza si no tiene forma de UUID.
 */
export function uuidPathSegment(value: string, paramName: string): string {
  if (!UUID_PATTERN.test(value)) {
    throw new Error(
      `El parámetro "${paramName}" no es un identificador válido.`,
    );
  }
  return encodeURIComponent(value);
}

export { UUID_PATTERN };
