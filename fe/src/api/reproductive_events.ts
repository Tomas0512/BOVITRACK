/*
 * Archivo: api/reproductive_events.ts
 * What? Cliente HTTP para el módulo de eventos reproductivos.
 *       Define tipos Create/Response y funciones list, create, delete.
 * Why? El frontend necesita consumir el backend de eventos reproductivos
 *            (CRUD) desde los componentes de la interfaz.
 * Impact? Sin este archivo, el componente ReproductiveTimeline no puede
 *           listar ni registrar eventos reproductivos.
 */
import api from "./axios";

// What? Datos necesarios para crear un evento reproductivo.
// Why? Tipar el body de la petición POST al backend.
export interface ReproductiveEventCreate {
  bovine_id: string;
  event_type: string;
  event_date: string;
  result?: string | null;
  due_date?: string | null;
  bull_id?: string | null;
  calf_id?: string | null;
  observations?: string | null;
}

// What? Estructura de la respuesta del backend para un evento reproductivo.
// Why? Tipar la respuesta de todas las llamadas del API.
export interface ReproductiveEventResponse {
  id: string;
  farm_id: string;
  bovine_id: string;
  event_type: string;
  event_date: string;
  result: string | null;
  due_date: string | null;
  bull_id: string | null;
  calf_id: string | null;
  observations: string | null;
  registered_by: string;
  created_at: string;
}

// What? Obtener todos los eventos reproductivos de un bovino específico.
// Why? Listar en el timeline del bovino los eventos registrados.
// Impact? Si falla, el usuario no ve el historial reproductivo del animal.
export async function listReproductiveEvents(
  farmId: string,
  bovineId: string
): Promise<ReproductiveEventResponse[]> {
  const response = await api.get<ReproductiveEventResponse[]>(
    `/farms/${farmId}/reproductive-events`,
    { params: { bovine_id: bovineId } }
  );
  return response.data;
}

// What? Registrar un nuevo evento reproductivo en el backend.
// Why? El usuario necesita documentar servicios, partos, diagnósticos, etc.
// Impact? Sin esta función, no se pueden crear eventos desde el frontend.
export async function createReproductiveEvent(
  farmId: string,
  data: ReproductiveEventCreate
): Promise<ReproductiveEventResponse> {
  const response = await api.post<ReproductiveEventResponse>(
    `/farms/${farmId}/reproductive-events`,
    data
  );
  return response.data;
}

// What? Eliminar un evento reproductivo por su ID.
// Why? Permitir corregir registros erróneos.
// Impact? El evento se borra permanentemente del sistema.
export async function deleteReproductiveEvent(
  farmId: string,
  eventId: string
): Promise<void> {
  await api.delete(`/farms/${farmId}/reproductive-events/${eventId}`);
}
