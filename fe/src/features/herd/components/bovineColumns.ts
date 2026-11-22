import type { BovineResponse } from "../../api/bovines";
import type { LandPlotResponse } from "../../api/land_plots";
import type { PaddockResponse } from "../../api/paddocks";

/* ═══════════════════════════════════════════════════════════════
   Catálogo de columnas y filtros del módulo Ganado → Bovinos.
   Cada columna/filtro está conectado a datos REALES que retorna
   la API. Los campos que aún no existen en la BD se registran
   con `available: false` para preparar la arquitectura sin romper.
   ═══════════════════════════════════════════════════════════════ */

export interface EnrichedBovine extends BovineResponse {
  land_plot_name: string | null;
  paddock_name: string | null;
  age_months: number | null;
  total_milk: number;
  milk_count: number;
  avg_milk: number;
  last_milking_date: string | null;
  ration_count: number;
  total_feed_quantity: number;
  last_feeding_date: string | null;
  treatment_count: number;
  last_treatment_date: string | null;
  next_treatment_date: string | null;
  last_treatment_type: string | null;
  last_treatment_product: string | null;
  movement_count: number;
  last_movement_date: string | null;
  last_movement_type: string | null;
  last_movement_origin: string | null;
  last_movement_destination: string | null;
  last_movement_counterparty: string | null;
  last_movement_price: number | null;
  last_movement_reason: string | null;
  service_count: number;
  calving_count: number;
  abort_count: number;
  last_service_date: string | null;
  last_calving_date: string | null;
  last_abort_date: string | null;
  last_event_type: string | null;
  last_event_date: string | null;
  last_event_result: string | null;
  next_due_date: string | null;
  bull_label: string | null;
  calf_label: string | null;
  father_label: string | null;
  mother_label: string | null;
}

export interface FilterCtx {
  rows: EnrichedBovine[];
  landPlots: LandPlotResponse[];
  paddocks: PaddockResponse[];
}

export type ColumnSortType = "string" | "number" | "date";

export interface ColumnDef {
  key: string;
  label: string;
  group: string;
  type: ColumnSortType;
  defaultVisible?: boolean;
  filterField?: string;
  getValue: (r: EnrichedBovine) => string | number | null;
  format?: (r: EnrichedBovine) => string;
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("es-CO");
}

export function fmtNum(n: number | null | undefined): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "";
  return String(Math.round(n * 100) / 100);
}

export function calcAgeMonths(birthDate: string | null | undefined): number | null {
  if (!birthDate) return null;
  const b = new Date(birthDate);
  if (Number.isNaN(b.getTime())) return null;
  const now = new Date();
  let m = (now.getFullYear() - b.getFullYear()) * 12 + (now.getMonth() - b.getMonth());
  if (now.getDate() < b.getDate()) m -= 1;
  return Math.max(0, m);
}

export function formatAge(months: number | null): string {
  if (months === null || Number.isNaN(months)) return "—";
  const y = Math.floor(months / 12);
  const m = months % 12;
  if (y === 0) return `${m} mes${m !== 1 ? "es" : ""}`;
  if (m === 0) return `${y} año${y !== 1 ? "s" : ""}`;
  return `${y}a ${m}m`;
}

const F = (v: string | null | undefined) => v ?? "";

export const EVENT_TYPE_LABELS: Record<string, string> = {
  servicio: "Servicio",
  diagnostico_gestion: "Diag. gestación",
  parto: "Parto",
  aborto: "Aborto",
  secado: "Secado",
};

export const MOVEMENT_TYPE_LABELS: Record<string, string> = {
  entrada: "Entrada",
  salida: "Salida",
  compra: "Compra",
  venta: "Venta",
  traslado: "Traslado",
  nacimiento: "Nacimiento",
};

/* ─── Columnas ─────────────────────────────────────────────── */
export const COLUMN_DEFS: ColumnDef[] = [
  { key: "identification_number", label: "ID", group: "Identificación", type: "string", defaultVisible: true, filterField: "identification_number", getValue: (r) => r.identification_number },
  { key: "name", label: "Nombre", group: "Identificación", type: "string", defaultVisible: true, filterField: "name", getValue: (r) => F(r.name) },
  { key: "sex", label: "Sexo", group: "Identificación", type: "string", defaultVisible: true, filterField: "sex", getValue: (r) => r.sex },
  { key: "breed", label: "Raza", group: "Genética", type: "string", defaultVisible: true, filterField: "breed", getValue: (r) => F(r.breed) },
  { key: "color", label: "Color", group: "Genética", type: "string", filterField: "color", getValue: (r) => F(r.color) },
  { key: "markings", label: "Marcas", group: "Identificación", type: "string", getValue: (r) => F(r.markings) },
  { key: "status", label: "Estado", group: "Identificación", type: "string", defaultVisible: true, filterField: "status", getValue: (r) => r.status },
  { key: "is_active", label: "Activo", group: "Identificación", type: "string", filterField: "is_active", getValue: (r) => (r.is_active ? "Sí" : "No") },
  { key: "purpose", label: "Propósito", group: "Identificación", type: "string", filterField: "purpose", getValue: (r) => F(r.purpose) },
  { key: "birth_date", label: "Fecha nac.", group: "Edad", type: "date", filterField: "birth_date", getValue: (r) => r.birth_date, format: (r) => fmtDate(r.birth_date) },
  { key: "age_months", label: "Edad", group: "Edad", type: "number", getValue: (r) => (r.age_months === null ? -1 : r.age_months), format: (r) => formatAge(r.age_months) },
  { key: "birth_weight", label: "Peso nac. (kg)", group: "Peso", type: "number", filterField: "birth_weight", getValue: (r) => (r.birth_weight === null ? -1 : Number(r.birth_weight)), format: (r) => (r.birth_weight ? `${r.birth_weight} kg` : "") },
  { key: "current_weight", label: "Peso actual (kg)", group: "Peso", type: "number", defaultVisible: true, filterField: "current_weight", getValue: (r) => (r.current_weight === null ? -1 : Number(r.current_weight)), format: (r) => (r.current_weight ? `${r.current_weight} kg` : "") },
  { key: "land_plot_name", label: "Lote", group: "Ubicación", type: "string", filterField: "land_plot_name", getValue: (r) => F(r.land_plot_name) },
  { key: "paddock_name", label: "Potrero", group: "Ubicación", type: "string", filterField: "paddock_name", getValue: (r) => F(r.paddock_name) },
  { key: "entry_type", label: "Tipo ingreso", group: "Movimientos", type: "string", getValue: (r) => r.entry_type },
  { key: "entry_date", label: "Fecha ingreso", group: "Movimientos", type: "date", filterField: "entry_date", getValue: (r) => r.entry_date, format: (r) => fmtDate(r.entry_date) },
  { key: "exit_date", label: "Fecha salida", group: "Movimientos", type: "date", filterField: "exit_date", getValue: (r) => r.exit_date ?? "", format: (r) => fmtDate(r.exit_date) },
  { key: "exit_reason", label: "Razón de salida", group: "Movimientos", type: "string", getValue: (r) => F(r.exit_reason) },
  { key: "father_label", label: "Padre", group: "Genética", type: "string", filterField: "father_label", getValue: (r) => F(r.father_label) },
  { key: "mother_label", label: "Madre", group: "Genética", type: "string", filterField: "mother_label", getValue: (r) => F(r.mother_label) },
  { key: "total_milk", label: "Leche total (L)", group: "Producción", type: "number", getValue: (r) => r.total_milk, format: (r) => (r.total_milk > 0 ? r.total_milk.toFixed(1) : "") },
  { key: "milk_count", label: "Nº ordeños", group: "Producción", type: "number", getValue: (r) => r.milk_count },
  { key: "avg_milk", label: "Prom. ordeño (L)", group: "Producción", type: "number", getValue: (r) => r.avg_milk, format: (r) => (r.avg_milk > 0 ? r.avg_milk.toFixed(1) : "") },
  { key: "last_milking_date", label: "Último ordeño", group: "Producción", type: "date", getValue: (r) => r.last_milking_date ?? "", format: (r) => fmtDate(r.last_milking_date) },
  { key: "ration_count", label: "Raciones", group: "Alimentación", type: "number", getValue: (r) => r.ration_count },
  { key: "total_feed_quantity", label: "Cant. alimento total", group: "Alimentación", type: "number", getValue: (r) => r.total_feed_quantity, format: (r) => fmtNum(r.total_feed_quantity) },
  { key: "last_feeding_date", label: "Última ración", group: "Alimentación", type: "date", getValue: (r) => r.last_feeding_date ?? "", format: (r) => fmtDate(r.last_feeding_date) },
  { key: "treatment_count", label: "Tratamientos", group: "Sanidad", type: "number", getValue: (r) => r.treatment_count },
  { key: "last_treatment_date", label: "Últ. tratamiento", group: "Sanidad", type: "date", filterField: "last_treatment_date", getValue: (r) => r.last_treatment_date ?? "", format: (r) => fmtDate(r.last_treatment_date) },
  { key: "next_treatment_date", label: "Próx. tratamiento", group: "Sanidad", type: "date", filterField: "next_treatment_date", getValue: (r) => r.next_treatment_date ?? "", format: (r) => fmtDate(r.next_treatment_date) },
  { key: "last_treatment_type", label: "Últ. tipo trat.", group: "Sanidad", type: "string", getValue: (r) => F(r.last_treatment_type) },
  { key: "last_treatment_product", label: "Últ. producto", group: "Sanidad", type: "string", getValue: (r) => F(r.last_treatment_product) },
  { key: "movement_count", label: "Movimientos", group: "Movimientos", type: "number", getValue: (r) => r.movement_count },
  { key: "last_movement_date", label: "Últ. movimiento", group: "Movimientos", type: "date", getValue: (r) => r.last_movement_date ?? "", format: (r) => fmtDate(r.last_movement_date) },
  { key: "last_movement_type", label: "Tipo últ. movimiento", group: "Movimientos", type: "string", filterField: "last_movement_type", getValue: (r) => F(r.last_movement_type) },
  { key: "last_movement_origin", label: "Últ. origen", group: "Movimientos", type: "string", getValue: (r) => F(r.last_movement_origin) },
  { key: "last_movement_destination", label: "Últ. destino", group: "Movimientos", type: "string", getValue: (r) => F(r.last_movement_destination) },
  { key: "last_movement_counterparty", label: "Contraparte", group: "Movimientos", type: "string", getValue: (r) => F(r.last_movement_counterparty) },
  { key: "last_movement_price", label: "Precio últ. mov.", group: "Movimientos", type: "number", getValue: (r) => (r.last_movement_price === null ? -1 : r.last_movement_price), format: (r) => (r.last_movement_price !== null ? String(r.last_movement_price) : "") },
  { key: "last_movement_reason", label: "Motivo últ. mov.", group: "Movimientos", type: "string", getValue: (r) => F(r.last_movement_reason) },
  { key: "last_service_date", label: "Últ. servicio", group: "Reproducción", type: "date", filterField: "last_service_date", getValue: (r) => r.last_service_date ?? "", format: (r) => fmtDate(r.last_service_date) },
  { key: "last_calving_date", label: "Últ. parto", group: "Reproducción", type: "date", filterField: "last_calving_date", getValue: (r) => r.last_calving_date ?? "", format: (r) => fmtDate(r.last_calving_date) },
  { key: "last_abort_date", label: "Últ. aborto", group: "Reproducción", type: "date", getValue: (r) => r.last_abort_date ?? "", format: (r) => fmtDate(r.last_abort_date) },
  { key: "last_event_type", label: "Últ. evento", group: "Reproducción", type: "string", getValue: (r) => r.last_event_type ?? "", format: (r) => EVENT_TYPE_LABELS[r.last_event_type ?? ""] ?? r.last_event_type ?? "" },
  { key: "last_event_date", label: "Fecha últ. evento", group: "Reproducción", type: "date", getValue: (r) => r.last_event_date ?? "", format: (r) => fmtDate(r.last_event_date) },
  { key: "last_event_result", label: "Resultado últ. evento", group: "Reproducción", type: "string", getValue: (r) => F(r.last_event_result) },
  { key: "service_count", label: "Nº servicios", group: "Reproducción", type: "number", getValue: (r) => r.service_count },
  { key: "calving_count", label: "Nº partos", group: "Reproducción", type: "number", getValue: (r) => r.calving_count },
  { key: "abort_count", label: "Nº abortos", group: "Reproducción", type: "number", getValue: (r) => r.abort_count },
  { key: "next_due_date", label: "Próxima fecha parto", group: "Reproducción", type: "date", getValue: (r) => r.next_due_date ?? "", format: (r) => fmtDate(r.next_due_date) },
  { key: "bull_label", label: "Toro últ. servicio", group: "Reproducción", type: "string", getValue: (r) => F(r.bull_label) },
  { key: "calf_label", label: "Cría últ. parto", group: "Reproducción", type: "string", getValue: (r) => F(r.calf_label) },
  { key: "created_at", label: "Fecha creación", group: "Registro", type: "date", filterField: "created_at", getValue: (r) => r.created_at, format: (r) => fmtDate(r.created_at) },
  { key: "updated_at", label: "Fecha actualización", group: "Registro", type: "date", filterField: "updated_at", getValue: (r) => r.updated_at, format: (r) => fmtDate(r.updated_at) },
  { key: "registered_by", label: "Registrado por", group: "Registro", type: "string", getValue: (r) => F(r.registered_by) },
  { key: "observations", label: "Observaciones", group: "Identificación", type: "string", filterField: "observations", getValue: (r) => F(r.observations) },
];

export const DEFAULT_VISIBLE_COLUMNS = COLUMN_DEFS.filter((c) => c.defaultVisible).map((c) => c.key);

/* ─── Filtros ──────────────────────────────────────────────── */
export type FieldType = "text" | "number" | "date" | "select" | "boolean";
export type Operator = "eq" | "ne" | "contains" | "gt" | "lt" | "gte" | "lte" | "date_from" | "date_to";

export interface FilterCondition {
  id: string;
  connector: "AND" | "OR";
  field: string;
  op: Operator;
  value: string;
}

export interface FilterFieldDef {
  key: string;
  label: string;
  category: string;
  type: FieldType;
  available: boolean;
  ops: Operator[];
  options?: string[];
  getValue: (r: EnrichedBovine) => string | number | null;
}

export const CATEGORIES: { id: string; label: string }[] = [
  { id: "Identificación", label: "Identificación" },
  { id: "Genética", label: "Genética" },
  { id: "Edad", label: "Edad" },
  { id: "Peso", label: "Peso" },
  { id: "Ubicación", label: "Ubicación" },
  { id: "Reproducción", label: "Reproducción" },
  { id: "Sanidad", label: "Sanidad" },
  { id: "Alimentación", label: "Alimentación" },
  { id: "Movimientos", label: "Movimientos" },
  { id: "Economía", label: "Economía" },
  { id: "Registro", label: "Registro" },
];

function unique(values: (string | null | undefined)[]): string[] {
  return [...new Set(values.map((v) => v ?? "").filter(Boolean))].sort((a, b) => a.localeCompare(b, "es"));
}

/** Construye la lista de campos de filtro con opciones reales según los datos. */
export function buildFilterFields(ctx: FilterCtx): FilterFieldDef[] {
  const parentOptions = unique(ctx.rows.map((r) => r.father_label).concat(ctx.rows.map((r) => r.mother_label)));
  return [
    { key: "identification_number", label: "ID del bovino", category: "Identificación", type: "text", available: true, ops: ["contains", "eq", "ne"], getValue: (r) => r.identification_number },
    { key: "name", label: "Nombre", category: "Identificación", type: "text", available: true, ops: ["contains", "eq", "ne"], getValue: (r) => F(r.name) },
    { key: "sex", label: "Sexo", category: "Identificación", type: "select", available: true, ops: ["eq", "ne"], options: ["macho", "hembra"], getValue: (r) => r.sex },
    { key: "status", label: "Estado", category: "Identificación", type: "select", available: true, ops: ["eq", "ne"], options: ["activo", "vendido", "muerto", "retirado"], getValue: (r) => r.status },
    { key: "is_active", label: "Activo", category: "Identificación", type: "boolean", available: true, ops: [], getValue: (r) => (r.is_active ? 1 : 0) },
    { key: "purpose", label: "Propósito", category: "Identificación", type: "select", available: true, ops: ["eq", "ne"], options: unique(ctx.rows.map((r) => r.purpose)), getValue: (r) => F(r.purpose) },
    { key: "observations", label: "Observaciones", category: "Identificación", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.observations) },
    { key: "breed", label: "Raza", category: "Genética", type: "select", available: true, ops: ["eq", "ne"], options: unique(ctx.rows.map((r) => r.breed)), getValue: (r) => F(r.breed) },
    { key: "color", label: "Color", category: "Genética", type: "select", available: true, ops: ["eq", "ne"], options: unique(ctx.rows.map((r) => r.color)), getValue: (r) => F(r.color) },
    { key: "father_label", label: "Padre", category: "Genética", type: "select", available: true, ops: ["eq", "ne"], options: parentOptions, getValue: (r) => F(r.father_label) },
    { key: "mother_label", label: "Madre", category: "Genética", type: "select", available: true, ops: ["eq", "ne"], options: parentOptions, getValue: (r) => F(r.mother_label) },
    { key: "genetic_line", label: "Línea genética", category: "Genética", type: "text", available: false, ops: ["contains"], getValue: () => "" },
    { key: "crossing", label: "Cruce", category: "Genética", type: "text", available: false, ops: ["contains"], getValue: () => "" },
    { key: "breed_percentage", label: "Porcentaje de raza", category: "Genética", type: "number", available: false, ops: ["gte", "lte"], getValue: () => null },
    { key: "birth_date", label: "Fecha de nacimiento", category: "Edad", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.birth_date },
    { key: "age_months", label: "Edad en meses", category: "Edad", type: "number", available: true, ops: ["gte", "lte", "eq"], getValue: (r) => r.age_months },
    { key: "birth_weight", label: "Peso al nacer (kg)", category: "Peso", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => (r.birth_weight === null ? null : Number(r.birth_weight)) },
    { key: "current_weight", label: "Peso actual (kg)", category: "Peso", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => (r.current_weight === null ? null : Number(r.current_weight)) },
    { key: "last_weigh_date", label: "Fecha del último pesaje", category: "Peso", type: "date", available: false, ops: ["date_from", "date_to"], getValue: () => null },
    { key: "daily_gain", label: "Ganancia diaria de peso", category: "Peso", type: "number", available: false, ops: ["gte", "lte"], getValue: () => null },
    { key: "land_plot_name", label: "Lote", category: "Ubicación", type: "select", available: true, ops: ["eq", "ne"], options: unique(ctx.landPlots.map((l) => l.name)), getValue: (r) => F(r.land_plot_name) },
    { key: "paddock_name", label: "Potrero", category: "Ubicación", type: "select", available: true, ops: ["eq", "ne"], options: unique(ctx.paddocks.map((p) => p.name)), getValue: (r) => F(r.paddock_name) },
    { key: "entry_date", label: "Fecha de ingreso", category: "Ubicación", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.entry_date },
    { key: "lot_entry_date", label: "Fecha de ingreso al lote", category: "Ubicación", type: "date", available: false, ops: ["date_from", "date_to"], getValue: () => null },
    { key: "service_count", label: "Nº de servicios", category: "Reproducción", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.service_count },
    { key: "calving_count", label: "Nº de partos", category: "Reproducción", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.calving_count },
    { key: "has_reproduction", label: "Con eventos reproductivos", category: "Reproducción", type: "boolean", available: true, ops: [], getValue: (r) => r.service_count + r.calving_count + r.abort_count },
    { key: "last_service_date", label: "Fecha de último servicio", category: "Reproducción", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.last_service_date },
    { key: "last_calving_date", label: "Fecha de último parto", category: "Reproducción", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.last_calving_date },
    { key: "abort_count", label: "Nº de abortos", category: "Reproducción", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.abort_count },
    { key: "last_abort_date", label: "Fecha de último aborto", category: "Reproducción", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.last_abort_date },
    { key: "last_event_type", label: "Tipo de último evento reproductivo", category: "Reproducción", type: "select", available: true, ops: ["eq", "ne"], options: unique(ctx.rows.map((r) => r.last_event_type).filter((v) => v !== null && v !== undefined)), getValue: (r) => F(r.last_event_type) },
    { key: "next_due_date", label: "Próxima fecha probable de parto", category: "Reproducción", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.next_due_date },
    { key: "repro_status", label: "Estado reproductivo", category: "Reproducción", type: "select", available: false, ops: ["eq"], options: [], getValue: () => null },
    { key: "gestation_status", label: "Estado de gestación", category: "Reproducción", type: "select", available: false, ops: ["eq"], options: [], getValue: () => null },
    { key: "treatment_count", label: "Nº de tratamientos", category: "Sanidad", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.treatment_count },
    { key: "has_treatment", label: "Con tratamientos", category: "Sanidad", type: "boolean", available: true, ops: [], getValue: (r) => r.treatment_count },
    { key: "last_treatment_date", label: "Fecha último tratamiento", category: "Sanidad", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.last_treatment_date },
    { key: "next_treatment_date", label: "Fecha próximo tratamiento", category: "Sanidad", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.next_treatment_date },
    { key: "last_treatment_type", label: "Tipo del último tratamiento", category: "Sanidad", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.last_treatment_type) },
    { key: "last_treatment_product", label: "Producto del último tratamiento", category: "Sanidad", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.last_treatment_product) },
    { key: "rations", label: "Nº de raciones de alimento", category: "Alimentación", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.ration_count },
    { key: "total_feed_quantity", label: "Cantidad total de alimento", category: "Alimentación", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.total_feed_quantity },
    { key: "last_feeding_date", label: "Fecha de la última ración", category: "Alimentación", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.last_feeding_date },
    { key: "has_feed", label: "Con alimentación registrada", category: "Alimentación", type: "boolean", available: true, ops: [], getValue: (r) => r.ration_count },
    { key: "diet_type", label: "Tipo de alimentación", category: "Alimentación", type: "text", available: false, ops: ["contains"], getValue: () => "" },
    { key: "total_milk", label: "Leche total (L)", category: "Producción", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.total_milk },
    { key: "milk_count", label: "Nº de ordeños", category: "Producción", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.milk_count },
    { key: "avg_milk", label: "Promedio por ordeño (L)", category: "Producción", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.avg_milk },
    { key: "last_milking_date", label: "Fecha del último ordeño", category: "Producción", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.last_milking_date },
    { key: "has_milk", label: "Con producción de leche", category: "Producción", type: "boolean", available: true, ops: [], getValue: (r) => r.milk_count },
    { key: "exit_date", label: "Fecha de salida", category: "Movimientos", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.exit_date },
    { key: "exit_reason", label: "Razón de salida", category: "Movimientos", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.exit_reason) },
    { key: "movement_count", label: "Nº de movimientos", category: "Movimientos", type: "number", available: true, ops: ["gte", "lte"], getValue: (r) => r.movement_count },
    { key: "last_movement_type", label: "Tipo de último movimiento", category: "Movimientos", type: "select", available: true, ops: ["eq"], options: unique(ctx.rows.map((r) => r.last_movement_type)), getValue: (r) => F(r.last_movement_type) },
    { key: "last_movement_origin", label: "Origen del último movimiento", category: "Movimientos", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.last_movement_origin) },
    { key: "last_movement_destination", label: "Destino del último movimiento", category: "Movimientos", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.last_movement_destination) },
    { key: "last_movement_counterparty", label: "Contraparte del último movimiento", category: "Movimientos", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.last_movement_counterparty) },
    { key: "origin", label: "Procedencia", category: "Movimientos", type: "text", available: false, ops: ["contains"], getValue: () => "" },
    { key: "destination", label: "Destino", category: "Movimientos", type: "text", available: false, ops: ["contains"], getValue: () => "" },
    { key: "purchase_value", label: "Valor de compra", category: "Economía", type: "number", available: false, ops: ["gte", "lte"], getValue: () => null },
    { key: "current_value", label: "Valor actual", category: "Economía", type: "number", available: false, ops: ["gte", "lte"], getValue: () => null },
    { key: "accumulated_cost", label: "Costo acumulado", category: "Economía", type: "number", available: false, ops: ["gte", "lte"], getValue: () => null },
    { key: "profitability", label: "Rentabilidad", category: "Economía", type: "number", available: false, ops: ["gte", "lte"], getValue: () => null },
    { key: "created_at", label: "Fecha de creación", category: "Registro", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.created_at },
    { key: "updated_at", label: "Fecha de actualización", category: "Registro", type: "date", available: true, ops: ["date_from", "date_to"], getValue: (r) => r.updated_at },
    { key: "registered_by", label: "Registrado por", category: "Registro", type: "text", available: true, ops: ["contains"], getValue: (r) => F(r.registered_by) },
    { key: "created_by", label: "Usuario que creó", category: "Registro", type: "text", available: false, ops: ["contains"], getValue: () => "" },
  ];
}

export function fieldOf(fields: FilterFieldDef[], key: string): FilterFieldDef | undefined {
  return fields.find((f) => f.key === key);
}

export function defaultOpForType(type: FieldType): Operator {
  switch (type) {
    case "date": return "date_to";
    case "select": return "eq";
    case "boolean": return "gt";
    default: return "contains";
  }
}

const num = (s: string) => Number.parseFloat(String(s).replace(",", "."));

export function testCondition(row: EnrichedBovine, field: FilterFieldDef, op: Operator, value: string): boolean {
  if (field.type === "boolean") {
    const v = Number(field.getValue(row) ?? 0);
    if (op === "gt") return v > 0;
    if (op === "eq") return v === 0;
    return false;
  }
  const raw = field.getValue(row);
  if (field.type === "date") {
    const target = String(value || "").slice(0, 10);
    const source = raw ? String(raw).slice(0, 10) : "";
    if (!target) return true;
    if (op === "date_from") return source >= target;
    if (op === "date_to") return source !== "" && source <= target;
    return false;
  }
  if (field.type === "number") {
    const a = num(String(raw ?? ""));
    const b = num(value);
    if (Number.isNaN(a) || Number.isNaN(b)) return false;
    if (op === "eq") return a === b;
    if (op === "gte") return a >= b;
    if (op === "lte") return a <= b;
    if (op === "gt") return a > b;
    if (op === "lt") return a < b;
    return false;
  }
  const hay = String(raw ?? "").toLowerCase();
  const needle = String(value ?? "").toLowerCase();
  if (op === "eq") return hay === needle;
  if (op === "ne") return hay !== needle;
  if (op === "contains") return hay.includes(needle);
  return false;
}

export function conditionToChip(field: FilterFieldDef, cond: FilterCondition): string {
  const label = field.label;
  const v = cond.value;
  const opsLabels: Record<string, string> = {
    eq: "", ne: "≠", contains: "contiene", gte: "≥", lte: "≤", gt: ">", lt: "<",
    date_from: "desde", date_to: "hasta",
  };
  const opLabel = opsLabels[cond.op] ?? "";
  const vLabel = field.type === "boolean"
    ? (cond.op === "gt" ? "Sí" : "No")
    : (field.type === "date" && cond.op.startsWith("date_") ? fmtDate(v) : v);
  return opLabel ? `${label}: ${opLabel} ${vLabel}` : `${label}: ${vLabel}`;
}

/** Aplica la lista de condiciones (conectores Y/O) sobre una fila. */
export function matchesConditions(row: EnrichedBovine, fields: FilterFieldDef[], conditions: FilterCondition[]): boolean {
  let result = true;
  let started = false;
  for (const cond of conditions) {
    const field = fieldOf(fields, cond.field);
    if (!field) continue;
    const r = field.available && testCondition(row, field, cond.op, cond.value);
    if (!started) {
      result = r;
      started = true;
    } else if (cond.connector === "AND") {
      result = result && r;
    } else {
      result = result || r;
    }
  }
  return started ? result : true;
}

export function countConditions(conditions: FilterCondition[]): number {
  return conditions.length;
}

/** Condiciones que realmente están activas (tienen valor o son booleanas). */
export function conditionsActive(conditions: FilterCondition[]): number {
  return conditions.filter((c) => c.field && (c.value !== "" || c.op === "gt" || c.op === "eq")).length;
}

export function exportCsv(rows: EnrichedBovine[], columnOrder: string[], visible: Set<string>) {
  const colByKey = new Map(COLUMN_DEFS.map((c) => [c.key, c]));
  const orderedKeys = columnOrder.filter((k) => colByKey.has(k));
  for (const c of COLUMN_DEFS) if (!orderedKeys.includes(c.key)) orderedKeys.push(c.key);
  const cols = orderedKeys.map((k) => colByKey.get(k)!).filter((c) => visible.has(c.key));
  const header = cols.map((c) => `"${c.label.replace(/"/g, '""')}"`).join(";");
  const body = rows
    .map((r) => cols.map((c) => `"${String(c.format ? c.format(r) : c.getValue(r) ?? "").replace(/"/g, '""')}"`).join(";"))
    .join("\n");
  const blob = new Blob([`\uFEFF${header}\n${body}`], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `bovinos_${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}