import { useCallback, useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft, Bell, BellRing, Check, Loader2, Save,
} from "lucide-react";
import {
  getNotificationPrefs,
  updateNotificationPrefs,
  listNotificationHistory,
  markNotificationRead,
  type NotificationPref,
  type NotificationLog,
} from "../api/alerts";
import AlertBanner from "../components/layout/AlertBanner";

const TYPE_LABELS: Record<string, string> = {
  sanitary: "Sanitario",
  low_stock: "Stock bajo",
  reproductive: "Reproductivo",
  birth: "Nacimiento",
};

const CHANNEL_OPTIONS = [
  { value: "email", label: "Email" },
  { value: "in_app", label: "En la app" },
  { value: "ambos", label: "Ambos" },
];

const FREQUENCY_OPTIONS = [
  { value: "real_time", label: "En tiempo real" },
  { value: "daily", label: "Diaria" },
  { value: "weekly", label: "Semanal" },
];

type ToggleField = "notify_sanitary" | "notify_low_stock" | "notify_reproductive" | "notify_birth";

const TOGGLES: { field: ToggleField; label: string; desc: string }[] = [
  { field: "notify_sanitary", label: "Planes sanitarios", desc: "Vacunas y tratamientos vencidos o próximos" },
  { field: "notify_low_stock", label: "Stock bajo", desc: "Insumos por debajo del mínimo" },
  { field: "notify_reproductive", label: "Eventos reproductivos", desc: "Celo, monta, diagnóstico y parto" },
  { field: "notify_birth", label: "Nacimientos", desc: "Aviso de crías recién nacidas" },
];

export default function AlertasPage() {
  const { farmId } = useParams<{ farmId: string }>();
  const [pref, setPref] = useState<NotificationPref | null>(null);
  const [history, setHistory] = useState<NotificationLog[]>([]);
  const [typeFilter, setTypeFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const load = useCallback(async () => {
    if (!farmId) return;
    setLoading(true);
    setError("");
    try {
      const [prefs, hist] = await Promise.all([
        getNotificationPrefs(farmId),
        listNotificationHistory(farmId, { type: typeFilter || undefined }),
      ]);
      setPref(prefs);
      setHistory(hist.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar alertas");
    } finally {
      setLoading(false);
    }
  }, [farmId, typeFilter]);

  useEffect(() => {
    load();
  }, [load]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!farmId || !pref) return;
    setSaving(true);
    setError("");
    setSaved(false);
    try {
      const updated = await updateNotificationPrefs(farmId, {
        channel: pref.channel,
        frequency: pref.frequency,
        notify_sanitary: pref.notify_sanitary,
        notify_low_stock: pref.notify_low_stock,
        notify_reproductive: pref.notify_reproductive,
        notify_birth: pref.notify_birth,
      });
      setPref(updated);
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleMarkRead = async (id: string) => {
    if (!farmId) return;
    try {
      await markNotificationRead(farmId, id);
      setHistory((prev) => prev.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n)));
    } catch {
      // Silencioso — no bloquear la interacción
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error && !pref) {
    return (
      <div className="flex justify-center pt-12">
        <div className="w-full max-w-md rounded-2xl bg-surface p-8 text-center shadow-lg">
          <h2 className="mb-2 text-lg font-bold text-text-primary">Error</h2>
          <p className="mb-6 text-sm text-text-secondary">{error}</p>
          <Link to="/dashboard" className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline hover:bg-primary-light">
            Volver al dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Link to={`/farms/${farmId}`} className="rounded-lg p-2 text-text-muted hover:bg-surface-alt hover:text-text-primary">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-text-primary">Alertas y notificaciones</h1>
      </div>

      {farmId && <AlertBanner farmId={farmId} />}

      {pref && (
        <form onSubmit={handleSave} className="rounded-xl border border-border bg-surface p-6 shadow-sm">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-text-primary">
            <Bell size={20} className="text-primary" /> Preferencias
          </h2>

          <div className="mb-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Canal de entrega</label>
              <select
                value={pref.channel}
                onChange={(e) => setPref({ ...pref, channel: e.target.value as NotificationPref["channel"] })}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              >
                {CHANNEL_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Frecuencia</label>
              <select
                value={pref.frequency}
                onChange={(e) => setPref({ ...pref, frequency: e.target.value as NotificationPref["frequency"] })}
                className="w-full rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
              >
                {FREQUENCY_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {TOGGLES.map((t) => (
              <label key={t.field} className="flex cursor-pointer items-start gap-3 rounded-lg border border-border p-3">
                <input
                  type="checkbox"
                  checked={pref[t.field]}
                  onChange={(e) => setPref({ ...pref, [t.field]: e.target.checked })}
                  className="mt-1 h-4 w-4 text-primary focus:ring-primary"
                />
                <span>
                  <span className="block text-sm font-semibold text-text-primary">{t.label}</span>
                  <span className="block text-xs text-text-secondary">{t.desc}</span>
                </span>
              </label>
            ))}
          </div>

          <div className="mt-5 flex items-center gap-3">
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60"
            >
              {saving ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
              {saving ? "Guardando..." : "Guardar preferencias"}
            </button>
            {saved && <span className="text-sm font-medium text-green-600">Preferencias guardadas</span>}
          </div>
        </form>
      )}

      <div className="rounded-xl border border-border bg-surface p-6 shadow-sm">
        <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-text-primary">
          <BellRing size={20} className="text-primary" /> Historial de notificaciones
        </h2>

        <div className="mb-4 flex items-center gap-3">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="w-48 rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none"
          >
            <option value="">Todos los tipos</option>
            {Object.entries(TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>

        {history.length === 0 ? (
          <p className="py-8 text-center text-sm text-text-secondary">
            No hay notificaciones todavía.
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {history.map((n) => (
              <li key={n.id} className={`flex items-start gap-3 py-3 ${n.read_at ? "opacity-60" : ""}`}>
                <span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${n.read_at ? "bg-border" : "bg-primary"}`} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate text-sm font-semibold text-text-primary">{n.title}</p>
                    <span className="shrink-0 rounded bg-surface-alt px-2 py-0.5 text-[11px] font-medium text-text-secondary">
                      {TYPE_LABELS[n.type] ?? n.type}
                    </span>
                  </div>
                  {n.message && <p className="mt-0.5 text-xs text-text-secondary">{n.message}</p>}
                  <p className="mt-0.5 text-[11px] text-text-muted">
                    {n.created_at ? new Date(n.created_at).toLocaleString("es-CO") : ""}
                    {n.channel === "email" ? " · enviado por email" : n.channel === "in_app" ? " · en la app" : " · email y app"}
                  </p>
                </div>
                {!n.read_at && (
                  <button
                    onClick={() => handleMarkRead(n.id)}
                    className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-border px-2.5 py-1.5 text-xs font-medium text-text-secondary hover:bg-surface-alt"
                  >
                    <Check size={14} /> Leída
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
