import { useState } from "react";
import { X } from "lucide-react";
import {
  createMilkProduction,
  updateMilkProduction,
  type MilkProductionRequest,
  type MilkProductionResponse,
} from "../../api/milk_production";
import type { BovineResponse } from "../../api/bovines";
import type { LandPlotResponse } from "../../api/land_plots";
import { getApiErrorMessage } from "../../api/errors";

interface Props {
  farmId: string;
  bovines: BovineResponse[];
  landPlots: LandPlotResponse[];
  existing?: MilkProductionResponse;
  lockedBovineId?: string;
  onSuccess: () => void;
  onClose: () => void;
}

const MILKING_TYPE_LABELS: Record<string, string> = {
  manual: "Manual",
  mecanico: "Mecánico",
};

const SESSION_OPTIONS = [
  { value: "mañana", label: "Mañana" },
  { value: "tarde", label: "Tarde" },
  { value: "noche", label: "Noche" },
];

export default function MilkProductionFormModal({ farmId, bovines, landPlots, existing, lockedBovineId, onSuccess, onClose }: Props) {
  const [form, setForm] = useState<MilkProductionRequest>({
    bovine_id: existing?.bovine_id ?? lockedBovineId ?? null,
    land_plot_id: existing?.land_plot_id ?? null,
    milking_date: existing
      ? new Date(existing.milking_date).toISOString().slice(0, 16)
      : new Date().toISOString().slice(0, 16),
    quantity_liters: existing ? Number(existing.quantity_liters) : 0,
    milking_type: existing?.milking_type ?? "manual",
    milking_session: existing?.milking_session ?? "mañana",
    observations: existing?.observations ?? null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const activeBovines = bovines.filter((b) => b.is_active);
  const activePlots = landPlots.filter((lp) => lp.is_active);

  const set = <K extends keyof MilkProductionRequest>(key: K, value: MilkProductionRequest[K]) => {
    setForm((f) => ({ ...f, [key]: value }));
    if (error) setError("");
  };

  const isComplete =
    (form.bovine_id || form.land_plot_id) &&
    form.milking_date !== "" &&
    Number(form.quantity_liters) > 0 &&
    form.milking_type !== "";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || !isComplete) return;
    setLoading(true);
    setError("");
    const payload: MilkProductionRequest = {
      ...form,
      quantity_liters: Number(form.quantity_liters),
      bovine_id: form.bovine_id || null,
      land_plot_id: form.land_plot_id || null,
      observations: form.observations || null,
    };
    try {
      if (existing) {
        await updateMilkProduction(farmId, existing.id, payload);
      } else {
        await createMilkProduction(farmId, payload);
      }
      onSuccess();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo guardar el ordeño"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">{existing ? "Editar ordeño" : "Registrar ordeño"}</h2>
          <button onClick={onClose} aria-label="Cerrar" className="rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary"><X size={20} /></button>
        </div>

        {error && <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Fecha y hora *</label>
              <input type="datetime-local" value={form.milking_date} max={new Date().toISOString().slice(0, 16)}
                onChange={(e) => set("milking_date", e.target.value)}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Litros *</label>
              <input type="number" min={0.1} step={0.1} value={form.quantity_liters}
                onChange={(e) => set("quantity_liters", e.target.value ? parseFloat(e.target.value) : 0)}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Tipo de ordeño *</label>
              <select value={form.milking_type} onChange={(e) => set("milking_type", e.target.value)}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                {Object.entries(MILKING_TYPE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Sesión</label>
              <select value={form.milking_session ?? ""} onChange={(e) => set("milking_session", e.target.value || null)}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                <option value="">Sin especificar</option>
                {SESSION_OPTIONS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Bovino <span className="text-red-600">*</span></label>
            <select value={form.bovine_id ?? ""} onChange={(e) => set("bovine_id", e.target.value || null)}
              className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none disabled:bg-surface-alt disabled:text-text-muted"
              disabled={Boolean(lockedBovineId)}>
              <option value="">— Seleccionar bovino —</option>
              {activeBovines.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.identification_number} · {b.name ?? "Sin nombre"}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Lote</label>
            <select value={form.land_plot_id ?? ""} onChange={(e) => set("land_plot_id", e.target.value || null)}
              className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
              <option value="">Sin lote</option>
              {activePlots.map((lp) => (
                <option key={lp.id} value={lp.id}>{lp.name} ({lp.usage_type})</option>
              ))}
            </select>
            <span className="mt-0.5 block text-xs text-text-muted">
              Indica un bovino o un lote: el bovino tiene prioridad y es el más usado para el control individual.
            </span>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Observaciones</label>
            <textarea value={form.observations ?? ""} maxLength={500}
              onChange={(e) => set("observations", e.target.value)}
              rows={2} className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
            <span className="mt-0.5 block text-right text-xs text-text-muted">{(form.observations ?? "").length}/500</span>
          </div>

          <p className="text-xs text-text-muted">
            El bovino tiene prioridad sobre el lote: se recomienda registrar por animal para un control individual.
          </p>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
              Cancelar
            </button>
            <button type="submit" disabled={!isComplete || loading}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? "Guardando..." : existing ? "Guardar cambios" : "Registrar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}