import { useEffect, useState } from "react";
import { Droplets } from "lucide-react";
import {
  listMilkProduction,
  type MilkProductionResponse,
} from "../../api/milk_production";

interface Props {
  farmId: string;
  bovineId: string;
}

const MILKING_TYPE_LABELS: Record<string, string> = {
  manual: "Manual",
  mechanical: "Mecánico",
};

const SESSION_LABELS: Record<string, string> = {
  morning: "Mañana",
  afternoon: "Tarde",
  evening: "Noche",
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export default function MilkProductionList({ farmId, bovineId }: Props) {
  const [records, setRecords] = useState<MilkProductionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    listMilkProduction(farmId, bovineId)
      .then(setRecords)
      .catch(() => setError("No se pudo cargar el historial de ordeño."))
      .finally(() => setLoading(false));
  }, [farmId, bovineId]);

  const totalLitros = records.reduce((sum, r) => sum + Number(r.quantity_liters), 0);

  return (
    <div className="rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-text-primary"><Droplets size={18} className="inline mr-1.5 align-text-bottom" />Historial de ordeño</h3>
        {records.length > 0 && (
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
            Total: {totalLitros.toFixed(1)} L ({records.length} registros)
          </span>
        )}
      </div>

      {loading && (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
      {error && (
        <p className="py-4 text-center text-sm text-red-500">{error}</p>
      )}
      {!loading && !error && records.length === 0 && (
        <p className="py-6 text-center text-sm text-text-muted">
          Sin registros de ordeño para este animal.
        </p>
      )}
      {!loading && !error && records.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[480px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">Fecha</th>
                <th className="pb-2 pr-4">Sesión</th>
                <th className="pb-2 pr-4">Tipo</th>
                <th className="pb-2 pr-4">Litros</th>
                <th className="pb-2">Observaciones</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr
                  key={r.id}
                  className="border-b border-border last:border-0 hover:bg-surface-alt"
                >
                  <td className="py-2 pr-4 font-medium text-text-primary whitespace-nowrap">
                    {formatDate(r.milking_date)}
                  </td>
                  <td className="py-2 pr-4">
                    {r.milking_session ? (
                      <span className="rounded-full bg-sky-50 px-2 py-0.5 text-xs font-medium text-sky-700">
                        {SESSION_LABELS[r.milking_session] ?? r.milking_session}
                      </span>
                    ) : (
                      <span className="text-text-muted">—</span>
                    )}
                  </td>
                  <td className="py-2 pr-4 text-text-secondary">
                    {MILKING_TYPE_LABELS[r.milking_type] ?? r.milking_type}
                  </td>
                  <td className="py-2 pr-4 font-semibold text-blue-700">
                    {Number(r.quantity_liters).toFixed(1)} L
                  </td>
                  <td className="py-2 text-text-secondary">
                    {r.observations ?? <span className="text-text-muted">—</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
