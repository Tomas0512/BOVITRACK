// API pública de la feature livestock: bovinos, pesajes, terneros y movimientos.
// Es una feature BASE: la usan health, inventory, milk_production, herd y las
// páginas de app. Otras partes importan SOLO desde "@/features/livestock".

// Componentes
export { default as BovineFormModal } from "./components/BovineFormModal";
export { default as WeightChart } from "./components/WeightChart";
export { default as WeightHistory } from "./components/WeightHistory";
export { default as CalfList } from "./components/CalfList";
export { default as GrowthChart } from "./components/GrowthChart";
export { default as MovementList } from "./components/MovementList";

// Cliente HTTP que usan otras features
export {
  deleteBovine,
  getBovine,
  importBovinesCsv,
  listBovines,
  type BovineResponse,
  type ImportResult,
} from "./api/bovines";
export { listMovements, type MovementResponse } from "./api/movements";
