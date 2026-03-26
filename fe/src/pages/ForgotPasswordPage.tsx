/**
 * Archivo: pages/ForgotPasswordPage.tsx
 * Descripción: Página de recuperación de contraseña de BoviTrack.
 * ¿Para qué? Permitir que usuarios que olvidaron su contraseña soliciten
 *             un enlace de recuperación enviado a su correo electrónico.
 * Campos: correo electrónico.
 * Enlaces: "Volver al inicio de sesión".
 */

import { useState } from "react";
import { Link } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { forgotPassword } from "../api/auth";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  /** ¿El campo está lleno? */
  const isFormComplete = email.trim() !== "";

  /** Actualiza el campo de correo */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (error) setError("");
  };

  /** Validación del correo */
  const validate = (): boolean => {
    if (!email.trim()) {
      setError("El correo es obligatorio");
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Ingrese un correo válido (ej: correo@ejemplo.com)");
      return false;
    }
    return true;
  };

  /** Envío del formulario */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);

    try {
      await forgotPassword(email);
      setSubmitted(true);
    } catch {
      // Siempre mostramos éxito (no revelar si el email existe)
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="flex w-full items-center justify-center">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
          {!submitted ? (
            <>
              <div className="mb-2 text-center text-4xl" aria-hidden="true">🔑</div>

              <h2 className="mb-0.5 text-center text-xl font-bold text-primary">Recuperar contraseña</h2>
              <p className="mb-6 text-center text-sm leading-relaxed text-gray-500">
                Ingresa tu correo electrónico y te enviaremos un enlace para
                restablecer tu contraseña.
              </p>

              <form onSubmit={handleSubmit} noValidate>
                <div className="mb-4 flex flex-col">
                  <label htmlFor="email" className="mb-1 text-sm font-semibold text-gray-800">
                    Correo electrónico{" "}
                    <span className="font-bold text-red-600">*</span>
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="correo@ejemplo.com"
                    value={email}
                    onChange={handleChange}
                    autoFocus
                    className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-3 py-2 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10"
                  />
                  {error && <span className="mt-0.5 text-xs text-red-600">{error}</span>}
                </div>

                <button
                  type="submit"
                  className={`mt-2 w-full rounded-lg py-2.5 text-base font-bold text-white transition-all active:scale-[0.98] ${
                    !isFormComplete || loading
                      ? "cursor-not-allowed bg-gray-400 opacity-70"
                      : "bg-primary hover:bg-primary-light"
                  }`}
                  disabled={!isFormComplete || loading}
                >
                  {loading ? "Enviando..." : "Enviar enlace de recuperación"}
                </button>
              </form>

              <div className="mt-5 flex justify-center">
                <Link to="/login" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">← Volver al inicio de sesión</Link>
              </div>
            </>
          ) : (
            <div className="text-center">
              <div className="mb-3 text-5xl" aria-hidden="true">✉️</div>
              <h2 className="mb-0.5 text-center text-xl font-bold text-primary">¡Correo enviado!</h2>
              <p className="mb-6 text-center text-sm leading-relaxed text-gray-500">
                Hemos enviado un enlace de recuperación a{" "}
                <strong>{email}</strong>. Revisa tu bandeja de entrada y sigue
                las instrucciones.
              </p>
              <p className="mb-5 text-xs leading-relaxed text-gray-500">
                Si no recibes el correo en unos minutos, revisa tu carpeta de
                spam o correo no deseado.
              </p>

              <button
                type="button"
                className="w-full rounded-lg bg-primary py-2.5 text-base font-bold text-white transition-colors hover:bg-primary-light active:scale-[0.98]"
                onClick={() => {
                  setSubmitted(false);
                  setEmail("");
                }}
              >
                Reenviar correo
              </button>

              <div className="mt-5 flex justify-center">
                <Link to="/login" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">← Volver al inicio de sesión</Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
