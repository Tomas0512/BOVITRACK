import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { createMovement, updateMovement, type MovementRequest, type MovementResponse } from "../../api/movements";
import { listBovines, type BovineResponse } from "../../api/bovines";

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

export default function MovementFormModal({ farmId, existing, onSuccess, onClose }: Props) {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState<MovementRequest>({
    bovine_id: existing?.bovine_id ?? null,
    animal_identifier: existing?.animal_identifier ?? null,
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
  const [bovines, setBovines] = useState<BovineResponse[]>([]);

  useEffect(() => {
    let active = true;
    listBovines(farmId)
      .then((data) => { if (active) setBovines(data); })
      .catch(() => { if (active) setError("No se pudieron cargar los bovinos."); });
    return () => { active = false; };
  }, [farmId]);

  const isEdit = !!existing;

  const EXISTING_TYPES = ["venta", "traslado", "muerte"];
  const NEW_ANIMAL_TYPES = ["compra", "nacimiento"];
  const needsExistingBovine = EXISTING_TYPES.includes(form.movement_type);
  const needsNewIdentifier = NEW_ANIMAL_TYPES.includes(form.movement_type);

  const isFormComplete =
    form.movement_date !== "" &&
    (form.movement_type === "traslado"
      ? (form.origin_farm_name ?? "").trim() !== "" && (form.destination_farm_name ?? "").trim() !== ""
      : (form.counterparty_name ?? "").trim() !== "") &&
    (needsExistingBovine ? Boolean(form.bovine_id) : true) &&
    (needsNewIdentifier ? (form.animal_identifier ?? "").trim() !== "" : true);

  const validateStep = (s: number): boolean => {
    if (s === 0 && !form.movement_date) { setError("La fecha del movimiento es obligatoria"); return false; }
    if (s === 0 && needsExistingBovine && !form.bovine_id) {
      setError("Seleccione el bovino (por su número de identificación)");
      return false;
    }
    if (s === 0 && needsNewIdentifier && (form.animal_identifier ?? "").trim() === "") {
      setError("Ingrese el identificador del animal nuevo");
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
    if ((form.price ?? 0) < 0) {
      setError("El precio no puede ser negativo");
      return;
    }
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
          <button onClick={onClose} aria-label="Cerrar" className="rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary"><X size={20} /></button>
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
                <label className="mb-1 block text-xs font-medium text-text-secondary">
                  Bovino (identificación) <span className="text-red-600">*</span>
                </label>
                {needsNewIdentifier ? (
                  <input type="text" maxLength={50} value={form.animal_identifier ?? ""}
                    onChange={(e) => { setForm({ ...form, animal_identifier: e.target.value || null }); setError(""); }}
                    placeholder="Identificador del animal nuevo" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                ) : (
                  <select value={form.bovine_id ?? ""} onChange={(e) => { setForm({ ...form, bovine_id: e.target.value || null }); setError(""); }}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                    disabled={bovines.length === 0}>
                    <option value="">Seleccione un bovino…</option>
                    {bovines.map((b) => (
                      <option key={b.id} value={b.id}>{b.identification_number}{b.name ? ` · ${b.name}` : ""}</option>
                    ))}
                  </select>
                )}
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
              <button key="paso-siguiente" type="button" onClick={nextStep}
                className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
                Siguiente →
              </button>
            ) : (
              <button key="paso-enviar" type="submit" disabled={!isFormComplete || loading}
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
