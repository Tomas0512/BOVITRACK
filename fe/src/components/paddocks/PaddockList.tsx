import { useEffect, useState } from "react";
import { listPaddocks, deletePaddock, type PaddockResponse } from "../../api/paddocks";
import { listLandPlots } from "../../api/land_plots";
import PaddockFormModal from "./PaddockFormModal";

interface Props {
  farmId: string;
}

const STATUS_BADGE: Record<string, string> = {
  libre: "bg-green-50 text-green-700",
  ocupado: "bg-yellow-50 text-yellow-700",
  en_descanso: "bg-blue-50 text-blue-700",
};

const COVERAGE_BADGE: Record<string, string> = {
  bueno: "bg-green-50 text-green-700",
  regular: "bg-yellow-50 text-yellow-700",
  malo: "bg-red-50 text-red-700",
};

export default function PaddockList({ farmId }: Props) {
  const [paddocks, setPaddocks] = useState<PaddockResponse[]>([]);
  const [hasLandPlots, setHasLandPlots] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<PaddockResponse | undefined>();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("");

  const fetchPaddocks = async () => {
    setLoading(true);
    setError("");
    try {
      const [data, plots] = await Promise.all([
        listPaddocks(farmId, statusFilter || undefined),
        listLandPlots(farmId),
      ]);
      setPaddocks(data);
      setHasLandPlots(plots.filter((p) => p.is_active).length > 0);
    } catch {
      setError("No se pudieron cargar los potreros");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPaddocks(); }, [farmId, statusFilter]);

  const handleDelete = async (p: PaddockResponse) => {
    if (!confirm(`¿Eliminar el potrero "${p.name}"?`)) return;
    setActionLoading(p.id);
    try {
      await deletePaddock(farmId, p.id);
      await fetchPaddocks();
    } catch {
      setError("No se pudo eliminar el potrero");
    } finally {
      setActionLoading(null);
    }
  };

  const handleSuccess = () => {
    setShowModal(false);
    setEditing(undefined);
    fetchPaddocks();
  };

  const counts = { libre: 0, ocupado: 0, en_descanso: 0 };
  paddocks.forEach((p) => { if (p.status in counts) counts[p.status as keyof typeof counts]++; });

  return (
    <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Potreros</h2>
          <p className="text-xs text-gray-400">
            {counts.libre} libre{counts.libre !== 1 ? "s" : ""} · {counts.ocupado} ocupado{counts.ocupado !== 1 ? "s" : ""} · {counts.en_descanso} en descanso
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <button
            onClick={() => { setEditing(undefined); setShowModal(true); }}
            disabled={!hasLandPlots}
            title={!hasLandPlots ? "Registre al menos un lote antes de crear potreros" : undefined}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:cursor-not-allowed disabled:opacity-40">
            + Nuevo potrero
          </button>
          {!hasLandPlots && (
            <p className="text-xs text-amber-600">⚠ Debe existir al menos un lote activo</p>
          )}
        </div>
      </div>

      {/* Filtro por estado */}
      <div className="mb-4 flex gap-2">
        {[{ key: "", label: "Todos" }, { key: "libre", label: "Libres" }, { key: "ocupado", label: "Ocupados" }, { key: "en_descanso", label: "En descanso" }].map((f) => (
          <button key={f.key} onClick={() => setStatusFilter(f.key)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              statusFilter === f.key ? "bg-primary text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}>
            {f.label}
          </button>
        ))}
      </div>

      {error && <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : paddocks.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-200 py-10 text-center">
          <p className="text-sm text-gray-400">No hay potreros registrados en esta finca</p>
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {paddocks.map((p) => (
            <div key={p.id} className="rounded-xl border border-gray-100 bg-surface p-4">
              <div className="mb-2 flex items-start justify-between">
                <span className="font-semibold text-gray-800">{p.name}</span>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[p.status] ?? "bg-gray-100 text-gray-600"}`}>
                  {p.status.replace("_", " ")}
                </span>
              </div>
              <p className="text-xs text-gray-500">{p.area_hectares} ha · Cap. {p.max_capacity}</p>
              <p className="text-xs text-gray-500">
                Cobertura: <span className={`rounded px-1 text-xs font-medium ${COVERAGE_BADGE[p.coverage_status] ?? ""}`}>{p.coverage_status}</span>
              </p>
              {p.pasture_type && (
                <p className="text-xs text-gray-500">Pasto: {p.pasture_type.replace("_", " ")}</p>
              )}
              {p.rest_start_date && (
                <p className="mt-1 text-xs text-blue-600">
                  Descanso: {p.rest_start_date} → {p.rest_end_date ?? "..."}
                </p>
              )}
              <div className="mt-3 flex gap-2">
                <button onClick={() => { setEditing(p); setShowModal(true); }}
                  className="rounded px-2 py-1 text-xs font-medium text-gray-500 hover:bg-gray-100">
                  Editar
                </button>
                <button onClick={() => handleDelete(p)} disabled={actionLoading === p.id}
                  className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50">
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <PaddockFormModal
          farmId={farmId}
          existing={editing}
          onSuccess={handleSuccess}
          onClose={() => { setShowModal(false); setEditing(undefined); }}
        />
      )}
    </div>
  );
}
