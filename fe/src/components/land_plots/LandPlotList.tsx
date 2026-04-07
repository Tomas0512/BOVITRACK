import { useEffect, useState } from "react";
import { listLandPlots, deleteLandPlot, type LandPlotResponse } from "../../api/land_plots";
import LandPlotFormModal from "./LandPlotFormModal";

interface Props {
  farmId: string;
}

export default function LandPlotList({ farmId }: Props) {
  const [plots, setPlots] = useState<LandPlotResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<LandPlotResponse | undefined>();
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchPlots = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listLandPlots(farmId);
      setPlots(data);
    } catch {
      setError("No se pudieron cargar los lotes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPlots(); }, [farmId]);

  const handleDelete = async (lp: LandPlotResponse) => {
    if (!confirm(`¿Eliminar el lote "${lp.name}"? Esta acción es irreversible.`)) return;
    setActionLoading(lp.id);
    try {
      await deleteLandPlot(farmId, lp.id);
      await fetchPlots();
    } catch {
      setError("No se pudo eliminar el lote");
    } finally {
      setActionLoading(null);
    }
  };

  const handleSuccess = () => {
    setShowModal(false);
    setEditing(undefined);
    fetchPlots();
  };

  const activeCount = plots.filter((p) => p.is_active).length;

  return (
    <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Lotes</h2>
          <p className="text-xs text-gray-400">{activeCount} activo{activeCount !== 1 ? "s" : ""} · {plots.length - activeCount} inactivo{plots.length - activeCount !== 1 ? "s" : ""}</p>
        </div>
        <button onClick={() => { setEditing(undefined); setShowModal(true); }}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
          + Nuevo lote
        </button>
      </div>

      {error && (
        <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : plots.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-200 py-10 text-center">
          <p className="text-sm text-gray-400">No hay lotes registrados en esta finca</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {plots.map((lp) => (
            <div key={lp.id} className={`rounded-xl border p-4 ${lp.is_active ? "border-gray-100 bg-surface" : "border-gray-200 bg-gray-50 opacity-70"}`}>
              <div className="mb-2 flex items-start justify-between">
                <span className="font-semibold text-gray-800">{lp.name}</span>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${lp.is_active ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {lp.is_active ? "Activo" : "Inactivo"}
                </span>
              </div>
              <p className="text-xs text-gray-500">{lp.area} {lp.area_unit} · {lp.usage_type}</p>
              <p className="text-xs text-gray-500">Cap. máx: {lp.max_capacity} animales</p>
              <div className="mt-3 flex gap-2">
                <button onClick={() => { setEditing(lp); setShowModal(true); }}
                  className="rounded px-2 py-1 text-xs font-medium text-gray-500 hover:bg-gray-100">
                  Editar
                </button>
                <button onClick={() => handleDelete(lp)} disabled={actionLoading === lp.id}
                  className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50">
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <LandPlotFormModal
          farmId={farmId}
          existing={editing}
          onSuccess={handleSuccess}
          onClose={() => { setShowModal(false); setEditing(undefined); }}
        />
      )}
    </div>
  );
}
