import { useCallback, useEffect, useRef, useState } from "react";

/**
 * ¿Qué? Sesión por inactividad: si no hay interacción durante `idleMs`,
 *        entra en advertencia (`warning`) y al llegar a 0 llama a `onExpire`.
 * ¿Para qué? Cumplir el requisito de "tiempo limitado de sesión con alerta".
 * ¿Impacto? Cualquier interacción (mouse, teclado, clic, scroll) reinicia el reloj.
 */
export function useSessionTimeout(idleMs: number, warnMs: number, onExpire: () => void) {
  const lastActivity = useRef<number | null>(null);
  const [remainingMs, setRemainingMs] = useState<number>(idleMs);
  const [warning, setWarning] = useState<boolean>(false);
  const expiredRef = useRef<boolean>(false);

  const touch = useCallback(() => {
    lastActivity.current = Date.now();
  }, []);

  // Actividad del usuario reinicia el contador de inactividad.
  useEffect(() => {
    const events = ["mousemove", "keydown", "click", "scroll", "touchstart"] as const;
    let throttle: number | undefined;
    const handler = () => {
      if (throttle) return;
      throttle = window.setTimeout(() => {
        throttle = undefined;
        touch();
      }, 400);
    };
    events.forEach((e) => window.addEventListener(e, handler));
    return () => {
      events.forEach((e) => window.removeEventListener(e, handler));
      if (throttle) window.clearTimeout(throttle);
    };
  }, [touch]);

  // Tick por segundo: calcula el tiempo restante y dispara el cierre al llegar a 0.
  useEffect(() => {
    if (lastActivity.current === null) lastActivity.current = Date.now();
    const timer = window.setInterval(() => {
      const since = lastActivity.current ?? Date.now();
      const rem = Math.max(0, idleMs - (Date.now() - since));
      setRemainingMs(rem);
      setWarning(rem <= warnMs && rem > 0);
      if (rem <= 0 && !expiredRef.current) {
        expiredRef.current = true;
        onExpire();
      }
    }, 1000);
    return () => window.clearInterval(timer);
  }, [idleMs, warnMs, onExpire]);

  return { remainingMs, warning, touch };
}
