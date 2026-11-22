import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

// Adjuntar token a cada request automáticamente
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem(ACCESS_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Refresh token de un solo vuelo (evita disparar varios refreshes simultáneos)
let refreshing: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh_token = sessionStorage.getItem(REFRESH_KEY);
  if (!refresh_token) {
    throw new Error("No hay refresh token disponible");
  }
  // Se usa axios directo (no la instancia `api`) para no caer en el interceptor.
  const response = await axios.post(`${api.defaults.baseURL}/auth/refresh`, { refresh_token });
  const { access_token, refresh_token: newRefresh } = response.data;
  sessionStorage.setItem(ACCESS_KEY, access_token);
  sessionStorage.setItem(REFRESH_KEY, newRefresh);
  return access_token;
}

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;

    // ¿Qué? Intentar renovar el access token en un 401 y reintentar la petición.
    const isAuthCall = (original?.url || "").includes("/auth/login") ||
      (original?.url || "").includes("/auth/refresh");

    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !isAuthCall &&
      sessionStorage.getItem(REFRESH_KEY)
    ) {
      original._retry = true;
      try {
        if (!refreshing) {
          refreshing = refreshAccessToken().finally(() => { refreshing = null; });
        }
        const newToken = await refreshing;
        original.headers = original.headers ?? {};
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch {
        // El refresh falló: limpiar sesión y notificar a la app.
        sessionStorage.removeItem(ACCESS_KEY);
        sessionStorage.removeItem(REFRESH_KEY);
        window.dispatchEvent(new Event("auth:logout"));
        return Promise.reject(error);
      }
    }

    // ¿Para qué? Mantener el error original (.response/.status) pero con un
    // mensaje legible, para que la UI pueda mostrar el detalle del backend.
    if (error.response) {
      const data = error.response.data as { detail?: unknown; message?: unknown };
      let message = "Error del servidor";
      if (error.response.status === 422 && Array.isArray(data.detail)) {
        message = data.detail
          .map((e: { msg?: string }) => e?.msg)
          .filter(Boolean)
          .join(". ");
      } else if (typeof data.detail === "string") {
        message = data.detail;
      } else if (typeof data.message === "string") {
        message = data.message;
      }
      error.message = message;
      return Promise.reject(error);
    }
    if (error.request) {
      error.message = "No se pudo conectar con el servidor";
      return Promise.reject(error);
    }
    return Promise.reject(error);
  }
);

export default api;
