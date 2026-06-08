import { useEffect, useState } from "react";
import {
  listSanitaryPlans,
  deleteSanitaryPlan,
  markSanitaryPlanAsApplied,
  type SanitaryPlanResponse,
} from "../../api/sanitary_plans";

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

  const fetchPlans = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listSanitaryPlans(farmId);
      setPlans(data);
    } catch {
      setError("No se pudieron cargar los planes sanitarios");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, [farmId]);

  const handleMarkApplied = async (plan: SanitaryPlanResponse) => {
    if (!confirm(`¿Marcar "${plan.vaccine_or_treatment_name}" como aplicado?`))
      return;
    setActionLoading(plan.id);
    try {
      await markSanitaryPlanAsApplied(farmId, plan.id);
      await fetchPlans();
    } catch {
      setError("No se pudo marcar como aplicado");
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
    } catch {
      setError("No se pudo desactivar el plan");
    } finally {
      setActionLoading(null);
    }
  };

  const isOverdue = (date: string | null) => {
    if (!date) return false;
    return new Date(date) < new Date();
  };

  return (
    <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-900">
            Planes Sanitarios
          </h2>
          <p className="text-xs text-gray-400">
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
        <div className="rounded-lg border border-dashed border-gray-200 py-10 text-center">
          <p className="text-sm text-gray-400">
            No hay planes sanitarios registrados
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">
                <th className="pb-2 pr-4">Tratamiento</th>
                <th className="pb-2 pr-4">Tipo</th>
                <th className="pb-2 pr-4">Frecuencia</th>
                <th className="pb-2 pr-4">Última aplicación</th>
                <th className="pb-2 pr-4">Próxima fecha</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {plans.map((plan) => {
                const overdue = isOverdue(plan.next_scheduled_date);
                const freqLabel =
                  FREQUENCY_LABEL[plan.frequency_days] ??
                  `Cada ${plan.frequency_days} días`;

                return (
                  <tr
                    key={plan.id}
                    className={`hover:bg-gray-50 ${overdue ? "bg-red-50" : ""}`}
                  >
                    <td className="py-3 pr-4 font-medium text-gray-800">
                      {plan.vaccine_or_treatment_name}
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          TYPE_BADGE[plan.treatment_type] ??
                          "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {plan.treatment_type}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-gray-500">{freqLabel}</td>
                    <td className="py-3 pr-4 text-gray-500">
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
                        {overdue && " 🔴"}
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
        </div>
      )}
    </div>
  );
}
