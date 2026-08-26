import axios from 'axios';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Token en memoria — se actualiza desde el store
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

// Interceptor: añade Bearer token si existe
apiClient.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

// Interceptor: normaliza errores del backend (FastAPI)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const data = error.response?.data;
    if (data?.detail && typeof data.detail === 'string') {
      error.message = data.detail;
    } else if (Array.isArray(data?.detail)) {
      error.message = data.detail
        .map((d: { msg?: string }) => d?.msg)
        .filter(Boolean)
        .join('. ');
    } else if (data?.message) {
      error.message = data.message;
    }
    return Promise.reject(error);
  }
);