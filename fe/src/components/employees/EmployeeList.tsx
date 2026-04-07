import { useEffect, useState } from "react";
import {
  listEmployees,
  listRoles,
  updateEmployee,
  removeEmployee,
  type EmployeeResponse,
  type RoleOption,
} from "../../api/employees";
import AssignEmployeeModal from "./AssignEmployeeModal";

interface Props {
  farmId: string;
}

export default function EmployeeList({ farmId }: Props) {
  const [employees, setEmployees] = useState<EmployeeResponse[]>([]);
  const [roles, setRoles] = useState<RoleOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState<"all" | "active" | "inactive">("all");
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [changingRole, setChangingRole] = useState<string | null>(null);

  const fetchEmployees = async () => {
    setLoading(true);
    setError("");
    try {
      const isActive = filter === "all" ? undefined : filter === "active";
      const [data, rolesData] = await Promise.all([
        listEmployees(farmId, isActive),
        listRoles(farmId),
      ]);
      setEmployees(data);
      setRoles(rolesData);
    } catch {
      setError("No se pudieron cargar los empleados");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [farmId, filter]);

  const toggleActive = async (emp: EmployeeResponse) => {
    setActionLoading(emp.user_id);
    try {
      await updateEmployee(farmId, emp.user_id, { is_active: !emp.is_active });
      await fetchEmployees();
    } catch {
      setError("No se pudo actualizar el empleado");
    } finally {
      setActionLoading(null);
    }
  };

  const handleRemove = async (emp: EmployeeResponse) => {
    if (!confirm(`¿Desvincular a ${emp.first_name} ${emp.last_name} de la finca?`)) return;
    setActionLoading(emp.user_id);
    try {
      await removeEmployee(farmId, emp.user_id);
      await fetchEmployees();
    } catch {
      setError("No se pudo desvincular al empleado");
    } finally {
      setActionLoading(null);
    }
  };

  const handleRoleChange = async (emp: EmployeeResponse, newRoleId: string) => {
    if (newRoleId === emp.role_id) { setChangingRole(null); return; }
    setActionLoading(emp.user_id);
    try {
      await updateEmployee(farmId, emp.user_id, { role_id: newRoleId });
      await fetchEmployees();
    } catch {
      setError("No se pudo cambiar el rol");
    } finally {
      setActionLoading(null);
      setChangingRole(null);
    }
  };

  const handleAssignSuccess = () => {
    setShowModal(false);
    fetchEmployees();
  };

  const activeCount = employees.filter((e) => e.is_active).length;
  const inactiveCount = employees.filter((e) => !e.is_active).length;

  return (
    <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Empleados</h2>
          <p className="text-xs text-gray-400">
            {activeCount} activo{activeCount !== 1 ? "s" : ""} · {inactiveCount} inactivo
            {inactiveCount !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light"
        >
          + Asignar empleado
        </button>
      </div>

      {/* Filtros */}
      <div className="mb-4 flex gap-2">
        {(["all", "active", "inactive"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              filter === f
                ? "bg-primary text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {f === "all" ? "Todos" : f === "active" ? "Activos" : "Inactivos"}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : employees.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-200 py-10 text-center">
          <p className="text-sm text-gray-400">No hay empleados en esta categoría</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">
                <th className="pb-2 pr-4">Nombre</th>
                <th className="pb-2 pr-4">Correo</th>
                <th className="pb-2 pr-4">Documento</th>
                <th className="pb-2 pr-4">Rol</th>
                <th className="pb-2 pr-4">Estado</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {employees.map((emp) => (
                <tr key={emp.id} className="hover:bg-gray-50">
                  <td className="py-3 pr-4 font-medium text-gray-800">
                    {emp.first_name} {emp.last_name}
                  </td>
                  <td className="py-3 pr-4 text-gray-600">{emp.email}</td>
                  <td className="py-3 pr-4 text-gray-500">
                    {emp.document_type} {emp.document_number}
                  </td>
                  <td className="py-3 pr-4">
                    {changingRole === emp.user_id ? (
                      <select
                        defaultValue={emp.role_id}
                        onChange={(e) => handleRoleChange(emp, e.target.value)}
                        onBlur={() => setChangingRole(null)}
                        autoFocus
                        className="rounded-lg border border-gray-200 px-2 py-0.5 text-xs focus:border-primary focus:outline-none"
                      >
                        {roles.map((r) => (
                          <option key={r.id} value={r.id}>{r.name}</option>
                        ))}
                      </select>
                    ) : (
                      <button
                        onClick={() => setChangingRole(emp.user_id)}
                        className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700 hover:bg-blue-100"
                        title="Clic para cambiar rol"
                      >
                        {emp.role_name}
                      </button>
                    )}
                  </td>
                  <td className="py-3 pr-4">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        emp.is_active
                          ? "bg-green-50 text-green-700"
                          : "bg-gray-100 text-gray-500"
                      }`}
                    >
                      {emp.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => toggleActive(emp)}
                        disabled={actionLoading === emp.user_id}
                        className="rounded px-2 py-1 text-xs font-medium text-gray-500 hover:bg-gray-100 disabled:opacity-50"
                      >
                        {emp.is_active ? "Desactivar" : "Activar"}
                      </button>
                      <button
                        onClick={() => handleRemove(emp)}
                        disabled={actionLoading === emp.user_id}
                        className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50"
                      >
                        Desvincular
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <AssignEmployeeModal
          farmId={farmId}
          onSuccess={handleAssignSuccess}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
