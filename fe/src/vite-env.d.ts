/// <reference types="vite/client" />

/**
 * ¿Qué?    Declaración de tipos para las variables de entorno de Vite.
 * ¿Para?   Que TypeScript reconozca import.meta.env.VITE_* sin errores.
 * ¿Impacto? Sin este archivo, tsc falla al compilar cualquier uso de import.meta.env.
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
