import { useState } from "react";
import { createBovine, updateBovine, type BovineRequest, type BovineResponse } from "../../api/bovines";
import type { LandPlotResponse } from "../../api/land_plots";

interface Props {
  farmId: string;
  landPlots: LandPlotResponse[];
  existing?: BovineResponse;
  onSuccess: () => void;
  onClose: () => void;
}

const ENTRY_TYPES = ["nacimiento", "compra", "donacion", "traspaso"];
const PURPOSES = ["leche", "carne", "doble_proposito", "cria", "trabajo"];
const STATUSES = ["activo", "vendido", "muerto", "retirado"];

export default function BovineFormModal({ farmId, landPlots, existing, onSuccess, onClose }: Props) {
  const [form, setForm] = useState<BovineRequest>({
    identification_number: existing?.identification_number ?? "",
    name: existing?.name ?? "",
    sex: existing?.sex ?? "macho",
    breed: existing?.breed ?? "",
    color: existing?.color ?? "",
    birth_date: existing?.birth_date ?? "",
    birth_weight: existing?.birth_weight ?? null,
    current_weight: existing?.current_weight ?? null,
    purpose: existing?.purpose ?? "",
    status: existing?.status ?? "activo",
    entry_type: existing?.entry_type ?? "nacimiento",
    entry_date: existing?.entry_date ?? "",
    land_plot_id: existing?.land_plot_id ?? null,
    observations: existing?.observations ?? "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const set = <K extends keyof BovineRequest>(key: K, value: BovineRequest[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const payload = {
      ...form,
      name: form.name || null,
      breed: form.breed || null,
      color: form.color || null,
      purpose: form.purpose || null,
      observations: form.observations || null,
      land_plot_id: form.land_plot_id || null,
    };
    try {
      if (existing) {
        await updateBovine(farmId, existing.id, payload);
      } else {
        await createBovine(farmId, payload);
      }
      onSuccess();
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(msg ?? "No se pudo guardar el bovino");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">{existing ? "Editar bovino" : "Registrar bovino"}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        {error && <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">N° Identificación *</label>
              <input type="text" value={form.identification_number}
                onChange={(e) => set("identification_number", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Nombre</label>
              <input type="text" value={form.name ?? ""}
                onChange={(e) => set("name", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Sexo *</label>
              <select value={form.sex} onChange={(e) => set("sex", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none">
                <option value="macho">Macho</option>
                <option value="hembra">Hembra</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Raza</label>
              <input type="text" value={form.breed ?? ""} onChange={(e) => set("breed", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Fecha nacimiento *</label>
              <input type="date" value={form.birth_date} onChange={(e) => set("birth_date", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Color</label>
              <input type="text" value={form.color ?? ""} onChange={(e) => set("color", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Peso nacimiento (kg)</label>
              <input type="number" min={0} step={0.1} value={form.birth_weight ?? ""}
                onChange={(e) => set("birth_weight", e.target.value ? parseFloat(e.target.value) : null)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Peso actual (kg)</label>
              <input type="number" min={0} step={0.1} value={form.current_weight ?? ""}
                onChange={(e) => set("current_weight", e.target.value ? parseFloat(e.target.value) : null)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Tipo de ingreso *</label>
              <select value={form.entry_type} onChange={(e) => set("entry_type", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none">
                {ENTRY_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Fecha ingreso *</label>
              <input type="date" value={form.entry_date} onChange={(e) => set("entry_date", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Propósito</label>
              <select value={form.purpose ?? ""} onChange={(e) => set("purpose", e.target.value || null)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none">
                <option value="">Sin especificar</option>
                {PURPOSES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Estado</label>
              <select value={form.status} onChange={(e) => set("status", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none">
                {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Lote asignado</label>
            <select value={form.land_plot_id ?? ""} onChange={(e) => set("land_plot_id", e.target.value || null)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none">
              <option value="">Sin lote</option>
              {landPlots.filter((lp) => lp.is_active).map((lp) => (
                <option key={lp.id} value={lp.id}>{lp.name} ({lp.usage_type})</option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Observaciones</label>
            <textarea value={form.observations ?? ""} onChange={(e) => set("observations", e.target.value)}
              rows={2} className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none" />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
              {loading ? "Guardando..." : existing ? "Guardar cambios" : "Registrar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
