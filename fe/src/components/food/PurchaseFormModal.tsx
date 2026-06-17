import { useState, useEffect } from "react";
import { recordPurchase, type FoodResponse, type PurchaseCreate } from "../../api/food";

interface Props {
  farmId: string;
  foods: FoodResponse[];
  isOpen: boolean;
  onSuccess: () => void;
  onClose: () => void;
}

export default function PurchaseFormModal({
  farmId,
  foods,
  isOpen,
  onSuccess,
  onClose,
}: Props) {
  if (!isOpen) return null;

  const [form, setForm] = useState<PurchaseCreate>({
    food_id: foods.length > 0 ? foods[0].id : "",
    quantity: 0,
    unit_cost: 0,
    movement_date: new Date().toISOString().slice(0, 16),
    notes: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      setForm({
        food_id: foods.length > 0 ? foods[0].id : "",
        quantity: 0,
        unit_cost: 0,
        movement_date: new Date().toISOString().slice(0, 16),
        notes: "",
      });
      setError("");
    }
  }, [isOpen, foods]);

  const selectedFood = foods.find((f) => f.id === form.food_id);
  const totalCost = form.quantity * form.unit_cost;

  const isFormValid =
    form.food_id &&
    form.quantity > 0 &&
    form.unit_cost >= 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await recordPurchase(farmId, form);
      onSuccess();
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(msg ?? "Could not record purchase");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">Register Purchase</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary text-xl leading-none">&times;</button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Food Item *</label>
            <select
              value={form.food_id}
              onChange={(e) => setForm((f) => ({ ...f, food_id: e.target.value }))}
              className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              required
            >
              <option value="">Select food...</option>
              {foods.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name} ({f.current_stock} {f.unit_of_measure} in stock)
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Quantity *</label>
              <input
                type="number" step="0.01" min="0.01"
                value={form.quantity || ""}
                onChange={(e) => setForm((f) => ({ ...f, quantity: parseFloat(e.target.value) || 0 }))}
                placeholder="e.g. 100"
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Unit Cost ($) *</label>
              <input
                type="number" step="1" min="0"
                value={form.unit_cost || ""}
                onChange={(e) => setForm((f) => ({ ...f, unit_cost: parseFloat(e.target.value) || 0 }))}
                placeholder="e.g. 5000"
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
                required
              />
            </div>
          </div>

          {totalCost > 0 && (
            <div className="rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700">
              Total cost: <strong>${totalCost.toLocaleString("es-CO")}</strong>
              {selectedFood && (
                <> &middot; Stock after: <strong>{selectedFood.current_stock + form.quantity} {selectedFood.unit_of_measure}</strong></>
              )}
            </div>
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Date & Time</label>
            <input
              type="datetime-local"
              value={form.movement_date ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, movement_date: e.target.value || null }))}
              className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Notes (optional)</label>
            <textarea
              value={form.notes ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value || null }))}
              placeholder="e.g. Purchase from Distribuidora XYZ, invoice #123"
              className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              rows={2}
            />
          </div>

          <div className="mt-4 flex gap-2 justify-end">
            <button type="button" onClick={onClose} className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
              Cancel
            </button>
            <button type="submit" disabled={!isFormValid || loading}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
              {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />}
              {loading ? "Saving..." : "Register Purchase"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
