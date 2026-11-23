import { useContext } from "react";
import { FarmContext } from "./farmContextDef";

export function useFarm() {
  const ctx = useContext(FarmContext);
  if (!ctx) throw new Error("useFarm must be used within a FarmProvider");
  return ctx;
}
