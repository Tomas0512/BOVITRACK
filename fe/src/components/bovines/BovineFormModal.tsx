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

const STEPS = [
  { label: "Identificación" },
  { label: "Fechas y pesos" },
  { label: "Clasificación" },
];

export default function BovineFormModal({ farmId, landPlots, existing, onSuccess, onClose }: Props) {
  const [step, setStep] = useState(0);
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

  const validateStep = (s: number): boolean => {
    const newErrors: Record<string, string> = {};
    if (s === 0) {
      if (!form.identification_number.trim()) newErrors.id = "Obligatorio";
    }
    if (s === 1) {
      if (!form.birth_date) newErrors.birth = "Obligatorio";
      if (!form.entry_date) newErrors.entry = "Obligatorio";
    }
    setError(Object.values(newErrors).join(". "));
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(step)) setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const isFormComplete =
    form.identification_number.trim() !== "" &&
    form.birth_date !== "" &&
    form.entry_date !== "";

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
      <div className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">{existing ? "Editar bovino" : "Registrar bovino"}</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary text-xl leading-none">×</button>
        </div>

        {error && <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        {/* Step indicator */}
        <div className="mb-4 flex items-center gap-1.5">
          {STEPS.map((s, i) => (
            <button key={i} type="button" onClick={() => { if (i < step) setStep(i); }} disabled={i > step}
              className={`flex-1 rounded-lg px-2 py-1.5 text-center text-xs font-semibold transition-colors ${i === step ? "bg-primary text-white" : i < step ? "bg-green-100 text-green-700" : "bg-gray-100 text-text-muted cursor-default"}`}
            >
              {i < step ? "✓ " : ""}{s.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-3"
          onKeyDown={(e) => {
            if (e.key === "Enter" && step < STEPS.length - 1) {
              e.preventDefault();
              nextStep();
            }
          }}>
          {step === 0 && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">N° Identificación *</label>
                  <input type="text" value={form.identification_number} maxLength={50}
                    onChange={(e) => set("identification_number", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                  <span className="mt-0.5 block text-right text-xs text-text-muted">{form.identification_number.length}/50</span>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Nombre</label>
                  <input type="text" value={form.name ?? ""} maxLength={100}
                    onChange={(e) => set("name", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                  <span className="mt-0.5 block text-right text-xs text-text-muted">{(form.name ?? "").length}/100</span>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Sexo *</label>
                  <select value={form.sex} onChange={(e) => set("sex", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    <option value="macho">Macho</option>
                    <option value="hembra">Hembra</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Raza</label>
                  <input type="text" value={form.breed ?? ""} maxLength={50}
                    onChange={(e) => set("breed", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Color</label>
                <input type="text" value={form.color ?? ""} maxLength={50}
                  onChange={(e) => set("color", e.target.value)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Fecha nacimiento *</label>
                  <input type="date" value={form.birth_date} onChange={(e) => set("birth_date", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Peso nacimiento (kg)</label>
                  <input type="number" min={0} step={0.1} value={form.birth_weight ?? ""}
                    onChange={(e) => set("birth_weight", e.target.value ? parseFloat(e.target.value) : null)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Peso actual (kg)</label>
                  <input type="number" min={0} step={0.1} value={form.current_weight ?? ""}
                    onChange={(e) => set("current_weight", e.target.value ? parseFloat(e.target.value) : null)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Tipo de ingreso *</label>
                  <select value={form.entry_type} onChange={(e) => set("entry_type", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {ENTRY_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Fecha ingreso *</label>
                <input type="date" value={form.entry_date} onChange={(e) => set("entry_date", e.target.value)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Propósito</label>
                  <select value={form.purpose ?? ""} onChange={(e) => set("purpose", e.target.value || null)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    <option value="">Sin especificar</option>
                    {PURPOSES.map((p) => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Estado</label>
                  <select value={form.status} onChange={(e) => set("status", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Lote asignado</label>
                <select value={form.land_plot_id ?? ""} onChange={(e) => set("land_plot_id", e.target.value || null)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                  <option value="">Sin lote</option>
                  {landPlots.filter((lp) => lp.is_active).map((lp) => (
                    <option key={lp.id} value={lp.id}>{lp.name} ({lp.usage_type})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Observaciones</label>
                <textarea value={form.observations ?? ""} maxLength={500}
                  onChange={(e) => set("observations", e.target.value)}
                  rows={2} className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                <span className="mt-0.5 block text-right text-xs text-text-muted">{(form.observations ?? "").length}/500</span>
              </div>
            </>
          )}

          <div className="flex gap-3 pt-2">
            {step > 0 && (
              <button type="button" onClick={prevStep}
                className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
                ← Anterior
              </button>
            )}
            {step < STEPS.length - 1 ? (
              <button type="button" onClick={nextStep}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
                Siguiente →
              </button>
            ) : (
              <button type="submit" disabled={!isFormComplete || loading}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed">
                {loading ? "Guardando..." : existing ? "Guardar cambios" : "Registrar"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
