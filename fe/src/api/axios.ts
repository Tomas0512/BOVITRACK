import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

// Adjuntar token a cada request automáticamente
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Formatear errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const data = error.response.data;
      // Errores de validación Pydantic (422)
      if (error.response.status === 422 && data.detail && Array.isArray(data.detail)) {
        const messages = data.detail.map(
          (err: { msg: string }) => err.msg
        );
        return Promise.reject(new Error(messages.join(". ")));
      }
      // Error con detail string
      if (data.detail && typeof data.detail === "string") {
        return Promise.reject(new Error(data.detail));
      }
      // Error con message string
      if (data.message && typeof data.message === "string") {
        return Promise.reject(new Error(data.message));
      }
      return Promise.reject(new Error("Error del servidor"));
    }
    if (error.request) {
      return Promise.reject(new Error("No se pudo conectar con el servidor"));
    }
    return Promise.reject(error);
  }
);

export default api;
