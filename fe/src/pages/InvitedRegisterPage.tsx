/**
 * Archivo: pages/InvitedRegisterPage.tsx
 * Descripción: Página de registro para empleados invitados a una finca.
 */

import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { getInvitationInfo, registerInvited, type InvitationInfo } from "../api/auth";

const DOCUMENT_TYPES = [
  { value: "", label: "Seleccione..." },
  { value: "CC", label: "Cédula de Ciudadanía" },
  { value: "CE", label: "Cédula de Extranjería" },
  { value: "TI", label: "Tarjeta de Identidad" },
  { value: "PP", label: "Pasaporte" },
  { value: "NIT", label: "NIT" },
];

export function InvitedRegisterPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const navigate = useNavigate();

  const [invitation, setInvitation] = useState<InvitationInfo | null>(null);
  const [loadingInvitation, setLoadingInvitation] = useState(true);
  const [invitationError, setInvitationError] = useState("");

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    documentType: "",
    documentNumber: "",
    phone: "",
    password: "",
    confirmPassword: "",
    acceptTerms: false,
    acceptDataPolicy: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState("");
  const [success, setSuccess] = useState(false);

  const TEXT_ONLY = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/;

  useEffect(() => {
    if (!token) {
      setInvitationError("No se encontró el token de invitación");
      setLoadingInvitation(false);
      return;
    }
    getInvitationInfo(token)
      .then(setInvitation)
      .catch(() => setInvitationError("Invitación inválida o expirada"))
      .finally(() => setLoadingInvitation(false));
  }, [token]);

  const isFormComplete =
    formData.firstName.trim() !== "" &&
    formData.lastName.trim() !== "" &&
    formData.documentType !== "" &&
    formData.documentNumber.trim() !== "" &&
    formData.phone.trim() !== "" &&
    formData.password !== "" &&
    formData.confirmPassword !== "" &&
    formData.acceptTerms &&
    formData.acceptDataPolicy;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => { const copy = { ...prev }; delete copy[name]; return copy; });
    }
  };

  const handleCheck = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: checked }));
    if (errors[name]) {
      setErrors((prev) => { const copy = { ...prev }; delete copy[name]; return copy; });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!formData.firstName.trim()) newErrors.firstName = "Los nombres son obligatorios";
    else if (!TEXT_ONLY.test(formData.firstName)) newErrors.firstName = "Solo se permiten letras";

    if (!formData.lastName.trim()) newErrors.lastName = "Los apellidos son obligatorios";
    else if (!TEXT_ONLY.test(formData.lastName)) newErrors.lastName = "Solo se permiten letras";

    if (!formData.documentType) newErrors.documentType = "Seleccione un tipo de documento";
    if (!formData.documentNumber.trim()) newErrors.documentNumber = "El número de documento es obligatorio";
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setServerError("");

    try {
      await registerInvited({
        token,
        first_name: formData.firstName,
        last_name: formData.lastName,
        document_type: formData.documentType,
        document_number: formData.documentNumber,
        phone: formData.phone,
        password: formData.password,
        accept_terms: formData.acceptTerms,
        accept_data_policy: formData.acceptDataPolicy,
      });
      setSuccess(true);
    } catch (err: unknown) {
      setServerError(
        err instanceof Error ? err.message : "Error al registrarse. Intente de nuevo."
      );
    } finally {
      setLoading(false);
    }
  };

  if (loadingInvitation) {
    return (
      <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
        <div className="text-center text-gray-500">Cargando invitación...</div>
      </AuthLayout>
    );
  }

  if (invitationError || !invitation) {
    return (
      <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
        <div className="flex w-full max-w-md flex-col items-center rounded-2xl bg-white p-8 shadow-lg">
          <div className="mb-4 text-4xl">⚠️</div>
          <h2 className="mb-2 text-lg font-bold text-gray-900">Invitación no válida</h2>
          <p className="mb-4 text-center text-sm text-gray-500">
            {invitationError || "No se pudo cargar la invitación"}
          </p>
          <Link to="/login" className="rounded-lg bg-primary px-6 py-2 text-sm font-bold text-white hover:bg-primary-light">
            Ir a iniciar sesión
          </Link>
        </div>
      </AuthLayout>
    );
  }

  if (success) {
    return (
      <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
        <div className="flex w-full max-w-md flex-col items-center rounded-2xl bg-white p-8 shadow-lg">
          <div className="mb-4 text-4xl">✅</div>
          <h2 className="mb-2 text-lg font-bold text-gray-900">¡Registro exitoso!</h2>
          <p className="mb-4 text-center text-sm text-gray-500">
            Tu cuenta ha sido creada y ya estás vinculado a la finca <strong>{invitation.farm_name}</strong>.
          </p>
          <button
            onClick={() => navigate("/login")}
            className="rounded-lg bg-primary px-6 py-2 text-sm font-bold text-white hover:bg-primary-light"
          >
            Iniciar sesión
          </button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout headerActionLabel="Iniciar sesión" headerActionTo="/login">
      <div className="flex w-full max-w-[620px] flex-col overflow-hidden rounded-2xl bg-white shadow-lg">
        <div className="px-7 py-5">
          {/* Info de la invitación */}
          <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3">
            <p className="text-sm text-blue-800">
              <strong>{invitation.inviter_name ?? "Un administrador"}</strong> te invitó a unirte a la finca{" "}
              <strong>{invitation.farm_name}</strong> como <strong>{invitation.role_name}</strong>.
            </p>
            <p className="mt-1 text-xs text-blue-600">Correo: {invitation.email}</p>
          </div>

          <h2 className="mb-0.5 text-xl font-bold text-primary">Completar registro</h2>
          <p className="mb-3 text-sm text-gray-500">Completa tus datos para unirte a la finca</p>

          {serverError && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">{serverError}</div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            {/* Nombres y Apellidos */}
            <div className="mb-2 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
              <div className="flex flex-col">
                <label htmlFor="firstName" className="mb-0.5 text-xs font-semibold text-gray-800">Nombres <span className="font-bold text-red-600">*</span></label>
                <input id="firstName" name="firstName" type="text" placeholder="Ingrese sus nombres" value={formData.firstName} onChange={handleChange}
                  className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-2.5 py-1.5 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10" />
                {errors.firstName && <span className="mt-0.5 text-xs text-red-600">{errors.firstName}</span>}
              </div>
              <div className="flex flex-col">
                <label htmlFor="lastName" className="mb-0.5 text-xs font-semibold text-gray-800">Apellidos <span className="font-bold text-red-600">*</span></label>
                <input id="lastName" name="lastName" type="text" placeholder="Ingrese sus apellidos" value={formData.lastName} onChange={handleChange}
                  className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-2.5 py-1.5 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10" />
                {errors.lastName && <span className="mt-0.5 text-xs text-red-600">{errors.lastName}</span>}
              </div>
            </div>

            {/* Tipo y Número de Documento */}
            <div className="mb-2 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
              <div className="flex flex-col">
                <label htmlFor="documentType" className="mb-0.5 text-xs font-semibold text-gray-800">Tipo de documento <span className="font-bold text-red-600">*</span></label>
                <select id="documentType" name="documentType" value={formData.documentType} onChange={handleChange}
                  className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-2.5 py-1.5 text-sm text-gray-800 outline-none transition-colors focus:border-primary focus:ring-2 focus:ring-primary/10">
                  {DOCUMENT_TYPES.map((dt) => (<option key={dt.value} value={dt.value}>{dt.label}</option>))}
                </select>
                {errors.documentType && <span className="mt-0.5 text-xs text-red-600">{errors.documentType}</span>}
              </div>
              <div className="flex flex-col">
                <label htmlFor="documentNumber" className="mb-0.5 text-xs font-semibold text-gray-800">Número de documento <span className="font-bold text-red-600">*</span></label>
                <input id="documentNumber" name="documentNumber" type="text" placeholder="Ingrese su número" value={formData.documentNumber} onChange={handleChange}
                  className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-2.5 py-1.5 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10" />
                {errors.documentNumber && <span className="mt-0.5 text-xs text-red-600">{errors.documentNumber}</span>}
              </div>
            </div>

            {/* Teléfono */}
            <div className="mb-2">
              <div className="flex flex-col">
                <label htmlFor="phone" className="mb-0.5 text-xs font-semibold text-gray-800">Teléfono <span className="font-bold text-red-600">*</span></label>
                <input id="phone" name="phone" type="tel" placeholder="+57 300 123 4567" value={formData.phone} onChange={handleChange}
                  className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-2.5 py-1.5 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10" />
                {errors.phone && <span className="mt-0.5 text-xs text-red-600">{errors.phone}</span>}
              </div>
            </div>

            {/* Contraseña y Verificar */}
            <div className="mb-2 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
              <div className="flex flex-col">
                <label htmlFor="password" className="mb-0.5 text-xs font-semibold text-gray-800">Contraseña <span className="font-bold text-red-600">*</span></label>
                <input id="password" name="password" type="password" placeholder="Mínimo 8 caracteres" value={formData.password} onChange={handleChange}
                  className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-2.5 py-1.5 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10" />
                {errors.password && <span className="mt-0.5 text-xs text-red-600">{errors.password}</span>}
                {formData.password && (
                  <ul className="mt-1.5 list-none space-y-0.5 p-0 text-xs">
                    <li className={formData.password.length >= 8 ? "text-green-600 before:mr-1 before:content-['✓']" : "text-gray-400 before:mr-1 before:content-['✗']"}>Mínimo 8 caracteres</li>
                    <li className={/[A-Z]/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-gray-400 before:mr-1 before:content-['✗']"}>Una letra mayúscula</li>
                    <li className={/[a-z]/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-gray-400 before:mr-1 before:content-['✗']"}>Una letra minúscula</li>
                    <li className={/\d/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-gray-400 before:mr-1 before:content-['✗']"}>Un número</li>
                    <li className={/[^A-Za-z0-9]/.test(formData.password) ? "text-green-600 before:mr-1 before:content-['✓']" : "text-gray-400 before:mr-1 before:content-['✗']"}>Un carácter especial</li>
                  </ul>
                )}
              </div>
              <div className="flex flex-col">
                <label htmlFor="confirmPassword" className="mb-0.5 text-xs font-semibold text-gray-800">Verificar contraseña <span className="font-bold text-red-600">*</span></label>
                <input id="confirmPassword" name="confirmPassword" type="password" placeholder="Repita la contraseña" value={formData.confirmPassword} onChange={handleChange}
                  className="rounded-lg border-[1.5px] border-gray-300 bg-surface px-2.5 py-1.5 text-sm text-gray-800 outline-none transition-colors placeholder:text-gray-400 focus:border-primary focus:ring-2 focus:ring-primary/10" />
                {errors.confirmPassword && <span className="mt-0.5 text-xs text-red-600">{errors.confirmPassword}</span>}
              </div>
            </div>

            {/* Checkboxes */}
            <div className="mb-2.5">
              <label className="mb-1 flex cursor-pointer items-start gap-1.5 text-xs text-gray-800">
                <input type="checkbox" name="acceptTerms" checked={formData.acceptTerms} onChange={handleCheck} className="mt-0.5 h-3.5 w-3.5 cursor-pointer accent-primary" />
                <span>Acepto los{" "}<a href="/terms" target="_blank" rel="noopener noreferrer" className="font-semibold text-primary underline hover:text-primary-light">términos y condiciones</a></span>
              </label>
              {errors.acceptTerms && <span className="text-xs text-red-600">{errors.acceptTerms}</span>}

              <label className="mb-1 flex cursor-pointer items-start gap-1.5 text-xs text-gray-800">
                <input type="checkbox" name="acceptDataPolicy" checked={formData.acceptDataPolicy} onChange={handleCheck} className="mt-0.5 h-3.5 w-3.5 cursor-pointer accent-primary" />
                <span>Autorizo el{" "}<a href="/privacy" target="_blank" rel="noopener noreferrer" className="font-semibold text-primary underline hover:text-primary-light">tratamiento de mis datos personales</a></span>
              </label>
              {errors.acceptDataPolicy && <span className="text-xs text-red-600">{errors.acceptDataPolicy}</span>}
            </div>

            <button
              type="submit"
              className={`w-full rounded-lg py-2 text-sm font-bold text-white transition-all active:scale-[0.98] ${
                !isFormComplete || loading ? "cursor-not-allowed bg-gray-400 opacity-70" : "bg-primary hover:bg-primary-light"
              }`}
              disabled={!isFormComplete || loading}
            >
              {loading ? "Registrando..." : "Completar registro"}
            </button>
          </form>

          <p className="mt-2.5 text-center text-sm text-gray-500">
            ¿Ya tienes cuenta?{" "}
            <Link to="/login" className="font-semibold text-primary hover:text-primary-light">Inicia sesión</Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
}
