// API pública de la feature health: tratamientos y planes sanitarios.
export { default as FarmTreatments } from "./components/FarmTreatments";
export { default as TreatmentList } from "./components/TreatmentList";
export { default as SanitaryPlanList } from "./components/SanitaryPlanList";
export { listTreatments, type TreatmentResponse } from "./api/treatments";
