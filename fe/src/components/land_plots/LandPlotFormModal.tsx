import { useState } from "react";
import { X } from "lucide-react";
import { getApiErrorMessage } from "../../api/errors";
import {
  createLandPlot,
  updateLandPlot,
  type LandPlotRequest,
  type LandPlotResponse,
  type PaddockNested,
} from "../../api/land_plots";

interface Props {
  farmId: string;
  existing?: LandPlotResponse;
  onSuccess: () => void;
  onClose: () => void;
}

const USAGE_TYPES = ["pastoreo", "cultivo", "reserva", "infraestructura", "otro"];
const AREA_UNITS = ["hectareas", "metros2", "fanegadas"];

const COVERAGE_OPTIONS = ["bueno", "regular", "malo"];
const PASTURE_TYPES = ["kikuyo", "brachiaria", "estrella", "guinea", "pasto_corte", "mixto", "otro"];

const nuevoPotrero = (): PaddockNested => ({
  name: "",
  area_hectares: 0,
  max_capacity: 1,
  coverage_status: "bueno",
  pasture_type: "",
  status: "libre",
});

// Al editar un lote no se piden potreros: ya existen y se gestionan aparte.
const STEPS_CREAR = [
  { label: "Información básica" },
  { label: "Tipo y capacidad" },
  { label: "Potreros" },
];
const STEPS_EDITAR = STEPS_CREAR.slice(0, 2);

export default function LandPlotFormModal({ farmId, existing, onSuccess, onClose }: Props) {
  const STEPS = existing ? STEPS_EDITAR : STEPS_CREAR;
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<LandPlotRequest>({
    name: existing?.name ?? "",
    area: existing?.area ?? 0,
    area_unit: existing?.area_unit ?? "hectareas",
    usage_type: existing?.usage_type ?? "",
    max_capacity: existing?.max_capacity ?? 1,
    location: existing?.location ?? "",
    paddocks: existing ? [] : [nuevoPotrero()],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const potrerosValidos =
    form.paddocks.length > 0 &&
    form.paddocks.every((p) => p.name.trim() !== "" && p.area_hectares > 0 && p.max_capacity >= 1);

  const validateStep = (s: number): boolean => {
    if (s === 0 && (!form.name.trim() || form.area <= 0)) {
      setError("Nombre y área son obligatorios");
      return false;
    }
    if (s === 2 && !potrerosValidos) {
      setError("Cada potrero necesita nombre, área mayor a 0 y capacidad mínima de 1");
      return false;
    }
    setError("");
    return true;
  };
  const nextStep = () => { if (validateStep(step)) setStep((s) => Math.min(s + 1, STEPS.length - 1)); };
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const isFormComplete =
    form.name.trim() !== "" &&
    form.area > 0 &&
    form.max_capacity >= 1 &&
    (existing ? true : potrerosValidos);

  const set = (key: keyof LandPlotRequest, value: string | number) => {
    setForm((f) => ({ ...f, [key]: value }));
    if (error) setError("");
  };

  const setPotrero = <K extends keyof PaddockNested>(i: number, key: K, value: PaddockNested[K]) =>
    setForm((f) => ({
      ...f,
      paddocks: f.paddocks.map((p, idx) => (idx === i ? { ...p, [key]: value } : p)),
    }));

  const agregarPotrero = () =>
    setForm((f) => ({ ...f, paddocks: [...f.paddocks, nuevoPotrero()] }));

  // Nunca se permite quitar el último: el lote quedaría sin potreros.
  const quitarPotrero = (i: number) =>
    setForm((f) => ({ ...f, paddocks: f.paddocks.filter((_, idx) => idx !== i) }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError("");
    try {
      if (existing) {
        // Al editar no se tocan los potreros: se gestionan desde su propia sección.
        const { paddocks: _omitidos, ...soloLote } = form;
        void _omitidos;
        await updateLandPlot(farmId, existing.id, soloLote);
      } else {
        await createLandPlot(farmId, form);
      }
      onSuccess();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo guardar el lote"));
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
          <button onClick={onClose} aria-label="Cerrar" className="rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary"><X size={20} /></button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
        )}

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
                <label className="mb-1 block text-sm font-medium text-text-secondary">Nombre del lote <span className="text-red-600">*</span></label>
                <input type="text" maxLength={100} value={form.name} onChange={(e) => set("name", e.target.value)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                <span className="mt-0.5 block text-right text-xs text-text-muted">{form.name.length}/100</span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Área <span className="text-red-600">*</span></label>
                  <input type="number" min={0.01} step={0.01} value={form.area} onChange={(e) => set("area", parseFloat(e.target.value) || 0)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Unidad <span className="text-red-600">*</span></label>
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

          {step === 2 && !existing && (
            <>
              <p className="rounded-lg bg-surface-alt px-3 py-2 text-xs text-text-secondary">
                Todo lote debe tener al menos un potrero. Se crean junto con el lote,
                en una sola operación.
              </p>

              {form.paddocks.map((p, i) => (
                <div key={i} className="rounded-xl border border-border p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wide text-text-muted">
                      Potrero {i + 1}
                    </span>
                    {form.paddocks.length > 1 && (
                      <button
                        type="button"
                        onClick={() => quitarPotrero(i)}
                        className="rounded px-2 py-0.5 text-xs font-medium text-red-500 hover:bg-red-50"
                      >
                        Quitar
                      </button>
                    )}
                  </div>

                  <div className="space-y-2">
                    <input
                      type="text"
                      value={p.name}
                      maxLength={100}
                      placeholder="Nombre del potrero"
                      onChange={(e) => setPotrero(i, "name", e.target.value)}
                      className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none"
                    />
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="mb-1 block text-xs text-text-secondary">Área (ha)</label>
                        <input
                          type="number" min={0.01} step={0.01} value={p.area_hectares}
                          onChange={(e) => setPotrero(i, "area_hectares", parseFloat(e.target.value) || 0)}
                          className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs text-text-secondary">Cap. animales</label>
                        <input
                          type="number" min={1} value={p.max_capacity}
                          onChange={(e) => setPotrero(i, "max_capacity", parseInt(e.target.value) || 1)}
                          className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="mb-1 block text-xs text-text-secondary">Cobertura</label>
                        <select
                          value={p.coverage_status}
                          onChange={(e) => setPotrero(i, "coverage_status", e.target.value)}
                          className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
                        >
                          {COVERAGE_OPTIONS.map((c) => <option key={c} value={c}>{c}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="mb-1 block text-xs text-text-secondary">Tipo de pasto</label>
                        <select
                          value={p.pasture_type ?? ""}
                          onChange={(e) => setPotrero(i, "pasture_type", e.target.value || null)}
                          className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
                        >
                          <option value="">Sin especificar</option>
                          {PASTURE_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              <button
                type="button"
                onClick={agregarPotrero}
                className="w-full rounded-lg border border-dashed border-border py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
              >
                + Añadir otro potrero
              </button>

              <p className="text-right text-xs text-text-muted">
                {form.paddocks.length} potrero{form.paddocks.length !== 1 ? "s" : ""} ·{" "}
                {form.paddocks.reduce((s, p) => s + (Number(p.area_hectares) || 0), 0).toFixed(2)} ha en total
              </p>
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
                {loading ? "Guardando..." : existing ? "Guardar cambios" : "Crear lote"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
