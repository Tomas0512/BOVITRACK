import { useEffect, useState } from "react";
import { createPaddock, updatePaddock, type PaddockRequest, type PaddockResponse } from "../../api/paddocks";
import { listLandPlots, type LandPlotResponse } from "../../api/land_plots";
import { getApiErrorMessage } from "../../api/errors";

interface Props {
  farmId: string;
  existing?: PaddockResponse;
  onSuccess: () => void;
  onClose: () => void;
}

const COVERAGE_OPTIONS = ["bueno", "regular", "malo"];
const STATUS_OPTIONS = ["libre", "ocupado", "en_descanso"];
const PASTURE_TYPES = ["kikuyo", "brachiaria", "estrella", "guinea", "pasto_corte", "mixto", "otro"];

const STEPS = [
  { label: "Información básica" },
  { label: "Tipo y estado" },
];

export default function PaddockFormModal({ farmId, existing, onSuccess, onClose }: Props) {
  const [step, setStep] = useState(0);
  // Un potrero pertenece siempre a un lote de la finca (finca > lote > potrero).
  const [landPlots, setLandPlots] = useState<LandPlotResponse[]>([]);
  const [form, setForm] = useState<PaddockRequest>({
    land_plot_id: existing?.land_plot_id ?? "",
    name: existing?.name ?? "",
    area_hectares: existing?.area_hectares ?? 0,
    max_capacity: existing?.max_capacity ?? 1,
    coverage_status: existing?.coverage_status ?? "bueno",
    pasture_type: existing?.pasture_type ?? "",
    status: existing?.status ?? "libre",
    rest_start_date: existing?.rest_start_date ?? null,
    rest_end_date: existing?.rest_end_date ?? null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listLandPlots(farmId, true)
      .then((data) => {
        setLandPlots(data);
        // Si solo hay un lote, se preselecciona para ahorrar un clic.
        setForm((f) => (f.land_plot_id === "" && data.length === 1 ? { ...f, land_plot_id: data[0].id } : f));
      })
      .catch(() => setError("No se pudieron cargar los lotes de la finca"));
  }, [farmId]);

  const validateStep = (s: number): boolean => {
    if (s === 0 && !form.land_plot_id) {
      setError("Seleccione el lote al que pertenece el potrero");
      return false;
    }
    if (s === 0 && (!form.name.trim() || form.area_hectares <= 0 || form.max_capacity < 1)) {
      setError("Nombre, área y capacidad máxima son obligatorios");
      return false;
    }
    setError("");
    return true;
  };
  const nextStep = () => { if (validateStep(step)) setStep((s) => Math.min(s + 1, STEPS.length - 1)); };
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const isFormComplete =
    form.land_plot_id !== "" && form.name.trim() !== "" && form.area_hectares > 0 && form.max_capacity >= 1;

  const set = <K extends keyof PaddockRequest>(key: K, value: PaddockRequest[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (existing) {
        await updatePaddock(farmId, existing.id, form);
      } else {
        await createPaddock(farmId, form);
      }
      onSuccess();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo guardar el potrero"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">{existing ? "Editar potrero" : "Nuevo potrero"}</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary text-xl leading-none">×</button>
        </div>

        {error && <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        {/* Step indicator */}
        <div className="mb-4 flex items-center gap-1.5">
          {STEPS.map((s, i) => (
            <button key={i} type="button" onClick={() => { if (i < step) setStep(i); }} disabled={i > step}
              className={`flex-1 rounded-lg px-2 py-1.5 text-center text-xs font-semibold transition-colors ${i === step ? "bg-primary text-white" : i < step ? "bg-green-100 text-green-700" : "bg-surface-alt text-text-muted cursor-default"}`}
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
                <label className="mb-1 block text-sm font-medium text-text-secondary">Lote al que pertenece</label>
                <select
                  value={form.land_plot_id}
                  onChange={(e) => set("land_plot_id", e.target.value)}
                  className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
                  required
                >
                  <option value="">Seleccione un lote…</option>
                  {landPlots.map((lp) => (
                    <option key={lp.id} value={lp.id}>{lp.name}</option>
                  ))}
                </select>
                {landPlots.length === 0 && (
                  <span className="mt-0.5 block text-xs text-amber-600">
                    Esta finca no tiene lotes. Cree un lote antes de registrar potreros.
                  </span>
                )}
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Nombre del potrero</label>
                <input type="text" value={form.name} maxLength={100} onChange={(e) => set("name", e.target.value)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                <span className="mt-0.5 block text-right text-xs text-text-muted">{form.name.length}/100</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Área (ha)</label>
                  <input type="number" min={0.01} step={0.01} value={form.area_hectares} onChange={(e) => set("area_hectares", parseFloat(e.target.value))}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Cap. máx. animales</label>
                  <input type="number" min={1} value={form.max_capacity} onChange={(e) => set("max_capacity", parseInt(e.target.value))}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Cobertura</label>
                  <select value={form.coverage_status} onChange={(e) => set("coverage_status", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {COVERAGE_OPTIONS.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Estado</label>
                  <select value={form.status} onChange={(e) => set("status", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {STATUS_OPTIONS.map((o) => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Tipo de pasto</label>
                <select value={form.pasture_type ?? ""} onChange={(e) => set("pasture_type", e.target.value || null)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                  <option value="">Sin especificar</option>
                  {PASTURE_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
                </select>
              </div>
              {form.status === "en_descanso" && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-text-secondary">Inicio descanso</label>
                    <input type="date" value={form.rest_start_date ?? ""} onChange={(e) => set("rest_start_date", e.target.value || null)}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm font-medium text-text-secondary">Fin descanso</label>
                    <input type="date" value={form.rest_end_date ?? ""} onChange={(e) => set("rest_end_date", e.target.value || null)}
                      className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                  </div>
                </div>
              )}
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
              <button key="paso-siguiente" type="button" onClick={nextStep}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
                Siguiente →
              </button>
            ) : (
              <button key="paso-enviar" type="submit" disabled={!isFormComplete || loading}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed">
                {loading ? "Guardando..." : existing ? "Guardar cambios" : "Crear potrero"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
