import api from "./axios";

export interface RoleOption {
  id: string;
  name: string;
  description: string | null;
}

export interface EmployeeAssign {
  user_email: string;
  role_id: string;
}

export interface InviteEmployee {
  email: string;
  role_id: string;
}

export interface EmployeeUpdate {
  role_id?: string;
  is_active?: boolean;
}

export interface EmployeeResponse {
  id: string;
  user_id: string;
  farm_id: string;
  role_id: string;
  role_name: string;
  /** Vinculación a ESTA finca (user_farm.is_active). */
  is_active: boolean;
  /** Estado de la cuenta del usuario (users.is_active). Si es false no puede iniciar sesión. */
  account_active: boolean;
  /** Nº de OTRAS fincas activas donde trabaja. Cerrar la cuenta le quita el acceso a todas. */
  other_farms_count: number;
  assigned_at: string;
  first_name: string;
  last_name: string;
  email: string;
  document_type: string;
  document_number: string;
  phone: string | null;
}

const base = (farmId: string) => `/farms/${farmId}`;

export async function listRoles(farmId: string): Promise<RoleOption[]> {
  const response = await api.get<RoleOption[]>(`${base(farmId)}/roles`);
  return response.data;
}

export async function listEmployees(
  farmId: string,
  isActive?: boolean
): Promise<EmployeeResponse[]> {
  const params = isActive !== undefined ? { is_active: isActive } : {};
  const response = await api.get<EmployeeResponse[]>(`${base(farmId)}/employees`, { params });
  return response.data;
}

export async function assignEmployee(
  farmId: string,
  data: EmployeeAssign
): Promise<EmployeeResponse> {
  const response = await api.post<EmployeeResponse>(`${base(farmId)}/employees`, data);
  return response.data;
}

export interface InvitationResponse {
  id: string;
  farm_id: string;
  email: string;
  role_id: string;
  expires_at: string;
  created_at: string;
}

export async function inviteEmployee(
  farmId: string,
  data: InviteEmployee
): Promise<InvitationResponse> {
  const response = await api.post<InvitationResponse>(`${base(farmId)}/employees/invite`, data);
  return response.data;
}

export async function updateEmployee(
  farmId: string,
  userId: string,
  data: EmployeeUpdate
): Promise<EmployeeResponse> {
  const response = await api.put<EmployeeResponse>(`${base(farmId)}/employees/${userId}`, data);
  return response.data;
}

export async function removeEmployee(farmId: string, userId: string): Promise<void> {
  await api.delete(`${base(farmId)}/employees/${userId}`);
}

/**
 * Cierra o restablece la CUENTA de un usuario (users.is_active).
 * Ojo: no confundir con updateEmployee({ is_active }), que solo afecta al
 * vínculo con esta finca. Cerrar la cuenta bloquea el login en todas sus
 * fincas y anula sus sesiones abiertas. Solo lo permite un Administrador.
 */
export async function setAccountStatus(
  farmId: string,
  userId: string,
  data: { is_active: boolean; reason?: string }
): Promise<EmployeeResponse> {
  const response = await api.put<EmployeeResponse>(
    `${base(farmId)}/employees/${userId}/account`,
    data
  );
  return response.data;
}
