import { createContext } from "react";

export type Theme = "light" | "dark";

export interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}

// El objeto de contexto vive aparte del proveedor: así ThemeContext.tsx solo
// exporta componentes y el Fast Refresh de Vite funciona (react-refresh).
export const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);
