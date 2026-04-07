/**
 * Archivo: pages/LoginPage.tsx
 * Descripción: Página de inicio de sesión de BoviTrack.
 * ¿Para qué? Permitir que usuarios registrados accedan al sistema.
 * Campos: correo electrónico, contraseña.
 * Enlaces: "¿Olvidaste tu contraseña?" y "¿No estás registrado?"
 */

import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const justRegistered = (location.state as { registered?: boolean })?.registered;

  /** ¿Están todos los campos llenos? */
  const isFormComplete =
    formData.email.trim() !== "" &&
    formData.password !== "";

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

    if (!formData.email.trim()) {
      newErrors.email = "El correo es obligatorio";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Ingrese un correo válido (ej: correo@ejemplo.com)";
    }

    if (!formData.password) {
      newErrors.password = "La contraseña es obligatoria";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /** Envío del formulario — conectado al backend */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setServerError("");

    try {
      await login(formData.email, formData.password);
      navigate("/dashboard");
    } catch (err: unknown) {
      setServerError(
        err instanceof Error ? err.message : "Error al iniciar sesión."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout headerActionLabel="Registrarse" headerActionTo="/register">
      <div className="flex w-full items-center justify-center">
        <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
          <h2 className="mb-0.5 text-xl font-bold text-primary">Iniciar sesión</h2>
          <p className="mb-6 text-sm text-gray-500">
            Ingresa tus credenciales para acceder a BoviTrack
          </p>

          {justRegistered && (
            <div className="mb-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-center text-sm text-green-600">Cuenta creada exitosamente. Inicia sesión.</div>
          )}
          {serverError && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">{serverError}</div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="mb-4 flex flex-col">
              <label htmlFor="email" className="mb-1 text-sm font-semibold text-gray-800">Correo electrónico <span className="font-bold text-red-600">*</span></label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="correo@ejemplo.com"
                value={formData.email}
                onChange={handleChange}
                className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-3 py-2 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10"
              />
              {errors.email && <span className="mt-0.5 text-xs text-red-600">{errors.email}</span>}
            </div>

            <div className="mb-4 flex flex-col">
              <label htmlFor="password" className="mb-1 text-sm font-semibold text-gray-800">Contraseña <span className="font-bold text-red-600">*</span></label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="Ingrese su contraseña"
                value={formData.password}
                onChange={handleChange}
                className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-3 py-2 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10"
              />
              {errors.password && <span className="mt-0.5 text-xs text-red-600">{errors.password}</span>}
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
              {loading ? "Ingresando..." : "Iniciar sesión"}
            </button>
          </form>

          {/* Enlaces bajo el botón */}
          <div className="mt-5 flex flex-col items-center gap-2 sm:flex-row sm:justify-between">
            <Link to="/forgot-password" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">¿Olvidaste tu contraseña?</Link>
            <Link to="/register" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">¿No estás registrado?</Link>
          </div>

          {/* Reactivación */}
          {serverError && serverError.includes("desactivada") && (
            <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-center">
              <p className="text-sm text-amber-700">Tu cuenta está desactivada.</p>
              <Link to="/request-reactivation" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">
                Solicitar reactivación
              </Link>
            </div>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
