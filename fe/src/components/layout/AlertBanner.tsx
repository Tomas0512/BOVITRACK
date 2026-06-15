import { useEffect, useState } from "react";
import { AlertTriangle, Circle } from "lucide-react";
import { listAlerts, type AlertsResponse } from "../../api/alerts";

interface Props {
  farmId: string;
}

export default function AlertBanner({ farmId }: Props) {
  const [alerts, setAlerts] = useState<AlertsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const data = await listAlerts(farmId, 7);
        setAlerts(data);
      } catch {
        // Silencioso — no bloquear la página por alertas
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [farmId]);

  if (loading) return null;

  const overdueCount = alerts?.overdue.length ?? 0;
  const upcomingCount = alerts?.upcoming.length ?? 0;

  if (overdueCount === 0 && upcomingCount === 0) return null;

  return (
    <div className="mb-4 flex flex-col gap-2">
      {overdueCount > 0 && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3">
          <div className="flex items-start gap-3">
            <Circle size={20} fill="#dc2626" stroke="none" className="mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold text-red-800">
                {overdueCount} plan{overdueCount !== 1 ? "es" : ""} sanitario
                {overdueCount !== 1 ? "s" : ""} vencido
                {overdueCount !== 1 ? "s" : ""}
              </p>
              <ul className="mt-1 list-inside list-disc text-xs text-red-700">
                {alerts!.overdue.slice(0, 5).map((a) => (
                  <li key={a.id}>
                    {a.vaccine_or_treatment_name}
                    {a.bovine_id ? ` — Bovino #${a.bovine_id.slice(0, 8)}` : ""}
                    {a.next_scheduled_date
                      ? ` (venció el ${new Date(a.next_scheduled_date).toLocaleDateString("es-CO")})`
                      : ""}
                  </li>
                ))}
                {overdueCount > 5 && (
                  <li className="font-medium">
                    y {overdueCount - 5} más...
                  </li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}

      {upcomingCount > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
          <div className="flex items-start gap-3">
            <AlertTriangle size={20} className="mt-0.5 shrink-0 text-amber-600" />
            <div>
              <p className="text-sm font-semibold text-amber-800">
                {upcomingCount} plan{upcomingCount !== 1 ? "es" : ""} sanitario
                {upcomingCount !== 1 ? "s" : ""} próxim{upcomingCount !== 1 ? "os" : "o"}
              </p>
              <ul className="mt-1 list-inside list-disc text-xs text-amber-700">
                {alerts!.upcoming.slice(0, 5).map((a) => (
                  <li key={a.id}>
                    {a.vaccine_or_treatment_name}
                    {a.bovine_id ? ` — Bovino #${a.bovine_id.slice(0, 8)}` : ""}
                    {a.next_scheduled_date
                      ? ` (programado el ${new Date(a.next_scheduled_date).toLocaleDateString("es-CO")})`
                      : ""}
                  </li>
                ))}
                {upcomingCount > 5 && (
                  <li className="font-medium">
                    y {upcomingCount - 5} más...
                  </li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
