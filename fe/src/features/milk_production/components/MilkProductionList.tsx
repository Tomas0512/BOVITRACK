import { useEffect, useState } from "react";
import { Droplets, Plus, Pencil, Trash2 } from "lucide-react";
import {
  listMilkProduction,
  deleteMilkProduction,
  type MilkProductionResponse,
} from "../../api/milk_production";
import { listBovines, type BovineResponse } from "../../api/bovines";
import { getApiErrorMessage } from "../../api/errors";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";
import ConfirmDialog from "../ConfirmDialog";
import MilkProductionFormModal from "../milk/MilkProductionFormModal";

interface Props {
  farmId: string;
  bovineId: string;
}

const MILKING_TYPE_LABELS: Record<string, string> = {
  manual: "Manual",
  mecanico: "Mecánico",
};

const SESSION_LABELS: Record<string, string> = {
  "mañana": "Mañana",
  "tarde": "Tarde",
  "noche": "Noche",
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
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<MilkProductionResponse | null>(null);
  const [deleting, setDeleting] = useState<MilkProductionResponse | null>(null);
  const [deleteError, setDeleteError] = useState("");

  const loadAll = async () => {
    setLoading(true);
    setError("");
    try {
      const [recordsData, bovinesData] = await Promise.all([
        listMilkProduction(farmId, { bovine_id: bovineId }),
        listBovines(farmId),
      ]);
      setRecords(recordsData);
      setBovines(bovinesData);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo cargar el historial de ordeño."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId, bovineId]);

  const currentBovine = bovines.find((b) => b.id === bovineId);

  const getValue = (r: MilkProductionResponse, key: string): string | number => {
    const v = (r as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { page, pageCount, start, end, total, paginated, setPage } =
    useTable<MilkProductionResponse>(records, { getValue, initialKey: "milking_date", initialDir: "desc" });

  const totalLitros = records.reduce((sum, r) => sum + Number(r.quantity_liters), 0);
  const days = () => {
    const set = new Set(records.map((r) => new Date(r.milking_date).toDateString()));
    return set.size;
  };

  const handleDelete = async () => {
    if (!deleting) return;
    setDeleteError("");
    try {
      await deleteMilkProduction(farmId, deleting.id);
      setDeleting(null);
      loadAll();
    } catch (err: unknown) {
      setDeleteError(getApiErrorMessage(err, "No se pudo eliminar el ordeño"));
    }
  };

  return (
    <div className="rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-bold text-text-primary"><Droplets size={18} className="inline mr-1.5 align-text-bottom text-blue-600" />Historial de ordeño</h3>
        <div className="flex flex-wrap items-center gap-2">
          {records.length > 0 && (
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              {totalLitros.toFixed(1)} L · {records.length} ordeños · {days()} días · {records.length > 0 ? (totalLitros / days()).toFixed(1) : "0"} L/día
            </span>
          )}
          <button onClick={() => { setEditing(null); setShowForm(true); }}
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-sm font-bold text-white hover:bg-primary-light">
            <Plus size={14} /> Ordeño
          </button>
        </div>
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
          <table className="w-full min-w-[540px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">Fecha</th>
                <th className="pb-2 pr-4">Sesión</th>
                <th className="pb-2 pr-4">Tipo</th>
                <th className="pb-2 pr-4">Litros</th>
                <th className="pb-2 pr-4">Observaciones</th>
                <th className="pb-2 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((r) => (
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
                  <td className="py-2">
                    <div className="flex justify-end gap-1">
                      <button onClick={() => { setEditing(r); setShowForm(true); }} aria-label="Editar"
                        className="rounded-lg p-1.5 text-text-muted hover:bg-blue-50 hover:text-blue-700">
                        <Pencil size={15} />
                      </button>
                      <button onClick={() => setDeleting(r)} aria-label="Eliminar"
                        className="rounded-lg p-1.5 text-text-muted hover:bg-red-50 hover:text-red-600">
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4">
            <Pagination page={page} pageCount={pageCount} start={start} end={end} total={total} onChange={(p) => setPage(p)} />
          </div>
        </div>
      )}

      {showForm && (
        <MilkProductionFormModal
          farmId={farmId}
          bovines={currentBovine ? [currentBovine] : []}
          landPlots={[]}
          lockedBovineId={bovineId}
          existing={editing ?? undefined}
          onSuccess={() => { setShowForm(false); setEditing(null); loadAll(); }}
          onClose={() => { setShowForm(false); setEditing(null); }}
        />
      )}

      <ConfirmDialog
        open={Boolean(deleting)}
        title="Eliminar ordeño"
        message={`¿Eliminar el ordeño de ${deleting ? formatDate(deleting.milking_date) : ""} (${deleting ? Number(deleting.quantity_liters).toFixed(1) : ""} L)? Esta acción es permanente.`}
        confirmLabel="Eliminar"
        onConfirm={handleDelete}
        onCancel={() => { setDeleting(null); setDeleteError(""); }}
      >
        {deleteError && <p className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{deleteError}</p>}
      </ConfirmDialog>
    </div>
  );
}