/**
 * Archivo: pages/RegisterPage.tsx
 * Descripción: Página de registro de BoviTrack.
 * Why? Permitir que nuevos usuarios creen una cuenta en el sistema.
 * Campos: nombres, apellidos, tipo doc, num doc, email, teléfono,
 *         contraseña, verificar contraseña, T&C, autorización datos.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { useAuth } from "../hooks/useAuth";

/** Tipos de documento disponibles */
const DOCUMENT_TYPES = [
  { value: "", label: "Seleccione..." },
  { value: "CC", label: "Cédula de Ciudadanía" },
  { value: "CE", label: "Cédula de Extranjería" },
  { value: "TI", label: "Tarjeta de Identidad" },
  { value: "PP", label: "Pasaporte" },
  { value: "NIT", label: "NIT" },
];

const STEPS = [
  { label: "Datos personales", subtitle: "Nombre y tipo de documento" },
  { label: "Contacto y seguridad", subtitle: "Correo, teléfono y contraseña" },
  { label: "Finalizar", subtitle: "Términos y condiciones" },
];

export function RegisterPage() {
  const [step, setStep] = useState(0);
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
  const { register } = useAuth();

  /** Regex: solo letras, espacios y tildes */
  const TEXT_ONLY = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/;

  const validateStep = (s: number): boolean => {
    const newErrors: Record<string, string> = {};
    if (s === 0) {
      if (!formData.firstName.trim()) newErrors.firstName = "Obligatorio";
      else if (!TEXT_ONLY.test(formData.firstName)) newErrors.firstName = "Solo letras";
      if (!formData.lastName.trim()) newErrors.lastName = "Obligatorio";
      else if (!TEXT_ONLY.test(formData.lastName)) newErrors.lastName = "Solo letras";
      if (!formData.documentType) newErrors.documentType = "Seleccione un tipo";
      if (!formData.documentNumber.trim()) newErrors.documentNumber = "Obligatorio";
    }
    if (s === 1) {
      if (!formData.email.trim()) newErrors.email = "Obligatorio";
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = "Correo inválido";
      if (!formData.phone.trim()) newErrors.phone = "Obligatorio";
      if (!formData.password) newErrors.password = "Obligatorio";
      else if (formData.password.length < 8) newErrors.password = "Mínimo 8 caracteres";
      else if (!/[A-Z]/.test(formData.password)) newErrors.password = "Debe tener mayúscula";
      else if (!/[a-z]/.test(formData.password)) newErrors.password = "Debe tener minúscula";
      else if (!/\d/.test(formData.password)) newErrors.password = "Debe tener número";
      else if (!/[^A-Za-z0-9]/.test(formData.password)) newErrors.password = "Debe tener carácter especial";
      if (!formData.confirmPassword) newErrors.confirmPassword = "Verifique la contraseña";
      else if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = "No coinciden";
    }
    if (s === 2) {
      if (!formData.acceptTerms) newErrors.acceptTerms = "Debe aceptar términos y condiciones";
      if (!formData.acceptDataPolicy) newErrors.acceptDataPolicy = "Debe autorizar tratamiento de datos";
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(step)) setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };

  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

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
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = "Debe contener al menos una mayúscula";
    } else if (!/[a-z]/.test(formData.password)) {
      newErrors.password = "Debe contener al menos una minúscula";
    } else if (!/\d/.test(formData.password)) {
      newErrors.password = "Debe contener al menos un número";
    } else if (!/[^A-Za-z0-9]/.test(formData.password)) {
      newErrors.password = "Debe contener al menos un carácter especial";
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
      await register({
        email: formData.email,
        first_name: formData.firstName,
        last_name: formData.lastName,
        document_type: formData.documentType,
        document_number: formData.documentNumber,
        phone: formData.phone,
        password: formData.password,
        accept_terms: formData.acceptTerms,
        accept_data_policy: formData.acceptDataPolicy,
      });
      // Registro + auto-login exitoso — ir al dashboard
      navigate("/dashboard");
    } catch (err: unknown) {
      setServerError(
        err instanceof Error ? err.message : "Error al registrarse. Intente de nuevo."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="flex w-full max-w-[620px] flex-col overflow-hidden rounded-2xl bg-surface shadow-lg">
        {/* ── Tarjeta del formulario ── */}
        <div className="px-7 py-5">
          <h2 className="mb-0.5 text-xl font-bold text-primary">Crear cuenta</h2>
          <p className="mb-3 text-sm text-text-secondary">
            Completa los datos para registrarte en BoviTrack
          </p>

          {serverError && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">{serverError}</div>
          )}

          {/* Step indicator */}
          <div className="mb-4 flex items-center gap-1.5">
            {STEPS.map((s, i) => (
              <button
                key={i}
                type="button"
                onClick={() => { if (i < step) setStep(i); }}
                disabled={i > step}
                className={`flex-1 rounded-lg px-2 py-1.5 text-center text-xs font-semibold transition-colors ${
                  i === step
                    ? "bg-primary text-white"
                    : i < step
                    ? "bg-green-100 text-green-700"
                    : "bg-surface-alt text-text-muted cursor-default"
                }`}
              >
                {i < step ? "✓ " : ""}{s.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} noValidate
            onKeyDown={(e) => {
              if (e.key === "Enter" && step < STEPS.length - 1) {
                e.preventDefault();
                nextStep();
              }
            }}>
            {step === 0 && (
              <>
                <div className="mb-2 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  <div className="flex flex-col">
                    <label htmlFor="firstName" className="mb-0.5 text-xs font-semibold text-text-primary">Nombres <span className="font-bold text-red-600">*</span></label>
                    <input id="firstName" name="firstName" type="text" required maxLength={100} placeholder="Ingrese sus nombres" value={formData.firstName} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10" />
                    <span className="mt-0.5 block text-right text-xs text-text-muted">{formData.firstName.length}/100</span>
                    {errors.firstName && <span className="mt-0.5 text-xs text-red-600">{errors.firstName}</span>}
                  </div>
                  <div className="flex flex-col">
                    <label htmlFor="lastName" className="mb-0.5 text-xs font-semibold text-text-primary">Apellidos <span className="font-bold text-red-600">*</span></label>
                    <input id="lastName" name="lastName" type="text" required maxLength={100} placeholder="Ingrese sus apellidos" value={formData.lastName} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10" />
                    <span className="mt-0.5 block text-right text-xs text-text-muted">{formData.lastName.length}/100</span>
                    {errors.lastName && <span className="mt-0.5 text-xs text-red-600">{errors.lastName}</span>}
                  </div>
                </div>
                <div className="mb-2 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  <div className="flex flex-col">
                    <label htmlFor="documentType" className="mb-0.5 text-xs font-semibold text-text-primary">Tipo de documento <span className="font-bold text-red-600">*</span></label>
                    <select id="documentType" name="documentType" value={formData.documentType} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/10">
                      {DOCUMENT_TYPES.map((dt) => (<option key={dt.value} value={dt.value}>{dt.label}</option>))}
                    </select>
                    {errors.documentType && <span className="mt-0.5 text-xs text-red-600">{errors.documentType}</span>}
                  </div>
                  <div className="flex flex-col">
                    <label htmlFor="documentNumber" className="mb-0.5 text-xs font-semibold text-text-primary">Número de documento <span className="font-bold text-red-600">*</span></label>
                    <input id="documentNumber" name="documentNumber" type="text" required maxLength={20} placeholder="Ingrese su número" value={formData.documentNumber} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10" />
                    {errors.documentNumber && <span className="mt-0.5 text-xs text-red-600">{errors.documentNumber}</span>}
                  </div>
                </div>
              </>
            )}

            {step === 1 && (
              <>
                <div className="mb-2 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  <div className="flex flex-col">
                    <label htmlFor="email" className="mb-0.5 text-xs font-semibold text-text-primary">Correo electrónico <span className="font-bold text-red-600">*</span></label>
                    <input id="email" name="email" type="email" required maxLength={255} placeholder="correo@ejemplo.com" value={formData.email} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10" />
                    {errors.email && <span className="mt-0.5 text-xs text-red-600">{errors.email}</span>}
                  </div>
                  <div className="flex flex-col">
                    <label htmlFor="phone" className="mb-0.5 text-xs font-semibold text-text-primary">Teléfono <span className="font-bold text-red-600">*</span></label>
                    <input id="phone" name="phone" type="tel" required maxLength={20} placeholder="+57 300 123 4567" value={formData.phone} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10" />
                    {errors.phone && <span className="mt-0.5 text-xs text-red-600">{errors.phone}</span>}
                  </div>
                </div>
                <div className="mb-2 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  <div className="flex flex-col">
                    <label htmlFor="password" className="mb-0.5 text-xs font-semibold text-text-primary">Contraseña <span className="font-bold text-red-600">*</span></label>
                    <input id="password" name="password" type="password" required maxLength={128} placeholder="Mínimo 8 caracteres" value={formData.password} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10" />
                    {errors.password && <span className="mt-0.5 text-xs text-red-600">{errors.password}</span>}
                    {formData.password && (
                      <ul className="mt-1.5 list-none space-y-0.5 p-0 text-xs">
                        <li className={formData.password.length >= 8 ? "text-green-600 before:mr-1 before:content-['✓']" : "text-text-muted before:mr-1 before:content-['✗']"}>Mínimo 8 caracteres</li>
                        <li className={/[A-Z]/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-text-muted before:mr-1 before:content-['✗']"}>Una letra mayúscula</li>
                        <li className={/[a-z]/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-text-muted before:mr-1 before:content-['✗']"}>Una letra minúscula</li>
                        <li className={/\d/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-text-muted before:mr-1 before:content-['✗']"}>Un número</li>
                        <li className={/[^A-Za-z0-9]/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-text-muted before:mr-1 before:content-['✗']"}>Un carácter especial</li>
                      </ul>
                    )}
                  </div>
                  <div className="flex flex-col">
                    <label htmlFor="confirmPassword" className="mb-0.5 text-xs font-semibold text-text-primary">Verificar contraseña <span className="font-bold text-red-600">*</span></label>
                    <input id="confirmPassword" name="confirmPassword" type="password" required maxLength={128} placeholder="Repita la contraseña" value={formData.confirmPassword} onChange={handleChange} className="rounded-lg border-[1.5px] border-border bg-surface px-2.5 py-1.5 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10" />
                    {errors.confirmPassword && <span className="mt-0.5 text-xs text-red-600">{errors.confirmPassword}</span>}
                  </div>
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <div className="mb-2.5">
                  <label className="mb-1 flex cursor-pointer items-start gap-1.5 text-xs text-text-primary">
                    <input type="checkbox" name="acceptTerms" checked={formData.acceptTerms} onChange={handleCheck} className="mt-0.5 h-3.5 w-3.5 cursor-pointer accent-primary" />
                    <span>Acepto los <a href="/terms" target="_blank" rel="noopener noreferrer" className="font-semibold text-primary underline hover:text-primary-light">términos y condiciones</a></span>
                  </label>
                  {errors.acceptTerms && <span className="text-xs text-red-600">{errors.acceptTerms}</span>}
                  <label className="mb-1 flex cursor-pointer items-start gap-1.5 text-xs text-text-primary">
                    <input type="checkbox" name="acceptDataPolicy" checked={formData.acceptDataPolicy} onChange={handleCheck} className="mt-0.5 h-3.5 w-3.5 cursor-pointer accent-primary" />
                    <span>Autorizo el <a href="/privacy" target="_blank" rel="noopener noreferrer" className="font-semibold text-primary underline hover:text-primary-light">tratamiento de mis datos personales</a></span>
                  </label>
                  {errors.acceptDataPolicy && <span className="text-xs text-red-600">{errors.acceptDataPolicy}</span>}
                </div>
              </>
            )}

            {/* Navigation buttons */}
            <div className="mt-4 flex gap-2">
              {step > 0 && (
                <button type="button" onClick={prevStep} className="flex-1 rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt transition-colors">
                  ← Anterior
                </button>
              )}
              {step < STEPS.length - 1 ? (
                <button key="paso-siguiente" type="button" onClick={nextStep} className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light transition-colors">
                  Siguiente →
                </button>
              ) : (
                <button key="paso-enviar" type="submit" disabled={!isFormComplete || loading}
                  className={`flex-1 rounded-lg py-2 text-sm font-bold text-white transition-all active:scale-[0.98] ${
                    !isFormComplete || loading ? "cursor-not-allowed bg-gray-400 opacity-70" : "bg-primary hover:bg-primary-light"
                  }`}
                >
                  {loading ? "Registrando..." : "Registrarse"}
                </button>
              )}
            </div>
          </form>

          {/* Enlace a login */}
          <p className="mt-2.5 text-center text-sm text-text-secondary">
            ¿Ya estás registrado?{" "}
            <Link to="/login" className="font-semibold text-primary hover:text-primary-light">Inicia sesión</Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
}
