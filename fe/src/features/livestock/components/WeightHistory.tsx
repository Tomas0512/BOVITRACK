import { useEffect, useState } from "react";
import { Scale, X } from "lucide-react";
import {
  listWeights,
  createWeight,
  deleteWeight,
  type WeightResponse,
  type WeightCreate,
} from "../../api/weights";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";

interface Props {
  farmId: string;
  bovineId: string;
}

const BODY_CONDITION_LABELS: Record<number, string> = {
  1: "1 – Muy delgado",
  2: "2 – Delgado",
  3: "3 – Normal",
  4: "4 – Gordo",
  5: "5 – Muy gordo",
};

function formatDate(iso: string) {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

const EMPTY_FORM: WeightCreate = {
  weight_kg: 0,
  measured_at: new Date().toISOString().slice(0, 10),
  body_condition: undefined,
  observations: "",
};

export default function WeightHistory({ farmId, bovineId }: Props) {
  const [weights, setWeights] = useState<WeightResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<WeightCreate>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const getValue = (w: WeightResponse, key: string): string | number => {
    const v = (w as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { page, pageCount, start, end, total, paginated, setPage, sortKey, sortDir, handleSort } =
    useTable<WeightResponse>(weights, { initialKey: "measured_at", initialDir: "desc", getValue });

  function load() {
    setLoading(true);
    listWeights(farmId, bovineId)
      .then(setWeights)
      .catch(() => setError("No se pudo cargar el historial de pesajes."))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId, bovineId]);

  const isFormComplete = form.weight_kg > 0 && form.measured_at !== "";

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError("");
    if (!form.weight_kg || form.weight_kg <= 0) {
      setFormError("El peso debe ser mayor a 0 kg.");
      return;
    }
    if (!form.measured_at) {
      setFormError("La fecha de medición es obligatoria.");
      return;
    }
    setSaving(true);
    try {
      await createWeight(farmId, bovineId, {
        ...form,
        body_condition: form.body_condition ?? null,
        observations: form.observations || null,
      });
      setForm(EMPTY_FORM);
      setShowModal(false);
      load();
    } catch {
      setFormError("No se pudo registrar el pesaje. Intente de nuevo.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(weightId: string) {
    if (!confirm("¿Eliminar este registro de pesaje?")) return;
    setDeletingId(weightId);
    try {
      await deleteWeight(farmId, bovineId, weightId);
      load();
    } catch {
      alert("No se pudo eliminar el pesaje.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-text-primary">
          <Scale size={18} className="inline mr-1.5 align-text-bottom text-primary" />
          Historial de pesajes
        </h3>
        <button
          onClick={() => {
            setForm(EMPTY_FORM);
            setFormError("");
            setShowModal(true);
          }}
          className="rounded-lg bg-primary px-4 py-1.5 text-sm font-medium text-white hover:bg-primary/90"
        >
          + Registrar pesaje
        </button>
      </div>

      {/* Modal para registrar pesaje */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={() => setShowModal(false)}
        >
          <div
            className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-bold text-primary">Registrar pesaje</h2>
              <button
                onClick={() => setShowModal(false)}
                className="rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary"
                aria-label="Cerrar"
              >
                <X size={20} />
              </button>
            </div>

            {formError && (
              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreate} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">
                  Peso (kg) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number" step="0.01" min="0.01" required
                  value={form.weight_kg || ""}
                  onChange={(e) => setForm((f) => ({ ...f, weight_kg: parseFloat(e.target.value) }))}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">
                  Fecha de medición <span className="text-red-500">*</span>
                </label>
                <input
                  type="date" required
                  max={new Date().toISOString().slice(0, 10)}
                  value={form.measured_at}
                  onChange={(e) => setForm((f) => ({ ...f, measured_at: e.target.value }))}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">
                  Condición corporal (1–5)
                </label>
                <select
                  value={form.body_condition ?? ""}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      body_condition: e.target.value ? parseInt(e.target.value) : undefined,
                    }))
                  }
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                >
                  <option value="">— Sin registrar —</option>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>{BODY_CONDITION_LABELS[n]}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">
                  Observaciones
                </label>
                <input
                  type="text" maxLength={500}
                  value={form.observations ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, observations: e.target.value }))}
                  placeholder="Opcional"
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                />
                <span className="mt-0.5 block text-right text-xs text-text-muted">{(form.observations ?? "").length}/500</span>
              </div>

              <div className="col-span-full mt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!isFormComplete || saving}
                  className={`rounded-lg px-6 py-2 text-sm font-medium text-white transition-colors ${
                    !isFormComplete || saving
                      ? "cursor-not-allowed bg-gray-400 opacity-70"
                      : "bg-primary hover:bg-primary/90"
                  }`}
                >
                  {saving ? "Guardando…" : "Guardar pesaje"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
      {error && (
        <p className="py-4 text-center text-sm text-red-500">{error}</p>
      )}
      {!loading && !error && weights.length === 0 && (
        <p className="py-6 text-center text-sm text-text-muted">
          Sin registros de pesaje. Registra el primero.
        </p>
      )}
      {!loading && !error && weights.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("measured_at")} className="uppercase">Fecha {sortKey === "measured_at" && (sortDir === "asc" ? "▲" : "▼")}</button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("weight_kg")} className="uppercase">Peso (kg) {sortKey === "weight_kg" && (sortDir === "asc" ? "▲" : "▼")}</button>
                </th>
                <th className="pb-2 pr-4">Ganancia diaria</th>
                <th className="pb-2 pr-4">Cond. corporal</th>
                <th className="pb-2 pr-4">Observaciones</th>
                <th className="pb-2" />
              </tr>
            </thead>
            <tbody>
              {paginated.map((w) => (
                <tr
                  key={w.id}
                  className="border-b border-border last:border-0 hover:bg-surface-alt"
                >
                  <td className="py-2 pr-4 font-medium text-text-primary whitespace-nowrap">
                    {formatDate(w.measured_at)}
                  </td>
                  <td className="py-2 pr-4 text-text-secondary">
                    {Number(w.weight_kg).toFixed(1)} kg
                  </td>
                  <td className="py-2 pr-4">
                    {w.daily_gain !== null ? (
                      <span
                        className={`font-medium ${
                          Number(w.daily_gain) >= 0 ? "text-green-600" : "text-red-500"
                        }`}
                      >
                        {Number(w.daily_gain) >= 0 ? "+" : ""}
                        {Number(w.daily_gain).toFixed(2)} kg/día
                      </span>
                    ) : (
                      <span className="text-text-muted">—</span>
                    )}
                  </td>
                  <td className="py-2 pr-4 text-text-secondary">
                    {w.body_condition !== null
                      ? BODY_CONDITION_LABELS[w.body_condition]
                      : <span className="text-text-muted">—</span>}
                  </td>
                  <td className="py-2 pr-4 text-text-secondary">
                    {w.observations ?? <span className="text-text-muted">—</span>}
                  </td>
                  <td className="py-2 text-right">
                    <button
                      onClick={() => handleDelete(w.id)}
                      disabled={deletingId === w.id}
                      className="text-xs text-red-400 hover:text-red-600 disabled:opacity-40"
                    >
                      {deletingId === w.id ? "…" : "Eliminar"}
                    </button>
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
    </div>
  );
}
