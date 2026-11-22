/**
 * Página: AuditPage.tsx
 * HU015 - Revisión de auditorías del sistema (Sprint 8 - Camilo, tarea 15.3)
 *
 * COMO: Administrador del sistema
 * QUIERO: una pantalla donde pueda filtrar la auditoría por finca, usuario,
 *         acción, entidad y rango de fechas, verla en una tabla y descargarla
 * PARA:   rastrear quién modificó qué información y cuándo, y conservar la
 *         evidencia sin depender de que alguien consulte la base de datos.
 *
 * ¿Impacto? Es la única pantalla del sistema que muestra la actividad de
 *           TODAS las fincas del usuario en un solo lugar. El backend acota
 *           los resultados a las fincas donde el usuario está registrado.
 */

import { useCallback, useEffect, useState } from "react";
import { Download, Filter, RotateCcw, ShieldCheck } from "lucide-react";
import {
  searchAuditLogs,
  getAuditCatalog,
  downloadAuditLogs,
  type AuditLogFilters,
  type AuditLogPage,
  type AuditCatalog,
} from "../api/audit_logs";
import { listFarms, type FarmResponse } from "../api/farms";

/** Registros por página mostrados en la tabla. */
const PAGE_SIZE = 50;

/**
 * COMO: Administrador
 * QUIERO: empezar siempre con la vista sin filtrar
 * PARA:   ver primero el panorama completo y luego ir acotando.
 */
const EMPTY_FILTERS: AuditLogFilters = {
  farm_id: undefined,
  action: undefined,
  entity: undefined,
  start_date: undefined,
  end_date: undefined,
  include_auth_events: true,
};

export default function AuditPage() {
  // ─── Estado ─────────────────────────────────────────────────────────────

  // Filtros que el usuario está editando en el formulario.
  const [filters, setFilters] = useState<AuditLogFilters>(EMPTY_FILTERS);

  // Página de resultados devuelta por el backend.
  const [page, setPage] = useState<AuditLogPage | null>(null);

  // Desplazamiento actual dentro del total de resultados.
  const [offset, setOffset] = useState(0);

  // Catálogo para poblar los desplegables de acción y entidad.
  const [catalog, setCatalog] = useState<AuditCatalog>({ actions: [], entities: [] });

  // Fincas del usuario, para el desplegable de finca.
  const [farms, setFarms] = useState<FarmResponse[]>([]);

  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState("");

  // ─── Carga de datos ─────────────────────────────────────────────────────

  /**
   * ¿Qué? Consulta la auditoría con los filtros y el offset actuales.
   * ¿Para qué? Refrescar la tabla al filtrar o al cambiar de página.
   * ¿Impacto? Se envuelve en useCallback para que el useEffect de abajo no
   *           se dispare en cada render y genere peticiones infinitas.
   */
  const loadLogs = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const result = await searchAuditLogs({ ...filters, limit: PAGE_SIZE, offset });
      setPage(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cargar la auditoría");
    } finally {
      setLoading(false);
    }
  }, [filters, offset]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  /**
   * ¿Qué? Carga una sola vez el catálogo de acciones/entidades y las fincas.
   * ¿Para qué? Que los desplegables muestren únicamente valores que existen.
   * ¿Impacto? Si falla, la tabla sigue funcionando; por eso no se muestra un
   *           error bloqueante al usuario.
   */
  useEffect(() => {
    getAuditCatalog()
      .then(setCatalog)
      .catch(() => setCatalog({ actions: [], entities: [] }));
    listFarms()
      .then(setFarms)
      .catch(() => setFarms([]));
  }, []);

  // ─── Manejadores ────────────────────────────────────────────────────────

  /**
   * ¿Qué? Actualiza un filtro y regresa a la primera página.
   * ¿Para qué? Evitar quedar en la página 5 de un resultado que ahora tiene 2.
   */
  const updateFilter = (key: keyof AuditLogFilters, value: string | boolean) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value === "" ? undefined : value,
    }));
    setOffset(0);
  };

  const resetFilters = () => {
    setFilters(EMPTY_FILTERS);
    setOffset(0);
  };

  /**
   * COMO: Administrador
   * QUIERO: descargar exactamente lo que estoy viendo
   * PARA:   que el archivo coincida con la evidencia que estoy reportando.
   *
   * ¿Impacto? Se envían los mismos filtros pero SIN limit/offset: el backend
   *           exporta todos los registros que los cumplen, no solo la página.
   */
  const handleDownload = async (format: "csv" | "excel") => {
    setDownloading(true);
    setError("");
    try {
      await downloadAuditLogs(format, filters);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo descargar el archivo");
    } finally {
      setDownloading(false);
    }
  };

  // ─── Cálculos de paginación ─────────────────────────────────────────────

  const total = page?.total ?? 0;
  const shownFrom = total === 0 ? 0 : offset + 1;
  const shownTo = Math.min(offset + PAGE_SIZE, total);
  const hasPrevious = offset > 0;
  const hasNext = offset + PAGE_SIZE < total;

  return (
    <div className="space-y-6">
      {/* Encabezado y botones de descarga */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-primary" size={24} />
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Auditoría del sistema</h1>
            <p className="text-sm text-text-secondary">
              Historial de acciones realizadas sobre los datos de tus fincas
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => handleDownload("csv")}
            disabled={downloading || total === 0}
            className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt disabled:opacity-50"
          >
            <Download size={16} /> CSV
          </button>
          <button
            onClick={() => handleDownload("excel")}
            disabled={downloading || total === 0}
            className="flex items-center gap-2 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-white transition-colors hover:opacity-90 disabled:opacity-50"
          >
            <Download size={16} /> Excel
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="rounded-2xl bg-surface p-6 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Filter size={18} className="text-text-secondary" />
          <h2 className="text-lg font-bold text-text-primary">Filtros</h2>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Field label="Finca">
            <select
              value={filters.farm_id ?? ""}
              onChange={(e) => updateFilter("farm_id", e.target.value)}
              className={inputClass}
            >
              <option value="">Todas mis fincas</option>
              {farms.map((farm) => (
                <option key={farm.id} value={farm.id}>
                  {farm.name}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Acción">
            <select
              value={filters.action ?? ""}
              onChange={(e) => updateFilter("action", e.target.value)}
              className={inputClass}
            >
              <option value="">Todas las acciones</option>
              {catalog.actions.map((action) => (
                <option key={action} value={action}>
                  {action}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Entidad">
            <select
              value={filters.entity ?? ""}
              onChange={(e) => updateFilter("entity", e.target.value)}
              className={inputClass}
            >
              <option value="">Todas las entidades</option>
              {catalog.entities.map((entity) => (
                <option key={entity} value={entity}>
                  {entity}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Desde">
            <input
              type="date"
              value={filters.start_date ?? ""}
              onChange={(e) => updateFilter("start_date", e.target.value)}
              className={inputClass}
            />
          </Field>

          <Field label="Hasta">
            <input
              type="date"
              value={filters.end_date ?? ""}
              onChange={(e) => updateFilter("end_date", e.target.value)}
              className={inputClass}
            />
          </Field>

          <div className="flex items-end gap-3">
            {/*
              COMO: Administrador revisando cambios de datos
              QUIERO: poder ocultar los inicios y cierres de sesión
              PARA:   que el ruido de los logins no tape los cambios reales
                      sobre bovinos, fincas o tratamientos.
            */}
            <label className="flex flex-1 items-center gap-2 text-sm text-text-secondary">
              <input
                type="checkbox"
                checked={filters.include_auth_events ?? true}
                onChange={(e) => updateFilter("include_auth_events", e.target.checked)}
                className="h-4 w-4 accent-primary"
              />
              Incluir eventos de sesión
            </label>

            <button
              onClick={resetFilters}
              className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt"
            >
              <RotateCcw size={16} /> Limpiar
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-danger bg-danger/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {/* Tabla de resultados */}
      <div className="rounded-2xl bg-surface p-6 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-bold text-text-primary">Registros</h2>
          <p className="text-sm text-text-secondary">
            {loading
              ? "Cargando…"
              : total === 0
                ? "Sin registros para estos filtros"
                : `Mostrando ${shownFrom}–${shownTo} de ${total}`}
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs uppercase tracking-wide text-text-muted">
                <th className="px-3 py-2">Fecha y hora</th>
                <th className="px-3 py-2">Usuario</th>
                <th className="px-3 py-2">Acción</th>
                <th className="px-3 py-2">Entidad</th>
                <th className="px-3 py-2">Finca</th>
                <th className="px-3 py-2">Detalles</th>
              </tr>
            </thead>
            <tbody>
              {!loading &&
                page?.items.map((log) => (
                  <tr key={log.id} className="border-b border-border/50 hover:bg-surface-alt">
                    <td className="whitespace-nowrap px-3 py-2 text-text-secondary">
                      {new Date(log.created_at).toLocaleString("es-CO")}
                    </td>
                    <td className="px-3 py-2 text-text-primary">
                      {/*
                        Un usuario eliminado deja el registro sin nombre, pero la
                        fila se conserva: la evidencia de auditoría no debe
                        perderse porque la cuenta ya no exista.
                      */}
                      {log.user_full_name ?? "Usuario eliminado"}
                      {log.user_email && (
                        <span className="block text-xs text-text-muted">{log.user_email}</span>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-text-secondary">
                      {log.entity}
                      {log.entity_id && (
                        <span className="block text-xs text-text-muted">{log.entity_id}</span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-text-secondary">{log.farm_name ?? "—"}</td>
                    <td
                      className="max-w-xs truncate px-3 py-2 text-text-muted"
                      title={log.details ?? ""}
                    >
                      {log.details ?? "—"}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        <div className="mt-4 flex items-center justify-end gap-2">
          <button
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            disabled={!hasPrevious || loading}
            className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt disabled:opacity-40"
          >
            Anterior
          </button>
          <button
            onClick={() => setOffset(offset + PAGE_SIZE)}
            disabled={!hasNext || loading}
            className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt disabled:opacity-40"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Componentes auxiliares locales ──────────────────────────────────────────

const inputClass =
  "w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-text-muted">
        {label}
      </label>
      {children}
    </div>
  );
}
