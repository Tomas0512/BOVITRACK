import { useState } from "react";
import { createPaddock, updatePaddock, type PaddockRequest, type PaddockResponse } from "../../api/paddocks";

interface Props {
  farmId: string;
  existing?: PaddockResponse;
  onSuccess: () => void;
  onClose: () => void;
}

const COVERAGE_OPTIONS = ["bueno", "regular", "malo"];
const STATUS_OPTIONS = ["libre", "ocupado", "en_descanso"];
const PASTURE_TYPES = ["kikuyo", "brachiaria", "estrella", "guinea", "pasto_corte", "mixto", "otro"];

export default function PaddockFormModal({ farmId, existing, onSuccess, onClose }: Props) {
  const [form, setForm] = useState<PaddockRequest>({
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

  const isFormComplete =
    form.name.trim() !== "" && form.area_hectares > 0 && form.max_capacity >= 1;

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
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(msg ?? "No se pudo guardar el potrero");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-text-primary">{existing ? "Editar potrero" : "Nuevo potrero"}</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-secondary text-xl leading-none">×</button>
        </div>

        {error && <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">Nombre del potrero</label>
            <input type="text" value={form.name} maxLength={100}
              onChange={(e) => set("name", e.target.value)}
              className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            <span className="mt-0.5 block text-right text-xs text-text-muted">{form.name.length}/100</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Área (ha)</label>
              <input type="number" min={0.01} step={0.01} value={form.area_hectares}
                onChange={(e) => set("area_hectares", parseFloat(e.target.value))}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Cap. máx. animales</label>
              <input type="number" min={1} value={form.max_capacity}
                onChange={(e) => set("max_capacity", parseInt(e.target.value))}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
            </div>
          </div>

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
                <input type="date" value={form.rest_start_date ?? ""}
                  onChange={(e) => set("rest_start_date", e.target.value || null)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Fin descanso</label>
                <input type="date" value={form.rest_end_date ?? ""}
                  onChange={(e) => set("rest_end_date", e.target.value || null)}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
              Cancelar
            </button>
            <button type="submit" disabled={!isFormComplete || loading}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? "Guardando..." : existing ? "Guardar cambios" : "Crear potrero"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
