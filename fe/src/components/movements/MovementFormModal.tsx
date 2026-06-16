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

export default function MovementFormModal({ farmId, existing, onSuccess, onClose }: Props) {
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">{isEdit ? "Editar movimiento" : "Registrar movimiento"}</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"><X size={20} /></button>
        </div>

        {error && <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Tipo de movimiento *</label>
            <select
              value={form.movement_type}
              onChange={(e) => setForm({ ...form, movement_type: e.target.value })}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            >
              {MOVEMENT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Fecha del movimiento *</label>
            <input
              type="date"
              value={form.movement_date}
              onChange={(e) => setForm({ ...form, movement_date: e.target.value })}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">ID del bovino</label>
            <input
              type="text"
              value={form.bovine_id ?? ""}
              onChange={(e) => setForm({ ...form, bovine_id: e.target.value || null })}
              placeholder="UUID del bovino (opcional)"
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">Valor ($)</label>
              <input
                type="number"
                min={0}
                step={0.01}
                value={form.price ?? ""}
                onChange={(e) => setForm({ ...form, price: e.target.value ? parseFloat(e.target.value) : null })}
                placeholder="0.00"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">Contraparte</label>
              <input
                type="text"
                value={form.counterparty_name ?? ""}
                onChange={(e) => setForm({ ...form, counterparty_name: e.target.value || null })}
                placeholder="Nombre del comprador/vendedor"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">Documento contraparte</label>
              <input
                type="text"
                value={form.counterparty_document ?? ""}
                onChange={(e) => setForm({ ...form, counterparty_document: e.target.value || null })}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">Teléfono contraparte</label>
              <input
                type="text"
                value={form.counterparty_phone ?? ""}
                onChange={(e) => setForm({ ...form, counterparty_phone: e.target.value || null })}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">Finca origen</label>
              <input
                type="text"
                value={form.origin_farm_name ?? ""}
                onChange={(e) => setForm({ ...form, origin_farm_name: e.target.value || null })}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600">Finca destino</label>
              <input
                type="text"
                value={form.destination_farm_name ?? ""}
                onChange={(e) => setForm({ ...form, destination_farm_name: e.target.value || null })}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Motivo</label>
            <textarea
              value={form.reason ?? ""}
              onChange={(e) => setForm({ ...form, reason: e.target.value || null })}
              rows={2}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">Observaciones</label>
            <textarea
              value={form.observations ?? ""}
              onChange={(e) => setForm({ ...form, observations: e.target.value || null })}
              rows={2}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
              {loading ? "Guardando..." : isEdit ? "Actualizar" : "Registrar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
