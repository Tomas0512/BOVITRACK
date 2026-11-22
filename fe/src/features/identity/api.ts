/**
 * Archivo: features/identity/api.ts
 * Descripción: Cliente HTTP de identidad: registro, login, recuperación de
 *              contraseña, verificación de correo, perfil y baja de la cuenta.
 * Nota: la renovación del access token NO está aquí: la hace el interceptor
 *       de @/core/http, una sola vez aunque fallen varias peticiones a la vez.
 */

import { http as api } from "@/core/http";
import type {
  UserResponse,
  TokenResponse,
  MessageResponse,
  RegisterRequest,
  LoginRequest,
} from "./types";

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

/** Solicitar recuperación de contraseña */
export async function forgotPassword(email: string): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>(`${AUTH}/forgot-password`, { email });
  return response.data;
}

/** Restablecer contraseña con token */
export async function resetPassword(token: string, newPassword: string, confirmPassword: string): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>(`${AUTH}/reset-password`, {
    token,
    new_password: newPassword,
    confirm_password: confirmPassword,
  });
  return response.data;
}

/** Obtener perfil del usuario actual */
export async function getMe(): Promise<UserResponse> {
  const response = await api.get<UserResponse>(`${USERS}/me`);
  return response.data;
}

/** Verificar el correo de una cuenta con el token recibido por email */
export async function verifyEmail(token: string): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>(`${AUTH}/verify-email`, null, {
    params: { token },
  });
  return response.data;
}

/** Eliminar la propia cuenta (requiere confirmación con el texto ELIMINAR) */
export async function deleteAccount(): Promise<MessageResponse> {
  const response = await api.delete<MessageResponse>(`${USERS}/me`, {
    data: { confirmation_text: "ELIMINAR" },
  });
  return response.data;
}
