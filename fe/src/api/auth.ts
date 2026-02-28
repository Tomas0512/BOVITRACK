/**
 * Archivo: api/auth.ts
 * Descripción: Cliente HTTP para los endpoints de autenticación del backend.
 * ¿Para qué? Centralizar todas las llamadas al backend en un solo lugar.
 *             Las páginas importan estas funciones en vez de usar axios directamente.
 * ¿Impacto? Si la URL del backend cambia, solo se modifica aquí.
 */

import axios from "axios";

/** Instancia de axios apuntando al backend */
const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// ── Tipos de respuesta ──────────────────────────

export interface UserResponse {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  document_type: string;
  document_number: string;
  phone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MessageResponse {
  message: string;
}

// ── Tipos de request ────────────────────────────

export interface RegisterData {
  email: string;
  first_name: string;
  last_name: string;
  document_type: string;
  document_number: string;
  phone: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

// ── Funciones de la API ─────────────────────────

/** Registrar un nuevo usuario */
export async function registerUser(data: RegisterData): Promise<UserResponse> {
  const response = await api.post<UserResponse>("/auth/register", data);
  return response.data;
}

/** Iniciar sesión */
export async function loginUser(data: LoginData): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>("/auth/login", data);
  return response.data;
}

/** Solicitar recuperación de contraseña */
export async function forgotPassword(email: string): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>("/auth/forgot-password", {
    email,
  });
  return response.data;
}

/** Restablecer contraseña con token */
export async function resetPassword(
  token: string,
  newPassword: string
): Promise<MessageResponse> {
  const response = await api.post<MessageResponse>("/auth/reset-password", {
    token,
    new_password: newPassword,
  });
  return response.data;
}
