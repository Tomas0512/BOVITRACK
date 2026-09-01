import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { listFarms, type FarmResponse } from "../api/farms";

interface FarmContextValue {
  farms: FarmResponse[];
  activeFarmId: string | null;
  activeFarm: FarmResponse | null;
  setActiveFarmId: (id: string) => void;
  loading: boolean;
}

const FarmContext = createContext<FarmContextValue | undefined>(undefined);

const STORAGE_KEY = "active_farm_id";

export function FarmProvider({ children }: { children: ReactNode }) {
  const [farms, setFarms] = useState<FarmResponse[]>([]);
  const [activeFarmId, setActiveFarmIdState] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY)
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listFarms()
      .then((data) => setFarms(data))
      .catch(() => setFarms([]))
      .finally(() => setLoading(false));
  }, []);

  // La finca activa efectiva: la guardada si sigue existiendo, si no la primera.
  const effectiveActiveFarmId = useMemo(() => {
    if (activeFarmId && farms.some((f) => f.id === activeFarmId)) return activeFarmId;
    return farms[0]?.id ?? null;
  }, [activeFarmId, farms]);

  const setActiveFarmId = useCallback((id: string) => {
    setActiveFarmIdState(id);
    localStorage.setItem(STORAGE_KEY, id);
  }, []);

  const activeFarm = useMemo(
    () => farms.find((f) => f.id === effectiveActiveFarmId) ?? null,
    [farms, effectiveActiveFarmId]
  );

  const value = useMemo(
    () => ({ farms, activeFarmId: effectiveActiveFarmId, activeFarm, setActiveFarmId, loading }),
    [farms, effectiveActiveFarmId, activeFarm, setActiveFarmId, loading]
  );

  return <FarmContext.Provider value={value}>{children}</FarmContext.Provider>;
}

export function useFarm() {
  const ctx = useContext(FarmContext);
  if (!ctx) throw new Error("useFarm must be used within a FarmProvider");
  return ctx;
}
