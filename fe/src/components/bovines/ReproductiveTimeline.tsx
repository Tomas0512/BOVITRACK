import { useEffect, useState } from "react";
import { Dna, X } from "lucide-react";
import {
  listReproductiveEvents,
  createReproductiveEvent,
  deleteReproductiveEvent,
  type ReproductiveEventResponse,
  type ReproductiveEventCreate,
} from "../../api/reproductive_events";

interface Props {
  farmId: string;
  bovineId: string;
}

const EVENT_TYPE_LABELS: Record<string, string> = {
  servicio: "Servicio",
  diagnostico_gestion: "Diagnóstico de gestión",
  parto: "Parto",
  aborto: "Aborto",
  secado: "Secado",
};

const EVENT_TYPE_COLORS: Record<string, string> = {
  servicio: "bg-blue-50 text-blue-700",
  diagnostico_gestion: "bg-purple-50 text-purple-700",
  parto: "bg-green-50 text-green-700",
  aborto: "bg-red-50 text-red-700",
  secado: "bg-yellow-50 text-yellow-700",
};

const RESULT_LABELS: Record<string, string> = {
  positivo: "Positivo",
  negativo: "Negativo",
  gemelos: "Gemelos",
  macho: "Macho",
  hembra: "Hembra",
};

function formatDate(iso: string) {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

const EMPTY_FORM: ReproductiveEventCreate = {
  bovine_id: "",
  event_type: "servicio",
  event_date: new Date().toISOString().slice(0, 10),
  result: undefined,
  due_date: undefined,
  bull_id: undefined,
  calf_id: undefined,
  observations: "",
};

export default function ReproductiveTimeline({ farmId, bovineId }: Props) {
  const [events, setEvents] = useState<ReproductiveEventResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<ReproductiveEventCreate>({
    ...EMPTY_FORM,
    bovine_id: bovineId,
  });
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  function load() {
    setLoading(true);
    listReproductiveEvents(farmId, bovineId)
      .then(setEvents)
      .catch(() => setError("No se pudieron cargar los eventos reproductivos."))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, [farmId, bovineId]);

  const isFormComplete = form.event_type !== "" && form.event_date !== "";

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError("");
    if (!form.event_date) {
      setFormError("La fecha del evento es obligatoria.");
      return;
    }
    setSaving(true);
    try {
      await createReproductiveEvent(farmId, {
        ...form,
        result: form.result || null,
        due_date: form.due_date || null,
        bull_id: form.bull_id || null,
        calf_id: form.calf_id || null,
        observations: form.observations || null,
      });
      setForm({ ...EMPTY_FORM, bovine_id: bovineId });
      setShowModal(false);
      load();
    } catch {
      setFormError("No se pudo registrar el evento. Intente de nuevo.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(eventId: string) {
    if (!confirm("¿Eliminar este evento reproductivo?")) return;
    setDeletingId(eventId);
    try {
      await deleteReproductiveEvent(farmId, eventId);
      load();
    } catch {
      alert("No se pudo eliminar el evento.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-gray-900">
          <Dna size={18} className="inline mr-1.5 align-text-bottom text-primary" />
          Eventos reproductivos
        </h3>
        <button
          onClick={() => {
            setForm({ ...EMPTY_FORM, bovine_id: bovineId });
            setFormError("");
            setShowModal(true);
          }}
          className="rounded-lg bg-primary px-4 py-1.5 text-sm font-medium text-white hover:bg-primary/90"
        >
          + Nuevo evento
        </button>
      </div>

      {/* Modal para crear evento */}
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={() => setShowModal(false)}
        >
          <div
            className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-bold text-primary">Nuevo evento reproductivo</h2>
              <button
                onClick={() => setShowModal(false)}
                className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              >
                <X size={20} />
              </button>
            </div>

            {formError && (
              <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreate} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">
                  Tipo de evento <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={form.event_type}
                  onChange={(e) => setForm((f) => ({ ...f, event_type: e.target.value }))}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                >
                  {Object.entries(EVENT_TYPE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">
                  Fecha del evento <span className="text-red-500">*</span>
                </label>
                <input
                  type="date" required
                  value={form.event_date}
                  onChange={(e) => setForm((f) => ({ ...f, event_date: e.target.value }))}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">Resultado</label>
                <select
                  value={form.result ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, result: e.target.value || undefined }))}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                >
                  <option value="">— Sin registrar —</option>
                  {Object.entries(RESULT_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-gray-600">
                  Fecha estimada de parto
                </label>
                <input
                  type="date"
                  value={form.due_date ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value || undefined }))}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="mb-1 block text-xs font-medium text-gray-600">
                  Observaciones
                </label>
                <input
                  type="text" maxLength={500}
                  value={form.observations ?? ""}
                  onChange={(e) => setForm((f) => ({ ...f, observations: e.target.value }))}
                  placeholder="Opcional"
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                />
                <span className="mt-0.5 block text-right text-xs text-gray-400">{(form.observations ?? "").length}/500</span>
              </div>

              <div className="col-span-full flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!isFormComplete || saving}
                  className={`rounded-lg px-6 py-2 text-sm font-medium text-white transition-colors ${
                    !isFormComplete || saving
                      ? "cursor-not-allowed bg-gray-400 opacity-70"
                      : "bg-primary hover:bg-primary/90"
                  }`}
                >
                  {saving ? "Guardando…" : "Guardar evento"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
      {error && (
        <p className="py-4 text-center text-sm text-red-500">{error}</p>
      )}
      {!loading && !error && events.length === 0 && (
        <p className="py-6 text-center text-sm text-gray-400">
          Sin eventos reproductivos registrados.
        </p>
      )}
      {!loading && !error && events.length > 0 && (
        <div className="space-y-3">
          {events.map((event) => (
            <div
              key={event.id}
              className="flex items-start gap-4 rounded-xl border border-gray-100 p-4"
            >
              <div className="mt-1">
                {event.event_type === "parto" ? (
                  <Dna size={20} className="text-green-500" />
                ) : event.event_type === "servicio" ? (
                  <Dna size={20} className="text-blue-500" />
                ) : event.event_type === "aborto" ? (
                  <Dna size={20} className="text-red-500" />
                ) : event.event_type === "secado" ? (
                  <Dna size={20} className="text-yellow-500" />
                ) : (
                  <Dna size={20} className="text-purple-500" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      EVENT_TYPE_COLORS[event.event_type] ?? "bg-gray-50 text-gray-700"
                    }`}
                  >
                    {EVENT_TYPE_LABELS[event.event_type] ?? event.event_type}
                  </span>
                  <span className="text-xs text-gray-400">
                    {formatDate(event.event_date)}
                  </span>
                  {event.due_date && (
                    <span className="text-xs text-amber-600">
                      Parto estimado: {formatDate(event.due_date)}
                    </span>
                  )}
                </div>
                {event.result && (
                  <p className="mt-1 text-sm text-gray-600">
                    Resultado: {RESULT_LABELS[event.result] ?? event.result}
                  </p>
                )}
                {event.observations && (
                  <p className="mt-0.5 text-sm text-gray-400">
                    {event.observations}
                  </p>
                )}
              </div>
              <button
                onClick={() => handleDelete(event.id)}
                disabled={deletingId === event.id}
                className="shrink-0 text-xs text-red-400 hover:text-red-600 disabled:opacity-40"
              >
                {deletingId === event.id ? "…" : "Eliminar"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
