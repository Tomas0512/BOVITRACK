import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, AlertTriangle, Loader2 } from "lucide-react";
import { AuthLayout } from "../components/layout/AuthLayout";
import { verifyEmail } from "../api/auth";

type State = "loading" | "success" | "error";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [state, setState] = useState<State>(token ? "loading" : "error");
  const [message, setMessage] = useState(
    token ? "" : "El enlace de verificación es inválido o está incompleto."
  );

  useEffect(() => {
    if (!token) return;
    verifyEmail(token)
      .then((res) => {
        setState("success");
        setMessage(res.message || "Correo electrónico verificado.");
      })
      .catch((err: unknown) => {
        setState("error");
        setMessage(
          err instanceof Error && err.message
            ? err.message
            : "No se pudo verificar el correo."
        );
      });
  }, [token]);

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="flex w-full items-center justify-center">
        <div className="w-full max-w-md rounded-2xl bg-surface p-8 text-center shadow-lg">
          {state === "loading" && (
            <>
              <Loader2 size={40} className="mx-auto mb-3 animate-spin text-primary" />
              <h2 className="mb-2 text-xl font-bold text-primary">Verificando…</h2>
              <p className="text-sm text-text-secondary">Validando el enlace recibido por correo.</p>
            </>
          )}

          {state === "success" && (
            <>
              <CheckCircle2 size={48} className="text-green-500 mx-auto mb-3" />
              <h2 className="mb-2 text-xl font-bold text-primary">¡Correo verificado!</h2>
              <p className="mb-6 text-sm text-text-secondary">{message}</p>
              <Link
                to="/login"
                className="block w-full rounded-lg bg-primary py-2.5 text-base font-bold text-white no-underline transition-colors hover:bg-primary-light"
              >
                Ir a iniciar sesión
              </Link>
            </>
          )}

          {state === "error" && (
            <>
              <AlertTriangle size={40} className="mx-auto mb-3 text-amber-500" />
              <h2 className="mb-2 text-xl font-bold text-primary">No se pudo verificar</h2>
              <p className="mb-6 text-sm text-text-secondary">{message}</p>
              <Link
                to="/login"
                className="block w-full rounded-lg bg-primary py-2.5 text-base font-bold text-white no-underline transition-colors hover:bg-primary-light"
              >
                Volver al inicio de sesión
              </Link>
            </>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
