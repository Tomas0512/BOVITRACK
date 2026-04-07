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
  is_active: boolean;
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
