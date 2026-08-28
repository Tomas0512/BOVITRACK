import AsyncStorage from '@react-native-async-storage/async-storage';
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

const ACCESS_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

// Token en memoria — se mantiene sincronizado con AsyncStorage
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

export async function loadAuthStorage(): Promise<{ access: string | null; refresh: string | null }> {
  const access = await AsyncStorage.getItem(ACCESS_KEY);
  const refresh = await AsyncStorage.getItem(REFRESH_KEY);
  return { access, refresh };
}

export async function saveAuthStorage(access: string, refresh: string): Promise<void> {
  await AsyncStorage.setItem(ACCESS_KEY, access);
  await AsyncStorage.setItem(REFRESH_KEY, refresh);
}

export async function clearAuthStorage(): Promise<void> {
  await AsyncStorage.removeItem(ACCESS_KEY);
  await AsyncStorage.removeItem(REFRESH_KEY);
}

// Listener para avisar al store cuando el refresh falla (sesión inválida)
type LogoutListener = () => void;
const logoutListeners: LogoutListener[] = [];
export function onLogoutEvent(fn: LogoutListener) {
  logoutListeners.push(fn);
}

// Adjuntar token a cada request
apiClient.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

// Refresh de un solo vuelo (evita múltiples refreshes simultáneos)
let refreshing: Promise<string> | null = null;

async function refreshToken(): Promise<string> {
  const refresh_token = await AsyncStorage.getItem(REFRESH_KEY);
  if (!refresh_token) throw new Error('No hay refresh token');
  const response = await axios.post(`${BASE_URL}/auth/refresh`, { refresh_token });
  const { access_token, refresh_token: newRefresh } = response.data;
  await saveAuthStorage(access_token, newRefresh);
  authToken = access_token;
  return access_token;
}

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

// Interceptor: refresh en 401 + normalizar errores sin perder el error original
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    const url = original?.url || '';
    const isAuthCall = url.includes('/auth/login') || url.includes('/auth/refresh');

    if (error.response?.status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true;
      try {
        if (!refreshing) refreshing = refreshToken().finally(() => { refreshing = null; });
        const token = await refreshing;
        original.headers = original.headers ?? {};
        original.headers.Authorization = `Bearer ${token}`;
        return apiClient(original);
      } catch {
        authToken = null;
        await clearAuthStorage();
        logoutListeners.forEach((fn) => fn());
        return Promise.reject(error);
      }
    }

    const data = error.response?.data as { detail?: unknown; message?: unknown };
    if (error.response) {
      if (Array.isArray(data?.detail)) {
        error.message = data.detail
          .map((d: { msg?: string }) => d?.msg)
          .filter(Boolean)
          .join('. ');
      } else if (typeof data?.detail === 'string') {
        error.message = data.detail;
      } else if (typeof data?.message === 'string') {
        error.message = data.message;
      }
      return Promise.reject(error);
    }
    if (error.request) {
      error.message = 'No se pudo conectar con el servidor';
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);
