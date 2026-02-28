/**
 * Archivo: pages/RegisterPage.tsx
 * Descripción: Página de registro de BoviTrack.
 * ¿Para qué? Permitir que nuevos usuarios creen una cuenta en el sistema.
 * Campos: nombres, apellidos, tipo doc, num doc, email, teléfono,
 *         contraseña, verificar contraseña, T&C, autorización datos.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { registerUser } from "../api/auth";
import "./RegisterPage.css";

/** Tipos de documento disponibles */
const DOCUMENT_TYPES = [
  { value: "", label: "Seleccione..." },
  { value: "CC", label: "Cédula de Ciudadanía" },
  { value: "CE", label: "Cédula de Extranjería" },
  { value: "TI", label: "Tarjeta de Identidad" },
  { value: "PP", label: "Pasaporte" },
  { value: "NIT", label: "NIT" },
];

export function RegisterPage() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    documentType: "",
    documentNumber: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
    acceptTerms: false,
    acceptDataPolicy: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState("");
  const navigate = useNavigate();

  /** Regex: solo letras, espacios y tildes */
  const TEXT_ONLY = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/;

  /** ¿Todos los campos obligatorios están llenos y checkboxes marcados? */
  const isFormComplete =
    formData.firstName.trim() !== "" &&
    formData.lastName.trim() !== "" &&
    formData.documentType !== "" &&
    formData.documentNumber.trim() !== "" &&
    formData.email.trim() !== "" &&
    formData.phone.trim() !== "" &&
    formData.password !== "" &&
    formData.confirmPassword !== "" &&
    formData.acceptTerms &&
    formData.acceptDataPolicy;

  /** Actualiza campos de texto / select */
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Limpiar error del campo al escribir
    if (errors[name]) {
      setErrors((prev) => {
        const copy = { ...prev };
        delete copy[name];
        return copy;
      });
    }
  };

  /** Actualiza checkboxes */
  const handleCheck = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: checked }));
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

    if (!formData.firstName.trim()) {
      newErrors.firstName = "Los nombres son obligatorios";
    } else if (!TEXT_ONLY.test(formData.firstName)) {
      newErrors.firstName = "Solo se permiten letras";
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = "Los apellidos son obligatorios";
    } else if (!TEXT_ONLY.test(formData.lastName)) {
      newErrors.lastName = "Solo se permiten letras";
    }

    if (!formData.documentType) newErrors.documentType = "Seleccione un tipo de documento";
    if (!formData.documentNumber.trim()) newErrors.documentNumber = "El número de documento es obligatorio";

    if (!formData.email.trim()) {
      newErrors.email = "El correo es obligatorio";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Ingrese un correo válido (ej: correo@ejemplo.com)";
    }

    if (!formData.phone.trim()) newErrors.phone = "El teléfono es obligatorio";

    if (!formData.password) {
      newErrors.password = "La contraseña es obligatoria";
    } else if (formData.password.length < 8) {
      newErrors.password = "Mínimo 8 caracteres";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Debe verificar la contraseña";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Las contraseñas no coinciden";
    }

    if (!formData.acceptTerms) newErrors.acceptTerms = "Debe aceptar los términos y condiciones";
    if (!formData.acceptDataPolicy) newErrors.acceptDataPolicy = "Debe autorizar el tratamiento de datos";

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
      await registerUser({
        email: formData.email,
        first_name: formData.firstName,
        last_name: formData.lastName,
        document_type: formData.documentType,
        document_number: formData.documentNumber,
        phone: formData.phone,
        password: formData.password,
      });
      // Registro exitoso — redirigir al login
      navigate("/login", { state: { registered: true } });
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setServerError(
          axiosErr.response?.data?.detail || "Error al registrarse. Intente de nuevo."
        );
      } else {
        setServerError("Error de conexión. Verifique que el servidor esté activo.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="register">
        {/* ── Tarjeta del formulario ── */}
        <div className="register__card">
          <h2 className="register__title">Crear cuenta</h2>
          <p className="register__subtitle">
            Completa los datos para registrarte en BoviTrack
          </p>

          {serverError && (
            <div className="register__server-error">{serverError}</div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            {/* Nombres y Apellidos */}
            <div className="register__row">
              <div className="register__field">
                <label htmlFor="firstName">Nombres <span className="register__required">*</span></label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  placeholder="Ingrese sus nombres"
                  value={formData.firstName}
                  onChange={handleChange}
                />
                {errors.firstName && <span className="register__error">{errors.firstName}</span>}
              </div>

              <div className="register__field">
                <label htmlFor="lastName">Apellidos <span className="register__required">*</span></label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  placeholder="Ingrese sus apellidos"
                  value={formData.lastName}
                  onChange={handleChange}
                />
                {errors.lastName && <span className="register__error">{errors.lastName}</span>}
              </div>
            </div>

            {/* Tipo y Número de Documento */}
            <div className="register__row">
              <div className="register__field">
                <label htmlFor="documentType">Tipo de documento <span className="register__required">*</span></label>
                <select
                  id="documentType"
                  name="documentType"
                  value={formData.documentType}
                  onChange={handleChange}
                >
                  {DOCUMENT_TYPES.map((dt) => (
                    <option key={dt.value} value={dt.value}>
                      {dt.label}
                    </option>
                  ))}
                </select>
                {errors.documentType && <span className="register__error">{errors.documentType}</span>}
              </div>

              <div className="register__field">
                <label htmlFor="documentNumber">Número de documento <span className="register__required">*</span></label>
                <input
                  id="documentNumber"
                  name="documentNumber"
                  type="text"
                  placeholder="Ingrese su número"
                  value={formData.documentNumber}
                  onChange={handleChange}
                />
                {errors.documentNumber && <span className="register__error">{errors.documentNumber}</span>}
              </div>
            </div>

            {/* Email y Teléfono */}
            <div className="register__row">
              <div className="register__field">
                <label htmlFor="email">Correo electrónico <span className="register__required">*</span></label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="correo@ejemplo.com"
                  value={formData.email}
                  onChange={handleChange}
                />
                {errors.email && <span className="register__error">{errors.email}</span>}
              </div>

              <div className="register__field">
                <label htmlFor="phone">Teléfono <span className="register__required">*</span></label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  placeholder="+57 300 123 4567"
                  value={formData.phone}
                  onChange={handleChange}
                />
                {errors.phone && <span className="register__error">{errors.phone}</span>}
              </div>
            </div>

            {/* Contraseña y Verificar */}
            <div className="register__row">
              <div className="register__field">
                <label htmlFor="password">Contraseña <span className="register__required">*</span></label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Mínimo 8 caracteres"
                  value={formData.password}
                  onChange={handleChange}
                />
                {errors.password && <span className="register__error">{errors.password}</span>}
              </div>

              <div className="register__field">
                <label htmlFor="confirmPassword">Verificar contraseña <span className="register__required">*</span></label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  placeholder="Repita la contraseña"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
                {errors.confirmPassword && <span className="register__error">{errors.confirmPassword}</span>}
              </div>
            </div>

            {/* Checkboxes */}
            <div className="register__checks">
              <label className="register__checkbox">
                <input
                  type="checkbox"
                  name="acceptTerms"
                  checked={formData.acceptTerms}
                  onChange={handleCheck}
                />
                <span>
                  Acepto los{" "}
                  <a href="#terminos" className="register__link">
                    términos y condiciones
                  </a>
                </span>
              </label>
              {errors.acceptTerms && <span className="register__error">{errors.acceptTerms}</span>}

              <label className="register__checkbox">
                <input
                  type="checkbox"
                  name="acceptDataPolicy"
                  checked={formData.acceptDataPolicy}
                  onChange={handleCheck}
                />
                <span>
                  Autorizo el{" "}
                  <a href="#datos" className="register__link">
                    tratamiento de mis datos personales
                  </a>
                </span>
              </label>
              {errors.acceptDataPolicy && <span className="register__error">{errors.acceptDataPolicy}</span>}
            </div>

            {/* Botón de registro */}
            <button
              type="submit"
              className={`register__btn${!isFormComplete || loading ? " register__btn--disabled" : ""}`}
              disabled={!isFormComplete || loading}
            >
              {loading ? "Registrando..." : "Registrarse"}
            </button>
          </form>

          {/* Enlace a login */}
          <p className="register__login-link">
            ¿Ya estás registrado?{" "}
            <Link to="/login">Inicia sesión</Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
}
