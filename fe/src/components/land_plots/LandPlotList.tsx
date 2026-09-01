import { useEffect, useState } from "react";
import { MapPin, Ruler, Users } from "lucide-react";
import { listLandPlots, deleteLandPlot, type LandPlotResponse } from "../../api/land_plots";
import { getApiErrorMessage } from "../../api/errors";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";
import ConfirmDialog from "../ConfirmDialog";
import LandPlotFormModal from "./LandPlotFormModal";

interface Props {
  farmId: string;
}

const USAGE_LABEL: Record<string, string> = {
  pastoreo: "Pastoreo",
  cultivo: "Cultivo",
  reserva: "Reserva",
  infraestructura: "Infraestructura",
  otro: "Otro",
};

const USAGE_BADGE: Record<string, string> = {
  pastoreo: "bg-green-50 text-green-700",
  cultivo: "bg-amber-50 text-amber-700",
  reserva: "bg-blue-50 text-blue-700",
  infraestructura: "bg-purple-50 text-purple-700",
  otro: "bg-surface-alt text-text-secondary",
};

export default function LandPlotList({ farmId }: Props) {
  const [plots, setPlots] = useState<LandPlotResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<LandPlotResponse | undefined>();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [toDelete, setToDelete] = useState<LandPlotResponse | null>(null);

  const getValue = (lp: LandPlotResponse, key: string): string | number => {
    const v = (lp as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { page, pageCount, start, end, total, paginated, setPage } =
    useTable<LandPlotResponse>(plots, { getValue });

  const fetchPlots = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listLandPlots(farmId);
      setPlots(data);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudieron cargar los lotes"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setPage(1); }, [farmId, setPage]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchPlots(); }, [farmId]);

  const handleDelete = async () => {
    if (!toDelete) return;
    setActionLoading(toDelete.id);
    try {
      await deleteLandPlot(farmId, toDelete.id);
      setToDelete(null);
      await fetchPlots();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo eliminar el lote"));
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
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-text-primary">Lotes</h2>
          <p className="text-xs text-text-muted">{activeCount} activo{activeCount !== 1 ? "s" : ""} · {plots.length - activeCount} inactivo{plots.length - activeCount !== 1 ? "s" : ""}</p>
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
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">No hay lotes registrados en esta finca</p>
        </div>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {paginated.map((lp) => (
              <div key={lp.id} className={`rounded-xl border p-4 ${lp.is_active ? "border-border bg-surface" : "border-border bg-surface-alt opacity-70"}`}>
                <div className="mb-2 flex items-start justify-between">
                  <span className="font-semibold text-text-primary">{lp.name}</span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${lp.is_active ? "bg-green-50 text-green-700" : "bg-surface-alt text-text-secondary"}`}>
                    {lp.is_active ? "Activo" : "Inactivo"}
                  </span>
                </div>
                <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${USAGE_BADGE[lp.usage_type] ?? USAGE_BADGE.otro}`}>
                  <MapPin size={11} /> {USAGE_LABEL[lp.usage_type] ?? lp.usage_type}
                </span>
                <p className="mt-2 flex items-center gap-1 text-xs text-text-secondary"><Ruler size={12} /> {lp.area} {lp.area_unit}</p>
                <p className="flex items-center gap-1 text-xs text-text-secondary"><Users size={12} /> Cap. máx: {lp.max_capacity} animales</p>
                <div className="mt-3 flex gap-2">
                  <button onClick={() => { setEditing(lp); setShowModal(true); }}
                    className="rounded px-2 py-1 text-xs font-medium text-text-secondary hover:bg-surface-alt">
                    Editar
                  </button>
                  <button onClick={() => setToDelete(lp)} disabled={actionLoading === lp.id}
                    className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50">
                    Eliminar
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4">
            <Pagination page={page} pageCount={pageCount} start={start} end={end} total={total} onChange={(p) => setPage(p)} />
          </div>
        </>
      )}

      {showModal && (
        <LandPlotFormModal
          farmId={farmId}
          existing={editing}
          onSuccess={handleSuccess}
          onClose={() => { setShowModal(false); setEditing(undefined); }}
        />
      )}

      <ConfirmDialog
        open={!!toDelete}
        title="Eliminar lote"
        message={`¿Eliminar el lote "${toDelete?.name}"? Esta acción es irreversible.`}
        confirmLabel="Eliminar"
        loading={actionLoading !== null}
        onConfirm={handleDelete}
        onCancel={() => setToDelete(null)}
      />
    </div>
  );
}
