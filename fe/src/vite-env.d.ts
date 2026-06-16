/// <reference types="vite/client" />

/**
 * What?    Declaración de tipos para las variables de entorno de Vite.
 * ¿Para?   Que TypeScript reconozca import.meta.env.VITE_* sin errores.
 * Impact? Sin este archivo, tsc falla al compilar cualquier uso de import.meta.env.
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
