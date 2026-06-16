import { useEffect, useState } from "react";
import { Plus, AlertTriangle, Pencil, Trash2, ArrowUpDown } from "lucide-react";
import { listMovements, deleteMovement, type MovementResponse } from "../../api/movements";
import MovementFormModal from "./MovementFormModal";

const TYPE_BADGE: Record<string, string> = {
  compra: "bg-green-100 text-green-800",
  venta: "bg-red-100 text-red-800",
  traslado: "bg-blue-100 text-blue-800",
  nacimiento: "bg-purple-100 text-purple-800",
  muerte: "bg-gray-200 text-gray-700",
};

const TYPE_LABEL: Record<string, string> = {
  compra: "Compra",
  venta: "Venta",
  traslado: "Traslado",
  nacimiento: "Nacimiento",
  muerte: "Muerte",
};

interface Props {
  farmId: string;
}

export default function MovementList({ farmId }: Props) {
  const [movements, setMovements] = useState<MovementResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<MovementResponse | null>(null);
  const [filterType, setFilterType] = useState("");

  const fetchData = async () => {
    try {
      const data = await listMovements(farmId, filterType ? { movement_type: filterType } : undefined);
      setMovements(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar movimientos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [farmId, filterType]);

  const handleDelete = async (id: string) => {
    if (!confirm("¿Estás seguro de eliminar este movimiento?")) return;
    try {
      await deleteMovement(farmId, id);
      fetchData();
    } catch {
      setError("No se pudo eliminar el movimiento");
    }
  };

  return (
    <div className="mt-6">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-bold text-gray-900">Movimientos del hato</h2>
        <div className="flex items-center gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-primary focus:outline-none"
          >
            <option value="">Todos los tipos</option>
            {Object.entries(TYPE_LABEL).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
          <button onClick={() => { setEditing(null); setShowModal(true); }}
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-1.5 text-sm font-bold text-white hover:bg-primary-light">
            <Plus size={16} />
            Registrar
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={16} /> {error}
          <button onClick={() => setError("")} className="ml-auto font-bold">X</button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : movements.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 py-8 text-center text-sm text-gray-400">
          <ArrowUpDown size={32} className="mx-auto mb-2 text-gray-300" />
          No hay movimientos registrados aún
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 text-xs font-semibold uppercase text-gray-500">
              <tr>
                <th className="px-4 py-3">Tipo</th>
                <th className="px-4 py-3">Fecha</th>
                <th className="px-4 py-3">Bovino</th>
                <th className="px-4 py-3">Valor</th>
                <th className="px-4 py-3">Contraparte</th>
                <th className="px-4 py-3">Motivo</th>
                <th className="px-4 py-3 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {movements.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${TYPE_BADGE[m.movement_type] || "bg-gray-100 text-gray-600"}`}>
                      {TYPE_LABEL[m.movement_type] || m.movement_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{new Date(m.movement_date).toLocaleDateString("es-CO")}</td>
                  <td className="px-4 py-3 text-gray-700">{m.bovine_id ? m.bovine_id.slice(0, 8) + "..." : "—"}</td>
                  <td className="px-4 py-3 text-gray-700">{m.price != null ? `$${Number(m.price).toLocaleString("es-CO")}` : "—"}</td>
                  <td className="px-4 py-3 text-gray-700">{m.counterparty_name || "—"}</td>
                  <td className="max-w-[200px] truncate px-4 py-3 text-gray-500">{m.reason || "—"}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => { setEditing(m); setShowModal(true); }}
                      className="mr-1 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                      title="Editar"
                    >
                      <Pencil size={15} />
                    </button>
                    <button
                      onClick={() => handleDelete(m.id)}
                      className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
                      title="Eliminar"
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <MovementFormModal
          farmId={farmId}
          existing={editing}
          onSuccess={() => { setShowModal(false); setEditing(null); fetchData(); }}
          onClose={() => { setShowModal(false); setEditing(null); }}
        />
      )}
    </div>
  );
}
