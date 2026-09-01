import { useEffect, useState } from "react";
import {
  listEmployees,
  listRoles,
  updateEmployee,
  removeEmployee,
  setAccountStatus,
  type EmployeeResponse,
  type RoleOption,
} from "../../api/employees";
import { getApiErrorMessage } from "../../api/errors";
import { useAuth } from "../../hooks/useAuth";
import { useTable } from "../../hooks/useTable";
import Pagination from "../Pagination";
import AssignEmployeeModal from "./AssignEmployeeModal";

interface Props {
  farmId: string;
}

export default function EmployeeList({ farmId }: Props) {
  const { user } = useAuth();
  const isAdmin = user?.role_name === "Administrador";
  const [employees, setEmployees] = useState<EmployeeResponse[]>([]);
  const [roles, setRoles] = useState<RoleOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState<"all" | "active" | "inactive">("all");
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [changingRole, setChangingRole] = useState<string | null>(null);

  const getValue = (emp: EmployeeResponse, key: string): string | number => {
    const v = (emp as unknown as Record<string, unknown>)[key];
    return typeof v === "number" ? v : String(v ?? "");
  };

  const { page, pageCount, start, end, total, paginated, setPage, sortKey, sortDir, handleSort } =
    useTable<EmployeeResponse>(employees, { getValue });

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
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudieron cargar los empleados"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setPage(1); }, [farmId, filter, setPage]);
  useEffect(() => {
    fetchEmployees();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [farmId, filter]);

  const getApiError = (err: unknown): string => getApiErrorMessage(err, "");

  const toggleActive = async (emp: EmployeeResponse) => {
    setActionLoading(emp.user_id);
    try {
      await updateEmployee(farmId, emp.user_id, { is_active: !emp.is_active });
      await fetchEmployees();
    } catch (err) {
      setError(getApiError(err) || "No se pudo actualizar el empleado");
    } finally {
      setActionLoading(null);
    }
  };

  const toggleAccount = async (emp: EmployeeResponse) => {
    const nombre = `${emp.first_name} ${emp.last_name}`;
    if (emp.account_active) {
      const alcance =
        emp.other_farms_count > 0
          ? `\n\nATENCIÓN: también trabaja en ${emp.other_farms_count} finca(s) más y perderá el acceso a todas.`
          : "";
      if (
        !confirm(
          `¿Cerrar la cuenta de ${nombre}?\n\n` +
            `No podrá volver a iniciar sesión en BoviTrack y se cerrarán sus sesiones abiertas. ` +
            `Sigue vinculado a la finca y sus registros se conservan.${alcance}`
        )
      )
        return;
    } else if (!confirm(`¿Reabrir la cuenta de ${nombre}? Podrá volver a iniciar sesión.`)) {
      return;
    }

    setActionLoading(emp.user_id);
    try {
      await setAccountStatus(farmId, emp.user_id, { is_active: !emp.account_active });
      await fetchEmployees();
    } catch (err) {
      setError(getApiError(err) || "No se pudo cambiar el estado de la cuenta");
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
    } catch (err) {
      setError(getApiError(err) || "No se pudo desvincular al empleado");
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
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "No se pudo cambiar el rol"));
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
  // Cuentas cerradas: no pueden iniciar sesión, aunque sigan vinculadas a la finca.
  const disabledAccountCount = employees.filter((e) => !e.account_active).length;

  return (
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-text-primary">Empleados</h2>
          <p className="text-xs text-text-muted">
            {activeCount} activo{activeCount !== 1 ? "s" : ""} · {inactiveCount} inactivo
            {inactiveCount !== 1 ? "s" : ""} en la finca
            {disabledAccountCount > 0 && (
              <>
                {" · "}
                <span className="font-medium text-red-600">
                  {disabledAccountCount} con la cuenta desactivada
                </span>
              </>
            )}
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
                : "bg-surface-alt text-text-secondary hover:bg-border"
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
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">No hay empleados en esta categoría</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("first_name")} className="uppercase">Nombre {sortKey === "first_name" && (sortDir === "asc" ? "▲" : "▼")}</button>
                </th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("email")} className="uppercase">Correo {sortKey === "email" && (sortDir === "asc" ? "▲" : "▼")}</button>
                </th>
                <th className="pb-2 pr-4">Documento</th>
                <th className="pb-2 pr-4">
                  <button onClick={() => handleSort("role_name")} className="uppercase">Rol {sortKey === "role_name" && (sortDir === "asc" ? "▲" : "▼")}</button>
                </th>
                <th className="pb-2 pr-4">Estado</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginated.map((emp) => (
                <tr key={emp.id} className="hover:bg-surface-alt">
                  <td className="py-3 pr-4 font-medium text-text-primary">
                    {emp.first_name} {emp.last_name}
                  </td>
                  <td className="py-3 pr-4 text-text-secondary">{emp.email}</td>
                  <td className="py-3 pr-4 text-text-secondary">
                    {emp.document_type} {emp.document_number}
                  </td>
                  <td className="py-3 pr-4">
                    {changingRole === emp.user_id ? (
                      <select
                        defaultValue={emp.role_id}
                        onChange={(e) => handleRoleChange(emp, e.target.value)}
                        onBlur={() => setChangingRole(null)}
                        autoFocus
                        className="rounded-lg border border-border px-2 py-0.5 text-xs focus:border-primary focus:outline-none"
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
                    {/* Tres estados posibles. La cuenta desactivada manda sobre el
                        vínculo con la finca: sin cuenta activa no puede entrar al
                        sistema, esté o no vinculado aquí. */}
                    {!emp.account_active ? (
                      <span
                        className="rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700"
                        title="La cuenta del usuario está desactivada: no puede iniciar sesión en el sistema."
                      >
                        Cuenta desactivada
                      </span>
                    ) : (
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          emp.is_active
                            ? "bg-green-50 text-green-700"
                            : "bg-surface-alt text-text-secondary"
                        }`}
                        title={
                          emp.is_active
                            ? "Activo en esta finca."
                            : "Sin acceso a esta finca. Puede iniciar sesión, pero no ve sus datos."
                        }
                      >
                        {emp.is_active ? "Activo" : "Inactivo en la finca"}
                      </span>
                    )}
                  </td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => toggleActive(emp)}
                        disabled={actionLoading === emp.user_id}
                        title={
                          emp.is_active
                            ? "Le quita el acceso a esta finca. No cierra su cuenta: podrá seguir iniciando sesión."
                            : "Le devuelve el acceso a esta finca."
                        }
                        className="rounded px-2 py-1 text-xs font-medium text-text-secondary hover:bg-surface-alt disabled:opacity-50"
                      >
                        {emp.is_active ? "Desactivar" : "Activar"}
                      </button>
                      {/* Solo el administrador puede cerrar/reabrir cuentas: la
                          acción alcanza a todas las fincas de esa persona. */}
                      {isAdmin && emp.user_id !== user?.id && (
                        <button
                          onClick={() => toggleAccount(emp)}
                          disabled={actionLoading === emp.user_id}
                          title={
                            emp.account_active
                              ? "Le impide iniciar sesión en BoviTrack, en esta finca y en cualquier otra."
                              : "Le permite volver a iniciar sesión en BoviTrack."
                          }
                          className="rounded px-2 py-1 text-xs font-medium text-amber-600 hover:bg-amber-50 disabled:opacity-50"
                        >
                          {emp.account_active ? "Cerrar cuenta" : "Reabrir cuenta"}
                        </button>
                      )}
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
          <div className="mt-4">
            <Pagination page={page} pageCount={pageCount} start={start} end={end} total={total} onChange={(p) => setPage(p)} />
          </div>
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
