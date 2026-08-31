import { useState, useEffect } from "react";
import { getApiErrorMessage } from "../../api/errors";
import {
  createFood,
  updateFood,
  type FoodCreate,
  type FoodResponse,
} from "../../api/food";

interface Props {
  farmId: string;
  isOpen: boolean;
  existing?: FoodResponse;
  onSuccess: () => void;
  onClose: () => void;
}

const CATEGORIES = ["concentrado", "forraje", "vitaminas", "suplementos", "medicamentos"];
const UNITS = ["kg", "litros", "bolsas", "metros", "unidades"];
const STEPS = [
  { label: "Info básica" },
  { label: "Stock y precio" },
  { label: "Vencimiento" },
];

export default function FoodFormModal({
  farmId,
  isOpen,
  existing,
  onSuccess,
  onClose,
}: Props) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<FoodCreate>({
    name: existing?.name ?? "",
    category: existing?.category ?? "concentrado",
    unit_of_measure: existing?.unit_of_measure ?? "kg",
    current_stock: existing?.current_stock ?? 0,
    min_stock_alert: existing?.min_stock_alert ?? null,
    cost_per_unit: existing?.cost_per_unit ?? null,
    expiration_date: existing?.expiration_date ?? null,
    supplier: existing?.supplier ?? null,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const validateStep = (s: number): boolean => {
    if (s === 0 && !form.name.trim()) { setError("El nombre es obligatorio"); return false; }
    setError("");
    return true;
  };
  const nextStep = () => { if (validateStep(step)) setStep((s) => Math.min(s + 1, STEPS.length - 1)); };
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const isFormComplete =
    form.name.trim() !== "" &&
    form.current_stock >= 0;

  // 🔄 RE-INICIALIZAR FORMULARIO AL CAMBIAR DE ALIMENTO
  // Esto asegura que si pasas de editar un alimento a crear uno nuevo, los campos se limpien
  useEffect(() => {
    setForm({
      name: existing?.name ?? "",
      category: existing?.category ?? "concentrado",
      unit_of_measure: existing?.unit_of_measure ?? "kg",
      current_stock: existing?.current_stock ?? 0,
      min_stock_alert: existing?.min_stock_alert ?? null,
      cost_per_unit: existing?.cost_per_unit ?? null,
      expiration_date: existing?.expiration_date ?? null,
      supplier: existing?.supplier ?? null,
    });
    setError("");
  }, [existing, isOpen]);

  const set = <K extends keyof FoodCreate>(key: K, value: FoodCreate[K]) => {
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
        await updateFood(farmId, existing.id, form);
      } else {
        await createFood(farmId, form);
      }
      onSuccess();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo guardar el alimento"));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">
            {existing ? "Editar alimento" : "Registrar alimento"}
          </h2>
          <button
            onClick={onClose}
            className="text-text-muted hover:text-text-secondary text-xl leading-none"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
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
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Nombre *</label>
                  <input type="text" maxLength={100} value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Ej: Concentrado Premium"
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                  <span className="mt-0.5 block text-right text-xs text-text-muted">{form.name.length}/100</span>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Categoría *</label>
                  <select value={form.category} onChange={(e) => set("category", e.target.value)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required>
                    {CATEGORIES.map((cat) => (<option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>))}
                  </select>
                </div>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Unidad *</label>
                <select value={form.unit_of_measure} onChange={(e) => set("unit_of_measure", e.target.value)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required>
                  {UNITS.map((unit) => (<option key={unit} value={unit}>{unit.charAt(0).toUpperCase() + unit.slice(1)}</option>))}
                </select>
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Stock actual *</label>
                <input type="number" step="0.01" value={form.current_stock} onChange={(e) => set("current_stock", parseFloat(e.target.value) || 0)}
                  placeholder="0" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Stock mínimo</label>
                  <input type="number" step="0.01" value={form.min_stock_alert ?? ""} onChange={(e) => set("min_stock_alert", e.target.value ? parseFloat(e.target.value) : null)}
                    placeholder="Ej: 20" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Precio unitario ($)</label>
                  <input type="number" step="0.01" value={form.cost_per_unit ?? ""} onChange={(e) => set("cost_per_unit", e.target.value ? parseFloat(e.target.value) : null)}
                    placeholder="Ej: 5000" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Vencimiento</label>
                  <input type="date" value={form.expiration_date ?? ""} onChange={(e) => set("expiration_date", e.target.value || null)}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-text-secondary">Proveedor</label>
                  <input type="text" maxLength={200} value={form.supplier ?? ""} onChange={(e) => set("supplier", e.target.value || null)}
                    placeholder="Ej: Distribuidora XYZ" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                  <span className="mt-0.5 block text-right text-xs text-text-muted">{(form.supplier ?? "").length}/200</span>
                </div>
              </div>
            </>
          )}

          <div className="flex gap-2 pt-2">
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
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />}
                {loading ? "Guardando..." : existing ? "Actualizar" : "Crear alimento"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
