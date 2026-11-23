// API pública de la feature farms: la finca activa, el alta de fincas, lotes,
// potreros y su mapa. Otras partes de la app importan SOLO desde "@/features/farms".

// Finca activa (selector del menú lateral y de las páginas)
export { FarmProvider } from "./context/FarmContext";
export { useFarm } from "./context/useFarm";

// Pantallas y componentes
export { default as CreateFarmPage } from "./pages/CreateFarmPage";
export { default as LandPlotList } from "./components/LandPlotList";
export { default as PaddockList } from "./components/PaddockList";
export { default as MapaInteractivoFinca } from "./components/MapaInteractivoFinca";

// Cliente HTTP que usan otras features (selectores de finca, lote y potrero)
export {
  deleteFarm,
  getFarm,
  listDepartments,
  listFarms,
  listPurposes,
  updateFarm,
  type DepartmentOption,
  type FarmRequest,
  type FarmResponse,
  type PurposeOption,
} from "./api/farms";
export { listLandPlots, type LandPlotResponse } from "./api/land_plots";
export { listPaddocks, type PaddockResponse } from "./api/paddocks";
