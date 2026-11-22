import { useNavigate } from "react-router-dom";
import { useSessionTimeout } from "../hooks/useSessionTimeout";

const IDLE_MS = 15 * 60 * 1000;
const WARN_MS = 2 * 60 * 1000;

/**
 * ¿Qué? Muestra una alerta con la cuenta regresiva cuando la sesión está por
 *        vencerse por inactividad, y al llegar a 0 cierra la sesión.
 * ¿Para qué? Cumplir la sesión limitada (~15 min) con aviso previo.
 * ¿Impacto? Solo actúa dentro del layout autenticado (AppLayout).
 */
export default function SessionGuard() {
  const navigate = useNavigate();

  const { remainingMs, warning } = useSessionTimeout(IDLE_MS, WARN_MS, () => {
    sessionStorage.setItem("session_expired", "1");
    window.dispatchEvent(new Event("auth:logout"));
    navigate("/login", { replace: true });
  });

  const totalSec = Math.max(0, Math.ceil(remainingMs / 1000));
  const mins = Math.floor(totalSec / 60);
  const secs = totalSec % 60;

  if (!warning) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40">
      <div className="w-full max-w-sm rounded-2xl bg-surface p-6 text-center shadow-xl">
        <p className="text-sm font-semibold text-text-primary">Sesión por inactividad</p>
        <p className="mt-1 text-xs text-text-secondary">Se cerrará automáticamente en</p>
        <p className="mt-2 text-4xl font-bold tabular-nums text-primary">
          {mins}:{String(secs).padStart(2, "0")}
        </p>
        <p className="mt-2 text-xs text-text-muted">Interactúa para mantener la sesión abierta.</p>
      </div>
    </div>
  );
}
