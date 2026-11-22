import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bell, Check, ChevronRight } from "lucide-react";
import { useFarm } from "../../context/FarmContext";
import {
  getUnreadNotificationCount,
  listNotificationHistory,
  markNotificationRead,
  type NotificationLog,
} from "../../api/alerts";

const POLL_INTERVAL_MS = 60_000;
const PANEL_LIMIT = 5;

export default function NotificationBell() {
  const { activeFarmId } = useFarm();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [count, setCount] = useState(0);
  const [items, setItems] = useState<NotificationLog[]>([]);
  const [loading, setLoading] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const refreshCount = useCallback(async () => {
    if (!activeFarmId) return;
    try {
      const data = await getUnreadNotificationCount(activeFarmId);
      setCount(data.unread_count);
    } catch {
      // Silencioso: la campana no debe bloquear el flujo principal
    }
  }, [activeFarmId]);

  useEffect(() => {
    refreshCount();
    const intervalId = setInterval(refreshCount, POLL_INTERVAL_MS);

    const onVisibility = () => {
      if (document.visibilityState === "visible") refreshCount();
    };
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("focus", refreshCount);

    return () => {
      clearInterval(intervalId);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("focus", refreshCount);
    };
  }, [refreshCount]);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: PointerEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const handleToggle = async () => {
    const next = !open;
    setOpen(next);
    if (next && activeFarmId) {
      setLoading(true);
      try {
        const data = await listNotificationHistory(activeFarmId, {
          unread_only: true,
          limit: PANEL_LIMIT,
        });
        setItems(data.items);
      } catch {
        // Silencioso
      } finally {
        setLoading(false);
      }
    }
  };

  const handleMarkRead = async (id: string) => {
    if (!activeFarmId) return;
    try {
      await markNotificationRead(activeFarmId, id);
    } catch {
      return;
    }
    setItems((prev) => prev.filter((n) => n.id !== id));
    setCount((c) => Math.max(0, c - 1));
  };

  if (!activeFarmId) return null;

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={handleToggle}
        aria-label="Notificaciones"
        aria-expanded={open}
        title="Notificaciones"
        className="relative rounded-lg border border-border bg-surface p-2 text-text-secondary transition-colors hover:bg-surface-alt hover:text-text-primary"
      >
        <Bell size={18} />
        {count > 0 && (
          <span className="absolute -right-1.5 -top-1.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-bold leading-none text-white">
            {count > 99 ? "99+" : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-12 z-50 w-80 overflow-hidden rounded-xl border border-border bg-surface shadow-lg">
          <div className="flex items-center justify-between gap-2 border-b border-border bg-surface-alt/50 px-4 py-3">
            <p className="text-sm font-semibold text-text-primary">Notificaciones</p>
            {count > 0 && (
              <span className="rounded-full bg-red-600 px-2 py-0.5 text-[10px] font-bold text-white">
                {count} sin leer
              </span>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto">
            {loading ? (
              <p className="px-4 py-6 text-center text-sm text-text-muted">Cargando...</p>
            ) : items.length === 0 ? (
              <p className="px-4 py-6 text-center text-sm text-text-muted">
                No tienes notificaciones sin leer
              </p>
            ) : (
              <ul className="divide-y divide-border">
                {items.map((n) => (
                  <li key={n.id} className="px-4 py-3">
                    <div className="flex items-start gap-2">
                      <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-text-primary">{n.title}</p>
                        {n.message && (
                          <p className="mt-0.5 line-clamp-2 text-xs text-text-muted">
                            {n.message}
                          </p>
                        )}
                        <p className="mt-1 text-[10px] uppercase tracking-wide text-text-muted">
                          {new Date(n.created_at).toLocaleString("es-CO")}
                        </p>
                      </div>
                      <button
                        onClick={() => handleMarkRead(n.id)}
                        aria-label="Marcar como leída"
                        title="Marcar como leída"
                        className="rounded-lg p-1 text-text-muted transition-colors hover:bg-surface-alt hover:text-primary"
                      >
                        <Check size={15} />
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="border-t border-border p-2">
            <button
              onClick={() => {
                setOpen(false);
                navigate(`/farms/${activeFarmId}/alerts`);
              }}
              className="flex w-full items-center justify-center gap-1 rounded-lg px-3 py-2 text-sm font-semibold text-primary transition-colors hover:bg-surface-alt"
            >
              Ver todas <ChevronRight size={15} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}