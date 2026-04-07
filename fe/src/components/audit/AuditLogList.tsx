import { useEffect, useState } from "react";
import { listAuditLogs, type AuditLogEntry } from "../../api/audit_logs";

interface Props {
  farmId: string;
}

const ACTION_LABELS: Record<string, string> = {
  login: "Inicio de sesión",
  logout: "Cierre de sesión",
  delete_account: "Cuenta desactivada",
  create: "Creación",
  update: "Actualización",
  delete: "Eliminación",
};

const ENTITY_LABELS: Record<string, string> = {
  user: "Usuario",
  farm: "Finca",
  bovine: "Bovino",
  paddock: "Potrero",
  land_plot: "Lote",
  treatment: "Tratamiento",
  milk_production: "Producción de leche",
  food: "Alimento",
  task: "Tarea",
};

export default function AuditLogList({ farmId }: Props) {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    listAuditLogs(farmId)
      .then(setLogs)
      .catch(() => setError("No se pudo cargar el historial de auditoría"))
      .finally(() => setLoading(false));
  }, [farmId, open]);

  return (
    <div className="mt-6">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between rounded-2xl bg-white px-6 py-4 shadow-sm hover:bg-gray-50"
      >
        <span className="flex items-center gap-2 font-bold text-gray-900">
          🗂️ Historial de auditoría
        </span>
        <span className="text-gray-400">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="mt-2 rounded-2xl bg-white p-6 shadow-sm">
          {loading && (
            <div className="flex justify-center py-6">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            </div>
          )}
          {error && <p className="py-4 text-center text-sm text-red-500">{error}</p>}
          {!loading && !error && logs.length === 0 && (
            <p className="py-4 text-center text-sm text-gray-400">Sin registros de actividad.</p>
          )}
          {!loading && !error && logs.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-100 text-xs font-semibold uppercase tracking-wide text-gray-400">
                    <th className="pb-2 pr-4">Fecha</th>
                    <th className="pb-2 pr-4">Usuario</th>
                    <th className="pb-2 pr-4">Acción</th>
                    <th className="pb-2 pr-4">Módulo</th>
                    <th className="pb-2">Detalles</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id} className="border-b border-gray-50 last:border-0">
                      <td className="py-2 pr-4 text-gray-500 whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString("es-CO")}
                      </td>
                      <td className="py-2 pr-4">
                        <p className="font-medium text-gray-800">{log.user_full_name ?? "—"}</p>
                        <p className="text-xs text-gray-400">{log.user_email ?? ""}</p>
                      </td>
                      <td className="py-2 pr-4">
                        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                          {ACTION_LABELS[log.action] ?? log.action}
                        </span>
                      </td>
                      <td className="py-2 pr-4 text-gray-600">
                        {ENTITY_LABELS[log.entity] ?? log.entity}
                      </td>
                      <td className="py-2 max-w-xs truncate text-xs text-gray-400" title={log.details ?? ""}>
                        {log.details ?? "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
