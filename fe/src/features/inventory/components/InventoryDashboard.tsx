import { useEffect, useState } from "react";
import { AlertTriangle, TrendingUp, TrendingDown, Package, DollarSign } from "lucide-react";
import { listFoods, listStockMovements, type FoodResponse, type StockMovementResponse } from "../../api/food";

interface Props {
  farmId: string;
}

const MOVEMENT_TYPE_LABELS: Record<string, string> = {
  purchase: "Compra",
  adjustment: "Ajuste",
  consumption: "Consumo",
  return: "Devolución",
};

export default function InventoryDashboard({ farmId }: Props) {
  const [foods, setFoods] = useState<FoodResponse[]>([]);
  const [recentMovements, setRecentMovements] = useState<StockMovementResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [foodData, movementData] = await Promise.all([
        listFoods(farmId),
        listStockMovements(farmId, { limit: 10 }),
      ]);
      setFoods(foodData);
      setRecentMovements(movementData);
    } catch (err: unknown) {
      setError(err instanceof Error && err.message ? err.message : "No se pudo cargar el inventario");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId]);

  const lowStockItems = foods.filter((f) => f.min_stock_alert && f.current_stock <= f.min_stock_alert);
  const totalStockValue = foods.reduce((sum, f) => sum + (f.current_stock * (f.cost_per_unit ?? 0)), 0);
  const totalItems = foods.length;
  const outOfStock = foods.filter((f) => f.current_stock <= 0).length;

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return <div className="rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>;
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-xl bg-surface p-4 shadow-sm">
          <div className="flex items-center gap-2 text-text-muted mb-1">
            <Package size={16} />
            <span className="text-xs font-medium uppercase tracking-wide">Total de insumos</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">{totalItems}</p>
        </div>
        <div className="rounded-xl bg-surface p-4 shadow-sm">
          <div className="flex items-center gap-2 text-text-muted mb-1">
            <DollarSign size={16} />
            <span className="text-xs font-medium uppercase tracking-wide">Valor del inventario</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">
            ${totalStockValue.toLocaleString("es-CO", { minimumFractionDigits: 0 })}
          </p>
        </div>
        <div className="rounded-xl bg-amber-50 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-amber-600 mb-1">
            <AlertTriangle size={16} />
            <span className="text-xs font-medium uppercase tracking-wide">Stock bajo</span>
          </div>
          <p className="text-2xl font-bold text-amber-700">{lowStockItems.length}</p>
        </div>
        <div className="rounded-xl bg-red-50 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-red-600 mb-1">
            <TrendingDown size={16} />
            <span className="text-xs font-medium uppercase tracking-wide">Sin stock</span>
          </div>
          <p className="text-2xl font-bold text-red-700">{outOfStock}</p>
        </div>
      </div>

      {lowStockItems.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
          <h3 className="text-sm font-bold text-amber-800 flex items-center gap-2 mb-2">
            <AlertTriangle size={16} /> Alertas de stock bajo
          </h3>
          <div className="space-y-1">
            {lowStockItems.map((f) => (
              <div key={f.id} className="flex justify-between text-sm text-amber-700">
                <span>{f.name}</span>
                <span className="font-medium">
                  {f.current_stock} / {f.min_stock_alert} {f.unit_of_measure}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {recentMovements.length > 0 && (
        <div>
          <h3 className="text-sm font-bold text-text-primary mb-2 flex items-center gap-2">
            <TrendingUp size={16} /> Movimientos recientes de stock
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wide text-text-muted">
                  <th className="pb-2 pr-3">Fecha</th>
                  <th className="pb-2 pr-3">Tipo</th>
                  <th className="pb-2 pr-3">Cantidad</th>
                  <th className="pb-2 pr-3">Stock anterior</th>
                  <th className="pb-2 pr-3">Stock posterior</th>
                  <th className="pb-2">Notas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {recentMovements.map((m) => (
                  <tr key={m.id} className="hover:bg-surface-alt">
                    <td className="py-2 pr-3 text-text-secondary text-xs">
                      {new Date(m.movement_date).toLocaleDateString()}
                    </td>
                    <td className="py-2 pr-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        m.movement_type === "purchase" ? "bg-green-50 text-green-700" :
                        m.movement_type === "adjustment" ? "bg-blue-50 text-blue-700" :
                        m.movement_type === "consumption" ? "bg-orange-50 text-orange-700" :
                        "bg-surface-alt text-text-secondary"
                      }`}>
                        {MOVEMENT_TYPE_LABELS[m.movement_type] ?? m.movement_type}
                      </span>
                    </td>
                    <td className={`py-2 pr-3 font-medium ${
                      m.quantity > 0 ? "text-green-600" : "text-red-600"
                    }`}>
                      {m.quantity > 0 ? "+" : ""}{m.quantity}
                    </td>
                    <td className="py-2 pr-3 text-text-secondary">{m.stock_before}</td>
                    <td className="py-2 pr-3 text-text-secondary">{m.stock_after}</td>
                    <td className="py-2 text-text-muted text-xs truncate max-w-[150px]">
                      {m.notes ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
