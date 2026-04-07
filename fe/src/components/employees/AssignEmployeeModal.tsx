import { useEffect, useState } from "react";
import { inviteEmployee, listRoles, type RoleOption } from "../../api/employees";

interface Props {
  farmId: string;
  onSuccess: () => void;
  onClose: () => void;
}

export default function AssignEmployeeModal({ farmId, onSuccess, onClose }: Props) {
  const [roles, setRoles] = useState<RoleOption[]>([]);
  const [email, setEmail] = useState("");
  const [roleId, setRoleId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    listRoles(farmId)
      .then(setRoles)
      .catch(() => setError("No se pudieron cargar los roles"));
  }, [farmId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !roleId) {
      setError("Correo y rol son obligatorios");
      return;
    }
    setLoading(true);
    setError("");
    setSuccessMsg("");
    try {
      await inviteEmployee(farmId, { email: email.trim(), role_id: roleId });
      setSuccessMsg(`Se envió una invitación a ${email.trim()}`);
      setTimeout(() => onSuccess(), 2000);
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : undefined;
      setError(msg ?? "No se pudo enviar la invitación");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-gray-900">Invitar empleado</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        {successMsg && (
          <div className="mb-4 rounded-lg bg-green-50 px-4 py-2 text-sm text-green-700">
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Correo del empleado
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="correo@ejemplo.com"
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              required
            />
            <p className="mt-1 text-xs text-gray-400">
              Se enviará un enlace de registro al correo ingresado
            </p>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Rol</label>
            <select
              value={roleId}
              onChange={(e) => setRoleId(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              required
            >
              <option value="">Seleccionar rol...</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading || !!successMsg}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-60"
            >
              {loading ? "Enviando..." : "Enviar invitación"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
