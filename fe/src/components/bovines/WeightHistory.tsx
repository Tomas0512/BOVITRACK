import { useEffect, useState } from "react";
import {
  listWeights,
  createWeight,
  deleteWeight,
  type WeightResponse,
  type WeightCreate,
} from "../../api/weights";

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
  // "YYYY-MM-DD" → "DD/MM/YYYY"
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
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<WeightCreate>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  function load() {
    setLoading(true);
    listWeights(farmId, bovineId)
      .then(setWeights)
      .catch(() => setError("No se pudo cargar el historial de pesajes."))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, [farmId, bovineId]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError("");
    if (!form.weight_kg || form.weight_kg <= 0) {
      setFormError("El peso debe ser mayor a 0 kg.");
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
      setShowForm(false);
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
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-gray-900">⚖️ Historial de pesajes</h3>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-lg bg-primary px-4 py-1.5 text-sm font-medium text-white hover:bg-primary/90"
        >
          {showForm ? "Cancelar" : "+ Registrar pesaje"}
        </button>
      </div>

      {/* Formulario de registro */}
      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 grid grid-cols-1 gap-4 rounded-xl border border-gray-100 bg-gray-50 p-4 sm:grid-cols-2"
        >
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Peso (kg) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              required
              value={form.weight_kg || ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, weight_kg: parseFloat(e.target.value) }))
              }
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Fecha de medición <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              required
              max={new Date().toISOString().slice(0, 10)}
              value={form.measured_at}
              onChange={(e) =>
                setForm((f) => ({ ...f, measured_at: e.target.value }))
              }
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
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
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            >
              <option value="">— Sin registrar —</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  {BODY_CONDITION_LABELS[n]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Observaciones
            </label>
            <input
              type="text"
              value={form.observations ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, observations: e.target.value }))
              }
              placeholder="Opcional"
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          {formError && (
            <p className="col-span-full text-sm text-red-500">{formError}</p>
          )}

          <div className="col-span-full flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-primary px-6 py-2 text-sm font-medium text-white hover:bg-primary/90 disabled:opacity-50"
            >
              {saving ? "Guardando…" : "Guardar pesaje"}
            </button>
          </div>
        </form>
      )}

      {/* Tabla de historial */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
      {error && (
        <p className="py-4 text-center text-sm text-red-500">{error}</p>
      )}
      {!loading && !error && weights.length === 0 && (
        <p className="py-6 text-center text-sm text-gray-400">
          Sin registros de pesaje. Registra el primero.
        </p>
      )}
      {!loading && !error && weights.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs font-semibold uppercase tracking-wide text-gray-400">
                <th className="pb-2 pr-4">Fecha</th>
                <th className="pb-2 pr-4">Peso (kg)</th>
                <th className="pb-2 pr-4">Ganancia diaria</th>
                <th className="pb-2 pr-4">Cond. corporal</th>
                <th className="pb-2 pr-4">Observaciones</th>
                <th className="pb-2" />
              </tr>
            </thead>
            <tbody>
              {[...weights].reverse().map((w) => (
                <tr
                  key={w.id}
                  className="border-b border-gray-50 last:border-0 hover:bg-gray-50"
                >
                  <td className="py-2 pr-4 font-medium text-gray-800 whitespace-nowrap">
                    {formatDate(w.measured_at)}
                  </td>
                  <td className="py-2 pr-4 text-gray-700">
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
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="py-2 pr-4 text-gray-600">
                    {w.body_condition !== null
                      ? BODY_CONDITION_LABELS[w.body_condition]
                      : <span className="text-gray-400">—</span>}
                  </td>
                  <td className="py-2 pr-4 text-gray-500">
                    {w.observations ?? <span className="text-gray-300">—</span>}
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
        </div>
      )}
    </div>
  );
}
