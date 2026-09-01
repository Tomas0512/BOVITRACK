import { useEffect, useState } from "react";
import { Syringe, Plus } from "lucide-react";
import { listTreatments, createTreatment, type TreatmentResponse } from "../../api/treatments";
import { listBovines, type BovineResponse } from "../../api/bovines";
import { getApiErrorMessage } from "../../api/errors";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";

interface Props {
  farmId: string;
}

const TYPE_LABELS: Record<string, string> = {
  vacunacion: "Vacunación",
  desparasitacion: "Desparasitación",
  antibiotico: "Antibiótico",
  antiparasitario: "Antiparasitario",
  vitamina: "Vitamina",
  cirugia: "Cirugía",
  otro: "Otro",
};

const ROUTE_LABELS: Record<string, string> = {
  oral: "Oral",
  intramuscular: "Intramuscular",
  subcutanea: "Subcutánea",
  intravenosa: "Intravenosa",
  topica: "Tópica",
};

const EMPTY_FORM = {
  bovine_id: "",
  treatment_type: "vacunacion",
  product_name: "",
  dose: "",
  administration_route: "intramuscular",
  application_date: new Date().toISOString().slice(0, 10),
  next_application_date: "",
  observations: "",
};

export default function FarmTreatments({ farmId }: Props) {
  const [treatments, setTreatments] = useState<TreatmentResponse[]>([]);
  const [bovines, setBovines] = useState<BovineResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const isFormComplete =
    form.bovine_id !== "" &&
    form.product_name.trim() !== "" &&
    form.dose.trim() !== "" &&
    form.application_date !== "";

  const getValue = (t: TreatmentResponse, key: string): string | number => {
    const v = (t as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { page, pageCount, start, end, total, paginated, setPage } =
    useTable<TreatmentResponse>(treatments, { getValue });

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [tr, bov] = await Promise.all([listTreatments(farmId), listBovines(farmId)]);
      setTreatments(tr);
      setBovines(bov);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudieron cargar los tratamientos"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setPage(1); }, [farmId, setPage]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { load(); }, [farmId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.bovine_id || !form.product_name.trim() || !form.dose.trim()) {
      setError("Selecciona un animal y completa producto y dosis");
      return;
    }
    if (form.next_application_date && form.application_date && form.next_application_date < form.application_date) {
      setError("La próxima aplicación no puede ser anterior a la fecha de aplicación");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await createTreatment(farmId, {
        bovine_id: form.bovine_id || null,
        treatment_type: form.treatment_type,
        product_name: form.product_name.trim(),
        dose: form.dose.trim(),
        administration_route: form.administration_route,
        application_date: form.application_date,
        next_application_date: form.next_application_date || null,
        observations: form.observations || null,
      });
      setShowModal(false);
      setForm(EMPTY_FORM);
      await load();
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo registrar el tratamiento"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-text-primary">
            <Syringe size={18} className="mr-1.5 inline-block align-text-bottom text-primary" />
            Tratamientos aplicados
          </h2>
          <p className="text-xs text-text-muted">
            Registra los procedimientos (vacunas, desparasitaciones, etc.) aplicados a los animales
          </p>
        </div>
        <button onClick={() => { setShowModal(true); setError(""); }}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
          <Plus size={16} className="mr-1 inline-block -mt-0.5" /> Registrar tratamiento
        </button>
      </div>

      {error && (
        <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : treatments.length === 0 ? (
        <p className="py-8 text-center text-sm text-text-muted">Sin tratamientos registrados.</p>
      ) : (
        <div className="space-y-3">
          {paginated.map((t) => (
            <div key={t.id} className="rounded-xl border border-border bg-surface p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-text-primary">
                    {TYPE_LABELS[t.treatment_type] ?? t.treatment_type}: {t.product_name}
                  </p>
                  <p className="text-xs text-text-muted">
                    {new Date(t.application_date).toLocaleDateString("es-CO")}
                  </p>
                  <p className="mt-1 text-sm text-text-secondary">
                    Dosis: <span className="font-medium">{t.dose}</span> · Vía:{" "}
                    <span className="font-medium">{ROUTE_LABELS[t.administration_route] ?? t.administration_route}</span>
                  </p>
                  {t.observations && (
                    <p className="mt-1 text-xs text-text-muted">{t.observations}</p>
                  )}
                </div>
                {t.next_application_date && (
                  <div className="shrink-0 text-right text-xs text-text-muted">
                    <p>Próx. aplicación</p>
                    <p className="font-medium text-text-secondary">
                      {new Date(t.next_application_date).toLocaleDateString("es-CO")}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
          <Pagination page={page} pageCount={pageCount} start={start} end={end} total={total} onChange={(p) => setPage(p)} />
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-2xl bg-surface p-6 shadow-xl">
            <h2 className="mb-4 text-lg font-bold text-primary">Registrar tratamiento</h2>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Animal *</label>
                <select value={form.bovine_id} onChange={(e) => setForm({ ...form, bovine_id: e.target.value })}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required>
                  <option value="">Selecciona un animal…</option>
                  {bovines.map((b) => (
                    <option key={b.id} value={b.id}>{b.identification_number} {b.name ? `· ${b.name}` : ""}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Tipo <span className="text-red-600">*</span></label>
                  <select value={form.treatment_type} onChange={(e) => setForm({ ...form, treatment_type: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {Object.entries(TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Vía <span className="text-red-600">*</span></label>
                  <select value={form.administration_route} onChange={(e) => setForm({ ...form, administration_route: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none">
                    {Object.entries(ROUTE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Producto *</label>
                <input type="text" required value={form.product_name} onChange={(e) => setForm({ ...form, product_name: e.target.value })}
                  placeholder="Ej: Dectomax 1%" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Dosis *</label>
                  <input type="text" required value={form.dose} onChange={(e) => setForm({ ...form, dose: e.target.value })}
                    placeholder="Ej: 10 mL" className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
                </div>
                <div>
                  <label className="mb-1 block text-xs font-medium text-text-secondary">Fecha aplicación <span className="text-red-600">*</span></label>
                  <input type="date" value={form.application_date} onChange={(e) => setForm({ ...form, application_date: e.target.value })}
                    className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" required />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Próxima aplicación (opcional)</label>
                <input type="date" value={form.next_application_date} onChange={(e) => setForm({ ...form, next_application_date: e.target.value })}
                  className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-text-secondary">Observaciones</label>
                <textarea value={form.observations} onChange={(e) => setForm({ ...form, observations: e.target.value })}
                  rows={2} className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)}
                  className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">Cancelar</button>
                <button type="submit" disabled={!isFormComplete || saving}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:cursor-not-allowed disabled:opacity-60">
                  {saving ? "Guardando…" : "Guardar tratamiento"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
