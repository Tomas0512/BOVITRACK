/**
 * Archivo: pages/ResetPasswordPage.tsx
 * Descripción: Página para restablecer la contraseña de BoviTrack.
 * ¿Para qué? Permitir que el usuario defina una nueva contraseña después de
 *             haber recibido un enlace de recuperación por correo electrónico.
 * Flujo: El usuario llega con un token en la URL (?token=xxx), ingresa
 *        su nueva contraseña, la confirma y envía el formulario.
 */

import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { resetPassword as resetPasswordApi } from "../api/auth";
import "./ResetPasswordPage.css";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [serverError, setServerError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  /** ¿Están ambos campos llenos? */
  const isFormComplete =
    formData.password !== "" && formData.confirmPassword !== "";

  /** Actualiza campos de texto */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const copy = { ...prev };
        delete copy[name];
        return copy;
      });
    }
  };

  /** Validación del formulario */
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.password) {
      newErrors.password = "La contraseña es obligatoria";
    } else if (formData.password.length < 8) {
      newErrors.password = "Mínimo 8 caracteres";
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = "Debe contener al menos una mayúscula";
    } else if (!/[a-z]/.test(formData.password)) {
      newErrors.password = "Debe contener al menos una minúscula";
    } else if (!/[0-9]/.test(formData.password)) {
      newErrors.password = "Debe contener al menos un número";
    } else if (!/[^A-Za-z0-9]/.test(formData.password)) {
      newErrors.password = "Debe contener al menos un carácter especial";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Confirme su contraseña";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Las contraseñas no coinciden";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /** Indicadores de fortaleza de contraseña */
  const getPasswordStrength = () => {
    const pwd = formData.password;
    if (!pwd) return { level: 0, label: "", color: "" };

    let score = 0;
    if (pwd.length >= 8) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[a-z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;

    if (score <= 2) return { level: score, label: "Débil", color: "var(--color-error)" };
    if (score <= 3) return { level: score, label: "Media", color: "#f59e0b" };
    if (score <= 4) return { level: score, label: "Buena", color: "#3b82f6" };
    return { level: score, label: "Fuerte", color: "var(--color-primary)" };
  };

  const strength = getPasswordStrength();

  /** Envío del formulario */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setServerError("");

    try {
      await resetPasswordApi(token!, formData.password);
      setSubmitted(true);
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setServerError(
          axiosErr.response?.data?.detail || "Error al restablecer la contraseña."
        );
      } else {
        setServerError("Error de conexión. Verifique que el servidor esté activo.");
      }
    } finally {
      setLoading(false);
    }
  };

  /** Si no hay token en la URL, mostrar error */
  if (!token) {
    return (
      <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
        <div className="reset">
          <div className="reset__card">
            <div className="reset__icon" aria-hidden="true">⚠️</div>
            <h2 className="reset__title">Enlace inválido</h2>
            <p className="reset__subtitle">
              El enlace de recuperación no es válido o ha expirado.
              Solicita uno nuevo desde la página de recuperación.
            </p>
            <div className="reset__links">
              <Link to="/forgot-password">Solicitar nuevo enlace</Link>
            </div>
          </div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="reset">
        <div className="reset__card">
          {!submitted ? (
            <>
              <div className="reset__icon" aria-hidden="true">🔒</div>

              <h2 className="reset__title">Restablecer contraseña</h2>
              <p className="reset__subtitle">
                Ingresa tu nueva contraseña. Asegúrate de que sea segura y fácil
                de recordar.
              </p>

              <form onSubmit={handleSubmit} noValidate>
                {serverError && (
                  <div className="reset__server-error">{serverError}</div>
                )}

                {/* Nueva contraseña */}
                <div className="reset__field">
                  <label htmlFor="password">
                    Nueva contraseña <span className="reset__required">*</span>
                  </label>
                  <div className="reset__input-wrapper">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Mínimo 8 caracteres"
                      value={formData.password}
                      onChange={handleChange}
                      autoFocus
                    />
                    <button
                      type="button"
                      className="reset__toggle"
                      onClick={() => setShowPassword((v) => !v)}
                      aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                      {showPassword ? "🙈" : "👁️"}
                    </button>
                  </div>
                  {errors.password && (
                    <span className="reset__error">{errors.password}</span>
                  )}

                  {/* Barra de fortaleza */}
                  {formData.password && (
                    <div className="reset__strength">
                      <div className="reset__strength-bar">
                        {[1, 2, 3, 4, 5].map((i) => (
                          <div
                            key={i}
                            className="reset__strength-segment"
                            style={{
                              backgroundColor:
                                i <= strength.level ? strength.color : "#e5e7eb",
                            }}
                          />
                        ))}
                      </div>
                      <span
                        className="reset__strength-label"
                        style={{ color: strength.color }}
                      >
                        {strength.label}
                      </span>
                    </div>
                  )}
                </div>

                {/* Confirmar contraseña */}
                <div className="reset__field">
                  <label htmlFor="confirmPassword">
                    Confirmar contraseña <span className="reset__required">*</span>
                  </label>
                  <div className="reset__input-wrapper">
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirm ? "text" : "password"}
                      placeholder="Repita su nueva contraseña"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                    />
                    <button
                      type="button"
                      className="reset__toggle"
                      onClick={() => setShowConfirm((v) => !v)}
                      aria-label={showConfirm ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                      {showConfirm ? "🙈" : "👁️"}
                    </button>
                  </div>
                  {errors.confirmPassword && (
                    <span className="reset__error">{errors.confirmPassword}</span>
                  )}
                </div>

                {/* Requisitos */}
                <ul className="reset__requirements">
                  <li className={formData.password.length >= 8 ? "met" : ""}>Mínimo 8 caracteres</li>
                  <li className={/[A-Z]/.test(formData.password) ? "met" : ""}>Una letra mayúscula</li>
                  <li className={/[a-z]/.test(formData.password) ? "met" : ""}>Una letra minúscula</li>
                  <li className={/[0-9]/.test(formData.password) ? "met" : ""}>Un número</li>
                  <li className={/[^A-Za-z0-9]/.test(formData.password) ? "met" : ""}>Un carácter especial</li>
                </ul>

                <button
                  type="submit"
                  className={`reset__btn${!isFormComplete || loading ? " reset__btn--disabled" : ""}`}
                  disabled={!isFormComplete || loading}
                >
                  {loading ? "Restableciendo..." : "Restablecer contraseña"}
                </button>
              </form>

              <div className="reset__links">
                <Link to="/login">← Volver al inicio de sesión</Link>
              </div>
            </>
          ) : (
            /* ── Estado de éxito ── */
            <div className="reset__success">
              <div className="reset__success-icon" aria-hidden="true">✅</div>
              <h2 className="reset__title">¡Contraseña restablecida!</h2>
              <p className="reset__subtitle">
                Tu contraseña se ha cambiado correctamente. Ya puedes iniciar
                sesión con tu nueva contraseña.
              </p>

              <Link to="/login" className="reset__btn reset__btn--link">
                Ir a iniciar sesión
              </Link>
            </div>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
