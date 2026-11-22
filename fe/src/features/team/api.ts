/**
 * Archivo: features/team/api.ts
 * Descripción: Cliente HTTP del equipo de una finca: roles, empleados,
 *              invitaciones (y el registro por invitación) y reactivación de cuentas.
 */

import { http as api } from "@/core/http";
import type { UserResponse } from "@/features/identity";

const AUTH = "/auth";

export interface RoleOption {
  id: string;
  name: string;
  description: string | null;
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

/* ── Invitaciones ── */

export interface InvitationInfo {
  email: string;
  farm_name: string;
  role_name: string;
  inviter_name: string | null;
}

export interface InvitedRegisterRequest {
  token: string;
  first_name: string;
  last_name: string;
  document_type: string;
  document_number: string;
  phone: string;
  password: string;
  confirm_password: string;
  accept_terms: boolean;
  accept_data_policy: boolean;
}

/** Obtener info de una invitación por token */
export async function getInvitationInfo(token: string): Promise<InvitationInfo> {
  const response = await api.get<InvitationInfo>(`${AUTH}/invitation/${token}`);
  return response.data;
}

/** Registrar usuario invitado */
export async function registerInvited(data: InvitedRegisterRequest): Promise<UserResponse> {
  const response = await api.post<UserResponse>(`${AUTH}/register-invited`, data);
  return response.data;
}

/* ── Reactivación ── */

export interface ReactivationRequestData {
  email: string;
  reason?: string;
}

export interface ReactivationRequestResponse {
  id: string;
  user_id: string;
  reason: string | null;
  status: string;
  created_at: string;
  reviewed_at: string | null;
}

export interface ReactivationRequestDetail extends ReactivationRequestResponse {
  user_email: string;
  user_name: string;
}

export async function requestReactivation(data: ReactivationRequestData): Promise<ReactivationRequestResponse> {
  const response = await api.post<ReactivationRequestResponse>(`${AUTH}/request-reactivation`, data);
  return response.data;
}

// Moderación (solo Administrador): las usa pages/ReactivationRequestsPage.
export async function listReactivationRequests(): Promise<ReactivationRequestDetail[]> {
  const response = await api.get<ReactivationRequestDetail[]>("/admin/reactivation-requests");
  return response.data;
}

export async function approveReactivation(requestId: string): Promise<ReactivationRequestResponse> {
  const response = await api.post<ReactivationRequestResponse>(`/admin/reactivation-requests/${requestId}/approve`);
  return response.data;
}

export async function rejectReactivation(requestId: string): Promise<ReactivationRequestResponse> {
  const response = await api.post<ReactivationRequestResponse>(`/admin/reactivation-requests/${requestId}/reject`);
  return response.data;
}
