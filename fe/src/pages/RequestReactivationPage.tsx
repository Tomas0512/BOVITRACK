import { useState } from "react";
import { Link } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { requestReactivation } from "../api/auth";

export default function RequestReactivationPage() {
  const [email, setEmail] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await requestReactivation({ email, reason: reason || undefined });
      setSuccess(true);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(msg ?? "No se pudo enviar la solicitud");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
        <div className="flex w-full items-center justify-center">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-lg">
            <div className="mb-3 text-5xl">✅</div>
            <h2 className="mb-2 text-xl font-bold text-gray-800">Solicitud enviada</h2>
            <p className="mb-6 text-sm text-gray-500">
              Tu solicitud de reactivación ha sido registrada. Un administrador la revisará pronto.
            </p>
            <Link to="/login" className="inline-block rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white no-underline hover:bg-primary-light">
              Volver al login
            </Link>
          </div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="flex w-full items-center justify-center">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
          <h2 className="mb-0.5 text-xl font-bold text-primary">Solicitar reactivación</h2>
          <p className="mb-6 text-sm text-gray-500">
            Ingresa tu correo para solicitar la reactivación de tu cuenta desactivada.
          </p>

          {error && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">{error}</div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-semibold text-gray-800">Correo electrónico</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="correo@ejemplo.com"
                className="w-full rounded-lg border-[1.5px] border-gray-300 bg-surface px-3 py-2 text-sm text-gray-800 outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-semibold text-gray-800">Motivo (opcional)</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Explica por qué deseas reactivar tu cuenta..."
                rows={3}
                className="w-full rounded-lg border-[1.5px] border-gray-300 bg-surface px-3 py-2 text-sm text-gray-800 outline-none focus:border-primary focus:ring-2 focus:ring-primary/10"
              />
            </div>
            <button
              type="submit"
              disabled={!email.trim() || loading}
              className="w-full rounded-lg bg-primary py-2.5 text-base font-bold text-white transition-all hover:bg-primary-light disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Enviando..." : "Enviar solicitud"}
            </button>
          </form>

          <div className="mt-4 text-center">
            <Link to="/login" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">
              ← Volver al login
            </Link>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
