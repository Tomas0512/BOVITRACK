/**
 * Archivo: api/auth.ts
 * Descripción: Cliente HTTP para los endpoints de autenticación del backend.
 */

import api from "./axios";
import type {
  UserResponse,
  TokenResponse,
  MessageResponse,
  RegisterRequest,
  LoginRequest,
} from "../types/auth";

const AUTH = "/auth";
const USERS = "/users";

/** Registrar un nuevo usuario */
export async function registerUser(data: RegisterRequest): Promise<UserResponse> {
  const response = await api.post<UserResponse>(`${AUTH}/register`, data);
  return response.data;
}

/** Iniciar sesión */
export async function loginUser(data: LoginRequest): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>(`${AUTH}/login`, data);
  return response.data;
}

/** Renovar tokens */
export async function refreshToken(refresh_token: string): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>(`${AUTH}/refresh`, { refresh_token });
  return response.data;
}

/** Solicitar recuperación de contraseña */
export async function forgotPassword(email: string): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>(`${AUTH}/forgot-password`, { email });
  return response.data;
}

/** Restablecer contraseña con token */
export async function resetPassword(token: string, newPassword: string): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>(`${AUTH}/reset-password`, {
    token,
    new_password: newPassword,
  });
  return response.data;
}

/** Obtener perfil del usuario actual */
export async function getMe(): Promise<UserResponse> {
  const response = await api.get<UserResponse>(`${USERS}/me`);
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
