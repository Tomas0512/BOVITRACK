/*
 * features/team/pages/ReactivationRequestsPage.tsx
 *
 * COMO: Administrador de una finca
 * QUIERO: ver las solicitudes de reactivación de cuentas y aprobarlas o rechazarlas
 * PARA:   que alguien de mi equipo recupere el acceso sin tocar la base de datos.
 *
 * ¿Qué?  Lista las solicitudes PENDIENTES que el administrador puede moderar y
 *        permite aprobarlas (la cuenta vuelve a iniciar sesión) o rechazarlas.
 * ¿Impacto? El backend decide el alcance: solo aparecen personas que fueron
 *        miembros de alguna finca que este usuario administra (las demás no
 *        existen para él). Sin rol de Administrador, el backend responde 403 y
 *        la pantalla muestra ese mensaje.
 */

import { useEffect, useState } from "react";
import { CheckCircle2, RefreshCw, UserCheck, XCircle } from "lucide-react";
import { getApiErrorMessage } from "@/core/http";
import { ConfirmDialog } from "@/shared/ui";
import {
  approveReactivation,
  listReactivationRequests,
  rejectReactivation,
  type ReactivationRequestDetail,
} from "../api";

type Decision = "approve" | "reject";

export function ReactivationRequestsPage() {
  const [requests, setRequests] = useState<ReactivationRequestDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [pending, setPending] = useState<{ request: ReactivationRequestDetail; decision: Decision } | null>(null);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    setError("");
    return listReactivationRequests()
      .then(setRequests)
      .catch((err: unknown) => setError(getApiErrorMessage(err, "No se pudieron cargar las solicitudes")))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    // Carga inicial: el estado ya arranca en "cargando", así que no se toca aquí.
    listReactivationRequests()
      .then(setRequests)
      .catch((err: unknown) => setError(getApiErrorMessage(err, "No se pudieron cargar las solicitudes")))
      .finally(() => setLoading(false));
  }, []);

  const decide = async () => {
    if (!pending) return;
    const { request, decision } = pending;
    setSaving(true);
    setError("");
    try {
      await (decision === "approve" ? approveReactivation(request.id) : rejectReactivation(request.id));
      setRequests((current) => current.filter((r) => r.id !== request.id));
      setNotice(
        decision === "approve"
          ? `Cuenta de ${request.user_name} reactivada: ya puede iniciar sesión.`
          : `Solicitud de ${request.user_name} rechazada: la cuenta sigue desactivada.`,
      );
      setPending(null);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo procesar la solicitud"));
      setPending(null);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <UserCheck className="text-primary" size={24} />
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Solicitudes de reactivación</h1>
            <p className="text-sm text-text-secondary">
              Personas de tus fincas que piden recuperar el acceso a su cuenta.
            </p>
          </div>
        </div>
        <button
          onClick={() => {
            setNotice("");
            void load();
          }}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm font-medium text-text-secondary transition-colors hover:bg-surface-alt disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          Actualizar
        </button>
      </div>

      {notice && (
        <div role="status" className="flex items-center gap-2 rounded-lg border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-700">
          <CheckCircle2 size={18} />
          {notice}
        </div>
      )}
      {error && (
        <div role="alert" className="rounded-lg border border-danger bg-danger/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      <div className="rounded-2xl bg-surface p-6 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-bold text-text-primary">Pendientes</h2>
          {!loading && <p className="text-sm text-text-secondary">{requests.length} solicitud(es)</p>}
        </div>

        {loading ? (
          <p className="py-8 text-center text-sm text-text-muted">Cargando solicitudes…</p>
        ) : requests.length === 0 ? (
          <p className="py-8 text-center text-sm text-text-muted">
            No hay solicitudes pendientes de personas de tus fincas.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-border text-xs uppercase tracking-wide text-text-muted">
                  <th className="px-3 py-2">Fecha</th>
                  <th className="px-3 py-2">Persona</th>
                  <th className="px-3 py-2">Motivo</th>
                  <th className="px-3 py-2 text-right">Decisión</th>
                </tr>
              </thead>
              <tbody>
                {requests.map((r) => (
                  <tr key={r.id} className="border-b border-border/50 hover:bg-surface-alt">
                    <td className="whitespace-nowrap px-3 py-2 text-text-secondary">
                      {new Date(r.created_at).toLocaleString("es-CO")}
                    </td>
                    <td className="px-3 py-2 text-text-primary">
                      {r.user_name}
                      <span className="block text-xs text-text-muted">{r.user_email}</span>
                    </td>
                    <td className="px-3 py-2 text-text-secondary">{r.reason || "Sin motivo"}</td>
                    <td className="px-3 py-2">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => setPending({ request: r, decision: "approve" })}
                          aria-label={`Aprobar a ${r.user_name}`}
                          className="flex items-center gap-1 rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-white hover:opacity-90"
                        >
                          <CheckCircle2 size={14} /> Aprobar
                        </button>
                        <button
                          onClick={() => setPending({ request: r, decision: "reject" })}
                          aria-label={`Rechazar a ${r.user_name}`}
                          className="flex items-center gap-1 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-text-secondary hover:bg-surface-alt"
                        >
                          <XCircle size={14} /> Rechazar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={pending !== null}
        title={pending?.decision === "approve" ? "Aprobar solicitud" : "Rechazar solicitud"}
        message={
          pending?.decision === "approve"
            ? `${pending.request.user_name} podrá volver a iniciar sesión.`
            : `La cuenta de ${pending?.request.user_name ?? ""} seguirá desactivada.`
        }
        confirmLabel={pending?.decision === "approve" ? "Aprobar" : "Rechazar"}
        danger={pending?.decision === "reject"}
        loading={saving}
        onConfirm={() => void decide()}
        onCancel={() => setPending(null)}
      />
    </div>
  );
}
