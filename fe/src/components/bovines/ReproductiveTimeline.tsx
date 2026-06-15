/*
 * Archivo: components/bovines/ReproductiveTimeline.tsx
 * ¿Qué? Componente que muestra una línea de tiempo de eventos reproductivos
 *       de un bovino. Permite listar, crear y eliminar eventos.
 * ¿Para qué? El veterinario necesita registrar y consultar servicios,
 *            diagnósticos de gestación, partos, abortos y secados de cada animal.
 * ¿Impacto? Sin este componente, el módulo reproductivo (HU006) queda
 *           incompleto: el backend funciona pero no hay interfaz de usuario.
 */
import { useEffect, useState } from "react";
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

// ¿Qué? Etiquetas descriptivas para cada tipo de evento.
// ¿Para qué? Mostrar en español los tipos que vienen del backend en inglés.
const EVENT_TYPE_LABELS: Record<string, string> = {
  servicio: "Servicio",
  diagnostico_gestion: "Diagnóstico de gestión",
  parto: "Parto",
  aborto: "Aborto",
  secado: "Secado",
};

// ¿Qué? Colores de badge según el tipo de evento.
// ¿Para qué? Diferenciar visualmente cada tipo en la lista.
const EVENT_TYPE_COLORS: Record<string, string> = {
  servicio: "bg-blue-50 text-blue-700",
  diagnostico_gestion: "bg-purple-50 text-purple-700",
  parto: "bg-green-50 text-green-700",
  aborto: "bg-red-50 text-red-700",
  secado: "bg-yellow-50 text-yellow-700",
};

// ¿Qué? Etiquetas para los resultados de diagnóstico o parto.
// ¿Para qué? Traducir los valores que envía el backend.
const RESULT_LABELS: Record<string, string> = {
  positivo: "Positivo",
  negativo: "Negativo",
  gemelos: "Gemelos",
  macho: "Macho",
  hembra: "Hembra",
};

// ¿Qué? Convierte fecha ISO "YYYY-MM-DD" a formato legible "DD/MM/YYYY".
// ¿Para qué? Mostrar fechas en el formato colombiano.
function formatDate(iso: string) {
  const [y, m, d] = iso.split("-");
  return `${d}/${m}/${y}`;
}

// ¿Qué? Estado inicial del formulario de nuevo evento.
// ¿Para qué? Evitar valores undefined y tener un punto de partida limpio.
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
  // ¿Qué? Estado del componente: lista de eventos, carga, error, formulario.
  // ¿Para qué? Controlar cada aspecto visual del componente de forma independiente.
  const [events, setEvents] = useState<ReproductiveEventResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<ReproductiveEventCreate>({
    ...EMPTY_FORM,
    bovine_id: bovineId,
  });
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // ¿Qué? Carga los eventos reproductivos del bovino desde el backend.
  // ¿Para qué? Poblar la lista cada vez que se monta el componente.
  // ¿Impacto? Si falla, se muestra mensaje de error al usuario.
  function load() {
    setLoading(true);
    listReproductiveEvents(farmId, bovineId)
      .then(setEvents)
      .catch(() => setError("No se pudieron cargar los eventos reproductivos."))
      .finally(() => setLoading(false));
  }

  // ¿Qué? Recargar eventos cuando cambia el bovino o la finca.
  useEffect(() => {
    load();
  }, [farmId, bovineId]);

  // ¿Qué? Enviar un nuevo evento reproductivo al backend.
  // ¿Para qué? Registrar servicio, parto, aborto, etc.
  // ¿Impacto? Si falla, el evento no se guarda y se muestra error.
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
      setShowForm(false);
      load();
    } catch {
      setFormError("No se pudo registrar el evento. Intente de nuevo.");
    } finally {
      setSaving(false);
    }
  }

  // ¿Qué? Eliminar un evento reproductivo previa confirmación.
  // ¿Para qué? Corregir registros incorrectos.
  // ¿Impacto? El evento se borra permanentemente del sistema.
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
      {/* ¿Qué? Cabecera con título y botón para mostrar/ocultar el formulario. */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-bold text-gray-900">🧬 Eventos reproductivos</h3>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-lg bg-primary px-4 py-1.5 text-sm font-medium text-white hover:bg-primary/90"
        >
          {showForm ? "Cancelar" : "+ Nuevo evento"}
        </button>
      </div>

      {/* ¿Qué? Formulario inline para registrar un nuevo evento reproductivo.
          ¿Para qué? El usuario completa tipo, fecha, resultado y observaciones.
          ¿Impacto? Sin validación, se podrían enviar datos incompletos. */}
      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 grid grid-cols-1 gap-4 rounded-xl border border-gray-100 bg-gray-50 p-4 sm:grid-cols-2"
        >
          {/* Tipo de evento (select) */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Tipo de evento <span className="text-red-500">*</span>
            </label>
            <select
              value={form.event_type}
              onChange={(e) =>
                setForm((f) => ({ ...f, event_type: e.target.value }))
              }
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            >
              {Object.entries(EVENT_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {/* Fecha del evento */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Fecha del evento <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              required
              value={form.event_date}
              onChange={(e) =>
                setForm((f) => ({ ...f, event_date: e.target.value }))
              }
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          {/* Resultado del evento (solo aplica a algunos tipos) */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Resultado
            </label>
            <select
              value={form.result ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  result: e.target.value || undefined,
                }))
              }
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            >
              <option value="">— Sin registrar —</option>
              {Object.entries(RESULT_LABELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {/* Fecha estimada de parto (se auto calcula si es servicio) */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Fecha estimada de parto
            </label>
            <input
              type="date"
              value={form.due_date ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  due_date: e.target.value || undefined,
                }))
              }
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          {/* Observaciones adicionales */}
          <div className="sm:col-span-2">
            <label className="mb-1 block text-xs font-medium text-gray-600">
              Observaciones
            </label>
            <input
              type="text"
              value={form.observations ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, observations: e.target.value }))
              }
              placeholder="Opcional"
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>

          {/* Errores de validación del formulario */}
          {formError && (
            <p className="col-span-full text-sm text-red-500">{formError}</p>
          )}

          {/* Botón de guardado */}
          <div className="col-span-full flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-primary px-6 py-2 text-sm font-medium text-white hover:bg-primary/90 disabled:opacity-50"
            >
              {saving ? "Guardando…" : "Guardar evento"}
            </button>
          </div>
        </form>
      )}

      {/* ¿Qué? Indicador de carga mientras se obtienen los eventos.
          ¿Para qué? Feedback visual al usuario durante la petición HTTP. */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
      {/* ¿Qué? Mensaje de error si la carga falla. */}
      {error && (
        <p className="py-4 text-center text-sm text-red-500">{error}</p>
      )}
      {/* ¿Qué? Estado vacío: no hay eventos registrados. */}
      {!loading && !error && events.length === 0 && (
        <p className="py-6 text-center text-sm text-gray-400">
          Sin eventos reproductivos registrados.
        </p>
      )}
      {/* ¿Qué? Lista de eventos en formato tarjeta (timeline).
          ¿Para qué? Cada tarjeta muestra tipo, fecha, resultado y acciones.
          ¿Impacto? Sin esta vista, el usuario no puede consultar el historial. */}
      {!loading && !error && events.length > 0 && (
        <div className="space-y-3">
          {events.map((event) => (
            <div
              key={event.id}
              className="flex items-start gap-4 rounded-xl border border-gray-100 p-4"
            >
              {/* Icono según tipo de evento */}
              <span className="mt-1 text-xl">
                {event.event_type === "parto"
                  ? "🐄"
                  : event.event_type === "servicio"
                  ? "🤝"
                  : event.event_type === "aborto"
                  ? "⚠️"
                  : event.event_type === "secado"
                  ? "⏹️"
                  : "🔬"}
              </span>
              <div className="flex-1">
                {/* Badge de tipo + fecha + fecha estimada de parto */}
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
                {/* Resultado del evento */}
                {event.result && (
                  <p className="mt-1 text-sm text-gray-600">
                    Resultado: {RESULT_LABELS[event.result] ?? event.result}
                  </p>
                )}
                {/* Observaciones */}
                {event.observations && (
                  <p className="mt-0.5 text-sm text-gray-400">
                    {event.observations}
                  </p>
                )}
              </div>
              {/* Botón eliminar */}
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
