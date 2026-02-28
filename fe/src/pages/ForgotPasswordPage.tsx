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
import "./ForgotPasswordPage.css";

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
      <div className="forgot">
        <div className="forgot__card">
          {!submitted ? (
            <>
              {/* ── Icono decorativo ── */}
              <div className="forgot__icon" aria-hidden="true">
                🔑
              </div>

              <h2 className="forgot__title">Recuperar contraseña</h2>
              <p className="forgot__subtitle">
                Ingresa tu correo electrónico y te enviaremos un enlace para
                restablecer tu contraseña.
              </p>

              <form onSubmit={handleSubmit} noValidate>
                <div className="forgot__field">
                  <label htmlFor="email">
                    Correo electrónico{" "}
                    <span className="forgot__required">*</span>
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="correo@ejemplo.com"
                    value={email}
                    onChange={handleChange}
                    autoFocus
                  />
                  {error && <span className="forgot__error">{error}</span>}
                </div>

                <button
                  type="submit"
                  className={`forgot__btn${!isFormComplete || loading ? " forgot__btn--disabled" : ""}`}
                  disabled={!isFormComplete || loading}
                >
                  {loading ? "Enviando..." : "Enviar enlace de recuperación"}
                </button>
              </form>

              <div className="forgot__links">
                <Link to="/login">← Volver al inicio de sesión</Link>
              </div>
            </>
          ) : (
            /* ── Estado de éxito ── */
            <div className="forgot__success">
              <div className="forgot__success-icon" aria-hidden="true">
                ✉️
              </div>
              <h2 className="forgot__title">¡Correo enviado!</h2>
              <p className="forgot__subtitle">
                Hemos enviado un enlace de recuperación a{" "}
                <strong>{email}</strong>. Revisa tu bandeja de entrada y sigue
                las instrucciones.
              </p>
              <p className="forgot__hint">
                Si no recibes el correo en unos minutos, revisa tu carpeta de
                spam o correo no deseado.
              </p>

              <button
                type="button"
                className="forgot__btn"
                onClick={() => {
                  setSubmitted(false);
                  setEmail("");
                }}
              >
                Reenviar correo
              </button>

              <div className="forgot__links">
                <Link to="/login">← Volver al inicio de sesión</Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
