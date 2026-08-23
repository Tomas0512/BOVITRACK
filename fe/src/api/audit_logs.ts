/**
 * Módulo: api/audit_logs.ts
 * HU015 - Revisión de auditorías del sistema (Sprint 8 - Camilo)
 *
 * COMO: Administrador del sistema
 * QUIERO: un cliente único que hable con los endpoints de auditoría
 * PARA:   que la página de auditoría no arme URLs ni maneje descargas a mano,
 *         y que cualquier cambio en el backend se ajuste en un solo archivo.
 *
 * ¿Qué?     Funciones tipadas contra /api/v1/admin/audit-logs.
 * ¿Impacto? El listado por finca (usado en FarmDetailPage desde el Sprint 1)
 *           se conserva sin cambios para no romper esa pantalla.
 */

import api from "./axios";

// ─── Tipos ────────────────────────────────────────────────────────────────────

/**
 * COMO: desarrollador del frontend
 * QUIERO: un tipo que refleje exactamente la respuesta del backend
 * PARA:   que TypeScript avise si el contrato cambia, en vez de fallar en
 *         tiempo de ejecución frente al usuario.
 */
export interface AuditLogEntry {
  id: string;
  user_id: string | null;
  action: string;
  entity: string;
  entity_id: string | null;
  details: string | null;
  created_at: string;
  user_email: string | null;
  user_full_name: string | null;
}

/** Registro de auditoría del endpoint administrativo (incluye datos de finca). */
export interface AuditLogRecord extends AuditLogEntry {
  farm_id: string | null;
  farm_name: string | null;
}

/** Página de resultados con la metadata necesaria para paginar en pantalla. */
export interface AuditLogPage {
  total: number;
  limit: number;
  offset: number;
  items: AuditLogRecord[];
}

/**
 * COMO: Administrador
 * QUIERO: combinar varios filtros en una misma búsqueda
 * PARA:   aislar el evento exacto que estoy investigando.
 *
 * Todos los campos son opcionales: sin filtros se traen los registros más
 * recientes de las fincas a las que el usuario tiene acceso.
 */
export interface AuditLogFilters {
  user_id?: string;
  farm_id?: string;
  action?: string;
  entity?: string;
  start_date?: string; // YYYY-MM-DD
  end_date?: string; // YYYY-MM-DD
  include_auth_events?: boolean;
  limit?: number;
  offset?: number;
}

/** Catálogo de valores existentes, para poblar los desplegables de filtro. */
export interface AuditCatalog {
  actions: string[];
  entities: string[];
}

// ─── Funciones ────────────────────────────────────────────────────────────────

/**
 * COMO: Administrador viendo el detalle de una finca
 * QUIERO: ver los últimos movimientos de esa finca
 * PARA:   revisar rápidamente qué cambió sin salir de la pantalla.
 *
 * Endpoint heredado del Sprint 1, usado por AuditLogList en FarmDetailPage.
 */
export async function listAuditLogs(farmId: string): Promise<AuditLogEntry[]> {
  const res = await api.get<AuditLogEntry[]>(`/farms/${farmId}/audit-logs`);
  return res.data;
}

/**
 * COMO: Administrador del sistema
 * QUIERO: consultar la auditoría aplicando filtros y paginación
 * PARA:   encontrar quién hizo qué y cuándo sin recorrer miles de registros.
 *
 * ¿Impacto? Axios omite automáticamente los parámetros `undefined`, por lo que
 *           solo se envían los filtros que el usuario realmente diligenció.
 */
export async function searchAuditLogs(
  filters: AuditLogFilters = {}
): Promise<AuditLogPage> {
  const res = await api.get<AuditLogPage>("/admin/audit-logs", {
    params: filters,
  });
  return res.data;
}

/**
 * COMO: Administrador usando los filtros
 * QUIERO: elegir la acción y la entidad de una lista desplegable
 * PARA:   no tener que adivinar nombres técnicos como 'create_bovine' ni
 *         arriesgarme a filtrar sin resultados por un error de escritura.
 */
export async function getAuditCatalog(): Promise<AuditCatalog> {
  const res = await api.get<AuditCatalog>("/admin/audit-logs/actions");
  return res.data;
}

/**
 * COMO: Administrador del sistema
 * QUIERO: descargar la auditoría filtrada en CSV o Excel
 * PARA:   conservar la evidencia fuera del sistema o adjuntarla a un informe.
 *
 * ¿Impacto? Se pide `responseType: "blob"` porque la respuesta es un archivo
 *           binario; sin esto axios lo interpretaría como texto y el Excel
 *           llegaría corrupto. El objeto URL temporal se libera al terminar
 *           para no dejar memoria retenida en el navegador.
 */
export async function downloadAuditLogs(
  format: "csv" | "excel",
  filters: AuditLogFilters = {}
): Promise<void> {
  const response = await api.get("/admin/audit-logs/export", {
    params: { ...filters, export: format },
    responseType: "blob",
  });

  const extension = format === "csv" ? "csv" : "xlsx";
  const stamp = new Date().toISOString().slice(0, 10);

  const link = document.createElement("a");
  link.href = window.URL.createObjectURL(new Blob([response.data]));
  link.download = `auditoria_${stamp}.${extension}`;
  link.click();
  window.URL.revokeObjectURL(link.href);
}
