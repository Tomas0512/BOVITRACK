import { useState } from "react";
import { createLandPlot, updateLandPlot, type LandPlotRequest, type LandPlotResponse } from "../../api/land_plots";

interface Props {
  farmId: string;
  existing?: LandPlotResponse;
  onSuccess: () => void;
  onClose: () => void;
}

const USAGE_TYPES = ["pastoreo", "cultivo", "reserva", "infraestructura", "otro"];
const AREA_UNITS = ["hectareas", "metros2", "fanegadas"];

const STEPS = [
  { label: "Información básica" },
  { label: "Tipo y capacidad" },
];

export default function LandPlotFormModal({ farmId, existing, onSuccess, onClose }: Props) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<LandPlotRequest>({
    name: existing?.name ?? "",
    area: existing?.area ?? 0,
    area_unit: existing?.area_unit ?? "hectareas",
    usage_type: existing?.usage_type ?? "",
    max_capacity: existing?.max_capacity ?? 1,
    location: existing?.location ?? "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const validateStep = (s: number): boolean => {
    if (s === 0 && (!form.name.trim() || form.area <= 0)) {
      setError("Nombre y área son obligatorios");
      return false;
    }
    setError("");
    return true;
  };
  const nextStep = () => { if (validateStep(step)) setStep((s) => Math.min(s + 1, STEPS.length - 1)); };
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const isFormComplete =
    form.name.trim() !== "" && form.area > 0 && form.max_capacity >= 1;

  const set = (key: keyof LandPlotRequest, value: string | number) => {
    setForm((f) => ({ ...f, [key]: value }));
    if (error) setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError("");
    try {
      if (existing) {
        await updateLandPlot(farmId, existing.id, form);
      } else {
        await createLandPlot(farmId, form);
      }
      onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error && err.message ? err.message : "No se pudo guardar el lote");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">
            {existing ? "Editar lote" : "Nuevo lote"}
          </h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary text-xl leading-none">×</button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
        )}

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

        <form onSubmit={handleSubmit} className="space-y-4"
          onKeyDown={(e) => {
            if (e.key === "Enter" && step < STEPS.length - 1) {
              e.preventDefault();
              nextStep();
            }
          }}>
          {step === 0 && (
            <>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Nombre del lote</label>
                <input type="text" maxLength={100} value={form.name} onChange={(e) => set("name", e.target.value)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                <span className="mt-0.5 block text-right text-xs text-text-muted">{form.name.length}/100</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Área</label>
                  <input type="number" min={0.01} step={0.01} value={form.area} onChange={(e) => set("area", parseFloat(e.target.value) || 0)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Unidad</label>
                  <select value={form.area_unit} onChange={(e) => set("area_unit", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {AREA_UNITS.map((u) => <option key={u} value={u}>{u}</option>)}
                  </select>
                </div>
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Tipo de uso</label>
                <select value={form.usage_type} onChange={(e) => set("usage_type", e.target.value)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required>
                  <option value="">Seleccionar...</option>
                  {USAGE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Capacidad máxima (animales)</label>
                <input type="number" min={1} value={form.max_capacity} onChange={(e) => set("max_capacity", parseInt(e.target.value) || 1)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Ubicación (opcional)</label>
                <input type="text" value={form.location ?? ""} onChange={(e) => set("location", e.target.value || "")}
                  placeholder="Ej: Sector norte, coordenadas, referencia"
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
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
                {loading ? "Guardando..." : existing ? "Guardar cambios" : "Crear lote"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
