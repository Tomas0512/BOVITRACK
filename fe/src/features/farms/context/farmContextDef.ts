import { createContext } from "react";
import type { FarmResponse } from "../api/farms";

export interface FarmContextValue {
  farms: FarmResponse[];
  activeFarmId: string | null;
  activeFarm: FarmResponse | null;
  setActiveFarmId: (id: string) => void;
  loading: boolean;
  refreshFarms: () => Promise<void>;
}

// El objeto de contexto vive aparte del proveedor: así FarmContext.tsx solo
// exporta componentes y el Fast Refresh de Vite funciona (react-refresh).
export const FarmContext = createContext<FarmContextValue | undefined>(undefined);
