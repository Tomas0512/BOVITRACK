import { useState, useEffect } from "react";
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

const CATEGORIES = [
  "concentrado",
  "forraje",
  "vitaminas",
  "suplementos",
  "medicamentos",
];
const UNITS = ["kg", "litros", "bolsas", "metros", "unidades"];

export default function FoodFormModal({
  farmId,
  isOpen, // 👈 Ya desestructuramos la prop que causaba el error de compilación
  existing,
  onSuccess,
  onClose,
}: Props) {
  // ─── CONTROL DE VISIBILIDAD ───
  // Si no está abierto, detenemos el renderizado aquí. Evita renderizar HTML innecesario.
  if (!isOpen) return null;

  // ─── ESTADO DEL FORMULARIO ───
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

  const set = <K extends keyof FoodCreate>(key: K, value: FoodCreate[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail
          : undefined;
      setError(msg ?? "No se pudo guardar el alimento");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 overflow-y-auto py-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl mx-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">
            {existing ? "Editar alimento" : "Registrar alimento"}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Nombre *
              </label>
              <input
                type="text" maxLength={100}
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
                placeholder="Ej: Concentrado Premium"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                required
              />
              <span className="mt-0.5 block text-right text-xs text-gray-400">{form.name.length}/100</span>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Categoría *
              </label>
              <select
                value={form.category}
                onChange={(e) => set("category", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                required
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Unidad *
              </label>
              <select
                value={form.unit_of_measure}
                onChange={(e) => set("unit_of_measure", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                required
              >
                {UNITS.map((unit) => (
                  <option key={unit} value={unit}>
                    {unit.charAt(0).toUpperCase() + unit.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Stock actual *
              </label>
              <input
                type="number"
                step="0.01"
                value={form.current_stock}
                onChange={(e) =>
                  set("current_stock", parseFloat(e.target.value) || 0)
                }
                placeholder="0"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Stock mínimo
              </label>
              <input
                type="number"
                step="0.01"
                value={form.min_stock_alert ?? ""}
                onChange={(e) =>
                  set(
                    "min_stock_alert",
                    e.target.value ? parseFloat(e.target.value) : null
                  )
                }
                placeholder="Ej: 20"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Precio unitario ($)
              </label>
              <input
                type="number"
                step="0.01"
                value={form.cost_per_unit ?? ""}
                onChange={(e) =>
                  set(
                    "cost_per_unit",
                    e.target.value ? parseFloat(e.target.value) : null
                  )
                }
                placeholder="Ej: 5000"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Vencimiento
              </label>
              <input
                type="date"
                value={form.expiration_date ?? ""}
                onChange={(e) =>
                  set("expiration_date", e.target.value || null)
                }
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Proveedor
              </label>
              <input
                type="text" maxLength={200}
                value={form.supplier ?? ""}
                onChange={(e) =>
                  set("supplier", e.target.value || null)
                }
                placeholder="Ej: Distribuidora XYZ"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
              <span className="mt-0.5 block text-right text-xs text-gray-400">{(form.supplier ?? "").length}/200</span>
            </div>
          </div>

          <div className="mt-4 flex gap-2 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={!isFormComplete || loading}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading && (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              )}
              {loading
                ? "Guardando..."
                : existing
                  ? "Actualizar"
                  : "Crear alimento"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
