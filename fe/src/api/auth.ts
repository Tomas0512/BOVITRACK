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
