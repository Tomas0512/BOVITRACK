import { apiClient } from './api';
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserResponse,
  MessageResponse,
} from '../types/auth';

export const loginUser = (data: LoginRequest) =>
  apiClient.post<TokenResponse>('/auth/login', data).then((r) => r.data);

export const registerUser = (data: RegisterRequest) =>
  apiClient.post<TokenResponse>('/auth/register', data).then((r) => r.data);

export const forgotPassword = (email: string) =>
  apiClient.post<MessageResponse>('/auth/forgot-password', { email }).then((r) => r.data);

export const resetPassword = (token: string, new_password: string) =>
  apiClient.post<MessageResponse>('/auth/reset-password', { token, new_password }).then((r) => r.data);

export const getMe = () =>
  apiClient.get<UserResponse>('/users/me').then((r) => r.data);