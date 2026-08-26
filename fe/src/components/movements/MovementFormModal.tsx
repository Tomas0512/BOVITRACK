import { useState } from "react";
import { X } from "lucide-react";
import { createMovement, updateMovement, type MovementRequest, type MovementResponse } from "../../api/movements";

const MOVEMENT_TYPES = [
  { value: "compra", label: "Compra" },
  { value: "venta", label: "Venta" },
  { value: "traslado", label: "Traslado" },
  { value: "nacimiento", label: "Nacimiento" },
  { value: "muerte", label: "Muerte" },
];

interface Props {
  farmId: string;
  existing?: MovementResponse | null;
  onSuccess: () => void;
  onClose: () => void;
}

const STEPS = [
  { label: "Tipo y fecha" },
  { label: "Contraparte" },
  { label: "Origen y notas" },
];

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export default function MovementFormModal({ farmId, existing, onSuccess, onClose }: Props) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<MovementRequest>({
    bovine_id: existing?.bovine_id ?? null,
    movement_type: existing?.movement_type ?? "compra",
    movement_date: existing?.movement_date ?? new Date().toISOString().slice(0, 10),
    price: existing?.price ?? null,
    counterparty_name: existing?.counterparty_name ?? null,
    counterparty_document: existing?.counterparty_document ?? null,
    counterparty_phone: existing?.counterparty_phone ?? null,
    origin_farm_name: existing?.origin_farm_name ?? null,
    destination_farm_name: existing?.destination_farm_name ?? null,
    reason: existing?.reason ?? null,
    observations: existing?.observations ?? null,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isEdit = !!existing;

  const validateStep = (s: number): boolean => {
    if (s === 0 && !form.movement_date) { setError("La fecha del movimiento es obligatoria"); return false; }
    if (s === 0 && form.bovine_id && !UUID_RE.test(form.bovine_id)) {
      setError("El ID del bovino no tiene un formato UUID válido");
      return false;
    }
    setError("");
    return true;
  };

  const nextStep = () => {
    if (validateStep(step)) setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setError("");
    try {
      const payload: MovementRequest = {
        ...form,
        price: form.price ?? null,
      };
      if (isEdit) {
        await updateMovement(farmId, existing!.id, payload);
      } else {
        await createMovement(farmId, payload);
      }
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar movimiento");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">{isEdit ? "Editar movimiento" : "Registrar movimiento"}</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary"><X size={20} /></button>
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
                <label className="mb-1 block text-xs font-medium text-text-secondary">Tipo de movimiento *</label>
                <select value={form.movement_type} onChange={(e) => setForm({ ...form, movement_type: e.target.value })}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                  {MOVEMENT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Fecha del movimiento *</label>
                <input type="date" value={form.movement_date} onChange={(e) => { setForm({ ...form, movement_date: e.target.value }); setError(""); }}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">ID del bovino</label>
                <input type="text" value={form.bovine_id ?? ""} onChange={(e) => { setForm({ ...form, bovine_id: e.target.value || null }); setError(""); }}
                  placeholder="UUID del bovino (opcional)"
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
            </>
          )}

          {step === 1 && (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Valor ($)</label>
                  <input type="number" min={0} step={0.01} value={form.price ?? ""}
                    onChange={(e) => setForm({ ...form, price: e.target.value ? parseFloat(e.target.value) : null })}
                    placeholder="0.00" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Contraparte</label>
                  <input type="text" value={form.counterparty_name ?? ""}
                    onChange={(e) => setForm({ ...form, counterparty_name: e.target.value || null })}
                    placeholder="Nombre del comprador/vendedor"
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Documento contraparte</label>
                  <input type="text" value={form.counterparty_document ?? ""}
                    onChange={(e) => setForm({ ...form, counterparty_document: e.target.value || null })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Teléfono contraparte</label>
                  <input type="text" value={form.counterparty_phone ?? ""}
                    onChange={(e) => setForm({ ...form, counterparty_phone: e.target.value || null })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Finca origen</label>
                  <input type="text" value={form.origin_farm_name ?? ""}
                    onChange={(e) => setForm({ ...form, origin_farm_name: e.target.value || null })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Finca destino</label>
                  <input type="text" value={form.destination_farm_name ?? ""}
                    onChange={(e) => setForm({ ...form, destination_farm_name: e.target.value || null })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Motivo</label>
                <textarea value={form.reason ?? ""} onChange={(e) => setForm({ ...form, reason: e.target.value || null })}
                  rows={2} className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Observaciones</label>
                <textarea value={form.observations ?? ""} onChange={(e) => setForm({ ...form, observations: e.target.value || null })}
                  rows={2} className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
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
              <button type="button" onClick={nextStep}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
                Siguiente →
              </button>
            ) : (
              <button type="submit" disabled={loading}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
                {loading ? "Guardando..." : isEdit ? "Actualizar" : "Registrar"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
