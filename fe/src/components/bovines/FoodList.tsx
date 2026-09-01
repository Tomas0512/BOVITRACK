import { useEffect, useState } from "react";
import { Sprout } from "lucide-react";
import {
  listConsumptions,
  listFoods,
  type ConsumptionResponse,
  type FoodResponse,
} from "../../api/food";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";

interface Props {
  farmId: string;
  bovineId: string;
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString("es-CO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function FoodList({ farmId, bovineId }: Props) {
  const [consumptions, setConsumptions] = useState<ConsumptionResponse[]>([]);
  const [foodMap, setFoodMap] = useState<Record<string, FoodResponse>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      listConsumptions(farmId, { bovine_id: bovineId }),
      listFoods(farmId),
    ])
      .then(([consumptions, foods]) => {
        if (cancelled) return;
        setConsumptions(consumptions);
        const map: Record<string, FoodResponse> = {};
        for (const f of foods) map[f.id] = f;
        setFoodMap(map);
      })
      .catch(() => {
        if (!cancelled) setError("No se pudo cargar el historial de alimentación.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [farmId, bovineId]);

  const getValue = (c: ConsumptionResponse, key: string): string | number => String((c as unknown as Record<string, unknown>)[key] ?? "");
  const { page, pageCount, start, end, total, paginated, setPage } = useTable<ConsumptionResponse>(consumptions, { getValue });

  return (
    <div className="rounded-2xl bg-surface p-6 shadow-sm">
      <h3 className="mb-4 font-bold text-text-primary"><Sprout size={18} className="inline-block mr-1.5 -mt-0.5" /> Historial de alimentación</h3>

      {loading && (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
      {error && (
        <p className="py-4 text-center text-sm text-red-500">{error}</p>
      )}
      {!loading && !error && consumptions.length === 0 && (
        <p className="py-6 text-center text-sm text-text-muted">
          Sin registros de alimentación para este animal.
        </p>
      )}
      {!loading && !error && consumptions.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">Fecha</th>
                <th className="pb-2 pr-4">Alimento</th>
                <th className="pb-2 pr-4">Categoría</th>
                <th className="pb-2 pr-4">Cantidad</th>
                <th className="pb-2">Observaciones</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((c) => {
                const food = foodMap[c.food_id];
                return (
                  <tr
                    key={c.id}
                    className="border-b border-border last:border-0 hover:bg-surface-alt"
                  >
                    <td className="py-2 pr-4 text-text-secondary whitespace-nowrap">
                      {formatDateTime(c.feeding_date)}
                    </td>
                    <td className="py-2 pr-4 font-medium text-text-primary">
                      {food?.name ?? (
                        <span className="text-text-muted text-xs">ID: {c.food_id.slice(0, 8)}…</span>
                      )}
                    </td>
                    <td className="py-2 pr-4">
                      {food ? (
                        <span className="rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700">
                          {food.category}
                        </span>
                      ) : (
                        <span className="text-text-muted">—</span>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-text-secondary">
                      {Number(c.quantity).toFixed(2)}{" "}
                      <span className="text-xs text-text-muted">
                        {food?.unit_of_measure ?? ""}
                      </span>
                    </td>
                    <td className="py-2 text-text-secondary">
                      {c.observations ?? (
                        <span className="text-text-muted">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {total > 0 && (
        <div className="mt-4">
          <Pagination page={page} pageCount={pageCount} start={start} end={end} total={total} onChange={(p) => setPage(p)} />
        </div>
      )}
    </div>
  );
}
