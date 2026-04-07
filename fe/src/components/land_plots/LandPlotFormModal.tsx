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

export default function LandPlotFormModal({ farmId, existing, onSuccess, onClose }: Props) {
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

  const set = (key: keyof LandPlotRequest, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(msg ?? "No se pudo guardar el lote");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">
            {existing ? "Editar lote" : "Nuevo lote"}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Nombre del lote</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Área</label>
              <input
                type="number"
                min={0.01}
                step={0.01}
                value={form.area}
                onChange={(e) => set("area", parseFloat(e.target.value))}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Unidad</label>
              <select
                value={form.area_unit}
                onChange={(e) => set("area_unit", e.target.value)}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              >
                {AREA_UNITS.map((u) => <option key={u} value={u}>{u}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Tipo de uso</label>
            <select
              value={form.usage_type}
              onChange={(e) => set("usage_type", e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              required
            >
              <option value="">Seleccionar...</option>
              {USAGE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Capacidad máxima (animales)</label>
            <input
              type="number"
              min={1}
              value={form.max_capacity}
              onChange={(e) => set("max_capacity", parseInt(e.target.value))}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Ubicación (opcional)</label>
            <input
              type="text"
              value={form.location ?? ""}
              onChange={(e) => set("location", e.target.value || "")}
              placeholder="Ej: Sector norte, coordenadas, referencia"
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50">
              Cancelar
            </button>
            <button type="submit" disabled={loading}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60">
              {loading ? "Guardando..." : existing ? "Guardar cambios" : "Crear lote"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
