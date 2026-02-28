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
import { loginUser } from "../api/auth";
import "./LoginPage.css";

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
      const tokens = await loginUser({
        email: formData.email,
        password: formData.password,
      });
      // Guardar tokens en localStorage
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      // Redirigir al dashboard (por ahora a /)
      navigate("/");
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setServerError(
          axiosErr.response?.data?.detail || "Error al iniciar sesión."
        );
      } else {
        setServerError("Error de conexión. Verifique que el servidor esté activo.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout headerActionLabel="Registrarse" headerActionTo="/register">
      <div className="login">
        <div className="login__card">
          <h2 className="login__title">Iniciar sesión</h2>
          <p className="login__subtitle">
            Ingresa tus credenciales para acceder a BoviTrack
          </p>

          {justRegistered && (
            <div className="login__success">Cuenta creada exitosamente. Inicia sesión.</div>
          )}
          {serverError && (
            <div className="login__server-error">{serverError}</div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="login__field">
              <label htmlFor="email">Correo electrónico <span className="login__required">*</span></label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="correo@ejemplo.com"
                value={formData.email}
                onChange={handleChange}
              />
              {errors.email && <span className="login__error">{errors.email}</span>}
            </div>

            <div className="login__field">
              <label htmlFor="password">Contraseña <span className="login__required">*</span></label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="Ingrese su contraseña"
                value={formData.password}
                onChange={handleChange}
              />
              {errors.password && <span className="login__error">{errors.password}</span>}
            </div>

            <button
              type="submit"
              className={`login__btn${!isFormComplete || loading ? " login__btn--disabled" : ""}`}
              disabled={!isFormComplete || loading}
            >
              {loading ? "Ingresando..." : "Iniciar sesión"}
            </button>
          </form>

          {/* Enlaces bajo el botón */}
          <div className="login__links">
            <Link to="/forgot-password">¿Olvidaste tu contraseña?</Link>
            <Link to="/register">¿No estás registrado?</Link>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
