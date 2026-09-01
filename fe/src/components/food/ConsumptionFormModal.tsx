import { useEffect, useState } from "react";
import { X } from "lucide-react";
import {
  createConsumption,
  type ConsumptionCreate,
  type FoodResponse,
} from "../../api/food";
import type { LandPlotResponse } from "../../api/land_plots";
import type { PaddockResponse } from "../../api/paddocks";
import type { BovineResponse } from "../../api/bovines";
import { listLandPlots } from "../../api/land_plots";
import { listPaddocks } from "../../api/paddocks";
import { listBovines } from "../../api/bovines";
import { getApiErrorMessage } from "../../api/errors";

interface Props {
  farmId: string;
  foods: FoodResponse[];
  onSuccess: () => void;
  onClose: () => void;
}

export default function ConsumptionFormModal({ farmId, foods, onSuccess, onClose }: Props) {
  const [form, setForm] = useState<ConsumptionCreate>({
    food_id: "",
    quantity: 0,
    feeding_date: new Date().toISOString().slice(0, 10),
    land_plot_id: null,
    paddock_id: null,
    bovine_id: null,
    source_bag: "",
    observations: "",
  });
  const [landPlots, setLandPlots] = useState<LandPlotResponse[]>([]);
  const [paddocks, setPaddocks] = useState<PaddockResponse[]>([]);
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([listLandPlots(farmId, true), listPaddocks(farmId), listBovines(farmId)])
      .then(([lp, pd, bv]) => {
        if (!active) return;
        setLandPlots(lp);
        setPaddocks(pd);
        setBovines(bv);
      })
      .catch(() => {
        if (active) setError("No se pudieron cargar lotes, potreros o bovinos.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [farmId]);

  const isFormComplete =
    form.food_id !== "" &&
    form.quantity > 0 &&
    form.feeding_date !== "" &&
    Boolean(form.land_plot_id || form.paddock_id || form.bovine_id) &&
    (form.source_bag ?? "").trim() !== "";

  const set = <K extends keyof ConsumptionCreate>(key: K, value: ConsumptionCreate[K]) => {
    setForm((f) => ({ ...f, [key]: value }));
    if (error) setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || saving) return;
    setSaving(true);
    setError("");
    try {
      await createConsumption(farmId, {
        ...form,
        land_plot_id: form.land_plot_id || null,
        paddock_id: form.paddock_id || null,
        bovine_id: form.bovine_id || null,
        source_bag: form.source_bag || null,
        observations: form.observations || null,
      });
      onSuccess();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo registrar el consumo"));
    } finally {
      setSaving(false);
    }
  };

  const inputClass =
    "w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">Registrar consumo</h2>
          <button onClick={onClose} aria-label="Cerrar" className="rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary">
            <X size={20} />
          </button>
        </div>

        {error && <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-text-secondary">Alimento *</label>
              <select value={form.food_id} onChange={(e) => set("food_id", e.target.value)} className={inputClass} required>
                <option value="">Seleccione…</option>
                {foods.map((f) => (
                  <option key={f.id} value={f.id}>{f.name} (stock: {f.current_stock})</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-text-secondary">Cantidad *</label>
              <input type="number" min={0.01} step={0.01} value={form.quantity || ""}
                onChange={(e) => set("quantity", parseFloat(e.target.value) || 0)} className={inputClass} required />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-text-secondary">Fecha *</label>
            <input type="date" value={form.feeding_date} onChange={(e) => set("feeding_date", e.target.value)} className={inputClass} required />
          </div>

          <label className="mb-1 block text-xs font-medium text-text-secondary">Destino (lote / potrero / bovino) <span className="text-red-600">*</span></label>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <select value={form.land_plot_id ?? ""} onChange={(e) => set("land_plot_id", e.target.value || null)} className={inputClass} disabled={loading}>
                <option value="">Lote…</option>
                {landPlots.filter((p) => p.is_active).map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div>
              <select value={form.paddock_id ?? ""} onChange={(e) => set("paddock_id", e.target.value || null)} className={inputClass} disabled={loading}>
                <option value="">Potrero…</option>
                {paddocks.filter((p) => p.is_active).map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div>
              <select value={form.bovine_id ?? ""} onChange={(e) => set("bovine_id", e.target.value || null)} className={inputClass} disabled={loading}>
                <option value="">Bovino…</option>
                {bovines.map((b) => (
                  <option key={b.id} value={b.id}>{b.identification_number}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-text-secondary">Origen / Bulto <span className="text-red-600">*</span></label>
            <input type="text" maxLength={120} value={form.source_bag ?? ""} placeholder="Ej: Bulto #5, Lote de compra 2026-A" onChange={(e) => set("source_bag", e.target.value)} className={inputClass} required />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-text-secondary">Observaciones</label>
            <textarea value={form.observations ?? ""} rows={2} maxLength={500} onChange={(e) => set("observations", e.target.value)} className={inputClass} />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">Cancelar</button>
            <button type="submit" disabled={!isFormComplete || saving} className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
              {saving ? "Guardando…" : "Registrar consumo"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
