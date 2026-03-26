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
        <div className="flex w-full items-center justify-center">
          <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
            <div className="mb-2 text-center text-4xl" aria-hidden="true">⚠️</div>
            <h2 className="mb-0.5 text-center text-xl font-bold text-primary">Enlace inválido</h2>
            <p className="mb-6 text-center text-sm leading-relaxed text-gray-500">
              El enlace de recuperación no es válido o ha expirado.
              Solicita uno nuevo desde la página de recuperación.
            </p>
            <div className="mt-5 flex justify-center">
              <Link to="/forgot-password" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">Solicitar nuevo enlace</Link>
            </div>
          </div>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="flex w-full items-center justify-center">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
          {!submitted ? (
            <>
              <div className="mb-2 text-center text-4xl" aria-hidden="true">🔒</div>

              <h2 className="mb-0.5 text-center text-xl font-bold text-primary">Restablecer contraseña</h2>
              <p className="mb-6 text-center text-sm leading-relaxed text-gray-500">
                Ingresa tu nueva contraseña. Asegúrate de que sea segura y fácil
                de recordar.
              </p>

              <form onSubmit={handleSubmit} noValidate>
                {serverError && (
                  <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">{serverError}</div>
                )}

                {/* Nueva contraseña */}
                <div className="mb-4 flex flex-col">
                  <label htmlFor="password" className="mb-1 text-sm font-semibold text-gray-800">
                    Nueva contraseña <span className="font-bold text-red-600">*</span>
                  </label>
                  <div className="relative flex items-center">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Mínimo 8 caracteres"
                      value={formData.password}
                      onChange={handleChange}
                      autoFocus
                      className="w-full rounded-lg border-[1.5px] border-gray-300 bg-surface py-2 pl-3 pr-10 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10"
                    />
                    <button
                      type="button"
                      className="absolute right-2 bg-transparent border-none cursor-pointer text-lg opacity-60 hover:opacity-100 transition-opacity"
                      onClick={() => setShowPassword((v) => !v)}
                      aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                      {showPassword ? "🙈" : "👁️"}
                    </button>
                  </div>
                  {errors.password && (
                    <span className="mt-0.5 text-xs text-red-600">{errors.password}</span>
                  )}

                  {/* Barra de fortaleza */}
                  {formData.password && (
                    <div className="mt-1.5 flex items-center gap-2">
                      <div className="flex flex-1 gap-0.5">
                        {[1, 2, 3, 4, 5].map((i) => (
                          <div
                            key={i}
                            className="h-1 flex-1 rounded-sm transition-colors"
                            style={{
                              backgroundColor:
                                i <= strength.level ? strength.color : "#e5e7eb",
                            }}
                          />
                        ))}
                      </div>
                      <span
                        className="min-w-14 text-right text-xs font-semibold"
                        style={{ color: strength.color }}
                      >
                        {strength.label}
                      </span>
                    </div>
                  )}
                </div>

                {/* Confirmar contraseña */}
                <div className="mb-4 flex flex-col">
                  <label htmlFor="confirmPassword" className="mb-1 text-sm font-semibold text-gray-800">
                    Confirmar contraseña <span className="font-bold text-red-600">*</span>
                  </label>
                  <div className="relative flex items-center">
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirm ? "text" : "password"}
                      placeholder="Repita su nueva contraseña"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      className="w-full rounded-lg border-[1.5px] border-gray-300 bg-surface py-2 pl-3 pr-10 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10"
                    />
                    <button
                      type="button"
                      className="absolute right-2 bg-transparent border-none cursor-pointer text-lg opacity-60 hover:opacity-100 transition-opacity"
                      onClick={() => setShowConfirm((v) => !v)}
                      aria-label={showConfirm ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                      {showConfirm ? "🙈" : "👁️"}
                    </button>
                  </div>
                  {errors.confirmPassword && (
                    <span className="mt-0.5 text-xs text-red-600">{errors.confirmPassword}</span>
                  )}
                </div>

                {/* Requisitos */}
                <ul className="mb-5 grid list-none grid-cols-1 gap-1 p-0 sm:grid-cols-2 sm:gap-x-3">
                  <li className={`relative pl-5 text-xs leading-relaxed ${formData.password.length >= 8 ? "text-primary before:text-primary before:content-['●']" : "text-gray-500 before:text-gray-300 before:content-['○']"} before:absolute before:left-0 before:text-[0.7rem]`}>Mínimo 8 caracteres</li>
                  <li className={`relative pl-5 text-xs leading-relaxed ${/[A-Z]/.test(formData.password) ? "text-primary before:text-primary before:content-['●']" : "text-gray-500 before:text-gray-300 before:content-['○']"} before:absolute before:left-0 before:text-[0.7rem]`}>Una letra mayúscula</li>
                  <li className={`relative pl-5 text-xs leading-relaxed ${/[a-z]/.test(formData.password) ? "text-primary before:text-primary before:content-['●']" : "text-gray-500 before:text-gray-300 before:content-['○']"} before:absolute before:left-0 before:text-[0.7rem]`}>Una letra minúscula</li>
                  <li className={`relative pl-5 text-xs leading-relaxed ${/[0-9]/.test(formData.password) ? "text-primary before:text-primary before:content-['●']" : "text-gray-500 before:text-gray-300 before:content-['○']"} before:absolute before:left-0 before:text-[0.7rem]`}>Un número</li>
                  <li className={`relative pl-5 text-xs leading-relaxed ${/[^A-Za-z0-9]/.test(formData.password) ? "text-primary before:text-primary before:content-['●']" : "text-gray-500 before:text-gray-300 before:content-['○']"} before:absolute before:left-0 before:text-[0.7rem]`}>Un carácter especial</li>
                </ul>

                <button
                  type="submit"
                  className={`mt-2 w-full rounded-lg py-2.5 text-base font-bold text-white transition-all active:scale-[0.98] ${
                    !isFormComplete || loading
                      ? "cursor-not-allowed bg-gray-400 opacity-70"
                      : "bg-primary hover:bg-primary-light"
                  }`}
                  disabled={!isFormComplete || loading}
                >
                  {loading ? "Restableciendo..." : "Restablecer contraseña"}
                </button>
              </form>

              <div className="mt-5 flex justify-center">
                <Link to="/login" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">← Volver al inicio de sesión</Link>
              </div>
            </>
          ) : (
            <div className="text-center">
              <div className="mb-3 text-5xl" aria-hidden="true">✅</div>
              <h2 className="mb-0.5 text-center text-xl font-bold text-primary">¡Contraseña restablecida!</h2>
              <p className="mb-6 text-center text-sm leading-relaxed text-gray-500">
                Tu contraseña se ha cambiado correctamente. Ya puedes iniciar
                sesión con tu nueva contraseña.
              </p>

              <Link
                to="/login"
                className="block w-full rounded-lg bg-primary py-2.5 text-center text-base font-bold text-white no-underline transition-colors hover:bg-primary-light hover:text-white"
              >
                Ir a iniciar sesión
              </Link>
            </div>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
