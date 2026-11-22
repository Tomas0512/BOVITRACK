import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import {
  listSanitaryPlans,
  deleteSanitaryPlan,
  markSanitaryPlanAsApplied,
  type SanitaryPlanResponse,
} from "../../api/sanitary_plans";
import { getApiErrorMessage } from "../../api/errors";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";

interface Props {
  farmId: string;
}

const FREQUENCY_LABEL: Record<number, string> = {
  1: "Diaria",
  7: "Semanal",
  14: "Cada 2 semanas",
  30: "Mensual",
  60: "Cada 2 meses",
  90: "Trimestral",
  180: "Semestral",
  365: "Anual",
};

const TYPE_BADGE: Record<string, string> = {
  vacuna: "bg-blue-50 text-blue-700",
  desparasitacion: "bg-amber-50 text-amber-700",
  suplemento: "bg-purple-50 text-purple-700",
  vitamina: "bg-green-50 text-green-700",
};

export default function SanitaryPlanList({ farmId }: Props) {
  const [plans, setPlans] = useState<SanitaryPlanResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const getValue = (plan: SanitaryPlanResponse, key: string): string | number => {
    const v = (plan as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { page, pageCount, start, end, total, paginated, setPage, sortKey, sortDir, handleSort } =
    useTable<SanitaryPlanResponse>(plans, { getValue });

  const fetchPlans = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listSanitaryPlans(farmId);
      setPlans(data);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudieron cargar los planes sanitarios"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setPage(1); }, [farmId, setPage]);
  useEffect(() => {
    fetchPlans();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId]);

  const handleMarkApplied = async (plan: SanitaryPlanResponse) => {
    if (!confirm(`¿Marcar "${plan.vaccine_or_treatment_name}" como aplicado?`))
      return;
    setActionLoading(plan.id);
    try {
      await markSanitaryPlanAsApplied(farmId, plan.id);
      await fetchPlans();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo marcar como aplicado"));
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (plan: SanitaryPlanResponse) => {
    if (
      !confirm(`¿Desactivar el plan "${plan.vaccine_or_treatment_name}"?`)
    )
      return;
    setActionLoading(plan.id);
    try {
      await deleteSanitaryPlan(farmId, plan.id);
      await fetchPlans();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo desactivar el plan"));
    } finally {
      setActionLoading(null);
    }
  };

  const isOverdue = (date: string | null) => {
    if (!date) return false;
    return new Date(date) < new Date();
  };

  return (
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-text-primary">
            Planes Sanitarios
          </h2>
          <p className="text-xs text-text-muted">
            {plans.length} plan{plans.length !== 1 ? "es" : ""}
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : plans.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">
            No hay planes sanitarios registrados
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("vaccine_or_treatment_name")} className="uppercase">
                    Tratamiento {sortKey === "vaccine_or_treatment_name" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("treatment_type")} className="uppercase">
                    Tipo {sortKey === "treatment_type" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("frequency_days")} className="uppercase">
                    Frecuencia {sortKey === "frequency_days" && (sortDir === "asc" ? "▲" : "▼")}
                  </button>
                </th>
                <th className="pb-2 pr-4">Última aplicación</th>
                <th className="pb-2 pr-4">Próxima fecha</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginated.map((plan) => {
                const overdue = isOverdue(plan.next_scheduled_date);
                const freqLabel =
                  FREQUENCY_LABEL[plan.frequency_days] ??
                  `Cada ${plan.frequency_days} días`;

                return (
                  <tr
                    key={plan.id}
                    className={`hover:bg-surface-alt ${overdue ? "bg-red-500/10" : ""}`}
                  >
                    <td className="py-3 pr-4 font-medium text-text-primary">
                      {plan.vaccine_or_treatment_name}
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          TYPE_BADGE[plan.treatment_type] ??
                          "bg-surface-alt text-text-secondary"
                        }`}
                      >
                        {plan.treatment_type}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-text-secondary">{freqLabel}</td>
                    <td className="py-3 pr-4 text-text-secondary">
                      {plan.last_applied_date
                        ? new Date(
                            plan.last_applied_date,
                          ).toLocaleDateString("es-CO")
                        : "Nunca"}
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-semibold ${
                          overdue
                            ? "bg-red-100 text-red-700"
                            : "bg-green-50 text-green-700"
                        }`}
                      >
                        {plan.next_scheduled_date
                          ? new Date(
                              plan.next_scheduled_date,
                            ).toLocaleDateString("es-CO")
                          : "Pendiente"}
                        {overdue && <AlertTriangle size={14} className="inline-block ml-1 -mt-0.5 text-red-600" />}
                      </span>
                    </td>
                    <td className="py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleMarkApplied(plan)}
                          disabled={actionLoading === plan.id}
                          className="rounded px-2 py-1 text-xs font-medium text-green-600 hover:bg-green-50 disabled:opacity-50"
                        >
                          {actionLoading === plan.id
                            ? "..."
                            : "Aplicado"}
                        </button>
                        <button
                          onClick={() => handleDelete(plan)}
                          disabled={actionLoading === plan.id}
                          className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50"
                        >
                          {actionLoading === plan.id ? "..." : "Desactivar"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <Pagination
            page={page}
            pageCount={pageCount}
            start={start}
            end={end}
            total={total}
            onChange={(p) => setPage(p)}
          />
        </div>
      )}
    </div>
  );
}
