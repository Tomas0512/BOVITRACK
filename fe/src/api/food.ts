/**
 * Módulo: api/food.ts
 * 
 * ¿Qué hace?
 * Define las funciones para comunicarse con los endpoints de alimentos e inventario
 * del backend en /api/v1/farms/{farm_id}/food
 * 
 * ¿Por qué?
 * El frontend NO llama directamente a URLs. Usa funciones que encapsulan
 * las llamadas HTTP, validaciones y transformaciones de datos.
 * 
 * ¿Impacto?
 * - Si la URL del backend cambia, solo editas AQUÍ
 * - Toda la lógica de errores está centralizada
 * - TypeScript valida los tipos de datos automáticamente
 */

import api from "./axios";

// ════════════════════════════════════════════════════════════════════════════════
// 📦 Interfaces de tipos para TypeScript
// ════════════════════════════════════════════════════════════════════════════════

/**
 * FoodCreate — Datos para CREAR un nuevo alimento
 * 
 * ¿Qué incluye?
 * - name: Nombre del alimento (ej: "Concentrado Premium", "Heno")
 * - category: Tipo de alimento (ej: "concentrado", "forraje", "vitaminas")
 * - unit_of_measure: Unidad (ej: "kg", "litros", "bolsas")
 * - current_stock: Cantidad actual en el inventario
 * - min_stock_alert: Cantidad mínima antes de enviar alerta
 * - cost_per_unit: Precio unitario (opcional)
 * - expiration_date: Fecha de vencimiento (opcional)
 * - supplier: Proveedor del alimento (opcional)
 */
import api from "./axios";

export interface FoodCreate {
  name: string;
  category: string;
  unit_of_measure: string;
  current_stock: number;
  min_stock_alert?: number | null;
  cost_per_unit?: number | null;
  expiration_date?: string | null;
  supplier?: string | null;
}

/**
 * FoodUpdate — Datos para ACTUALIZAR un alimento existente
 * 
 * Todos los campos son opcionales (solo actualizas lo que cambió)
 */
export interface FoodUpdate extends Partial<FoodCreate> {}

/**
 * FoodResponse — Datos que RETORNA el backend cuando consultas un alimento
 * 
 * Incluye además de FoodCreate:
 * - id: ID único del alimento
 * - farm_id: ID de la finca propietaria
 * - is_active: Si el alimento está disponible (false = borrado)
 * - created_at: Cuándo se creó
 * - updated_at: Cuándo se actualizó por última vez
 */
export interface FoodUpdate extends Partial<FoodCreate> {}

export interface FoodResponse extends FoodCreate {
  id: string;
  farm_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * ConsumptionCreate — Datos para REGISTRAR el consumo de un alimento
 * 
 * ¿Qué significa?
 * Si una vaca comió 5kg de concentrado, eso es un "consumo"
 * que DESCUENTA automáticamente del stock de ese alimento.
 */
export interface ConsumptionCreate {
  food_id: string;
  quantity: number;
  feeding_date: string;
  land_plot_id?: string | null;
  bovine_id?: string | null;
  observations?: string | null;
}

/**
 * ConsumptionResponse — Datos que retorna el backend para un consumo registrado
 */
export interface ConsumptionResponse extends ConsumptionCreate {
  id: string;
  farm_id: string;
  registered_by: string;
  created_at: string;
}

// ════════════════════════════════════════════════════════════════════════════════
// 🔌 Funciones API para CRUD de Alimentos
// ════════════════════════════════════════════════════════════════════════════════

/**
 * Función auxiliar para construir la URL base
 * 
 * Ejemplo: base("farm-123") retorna "/farms/farm-123/food"
 */
const base = (farmId: string) => `/farms/${farmId}/food`;

/**
 * 📝 Crear un nuevo alimento
 * 
 * Llamada POST /api/v1/farms/{farm_id}/food
 * Retorna: El alimento creado con ID asignado
 * 
 * Ejemplo:
 * ```
 * await createFood("farm-123", {
 *   name: "Concentrado",
 *   category: "concentrado",
 *   unit_of_measure: "kg",
 *   current_stock: 100
 * })
 * ```
 */
export async function createFood(
  farmId: string,
  data: FoodCreate
): Promise<FoodResponse> {
const base = (farmId: string) => `/farms/${farmId}/food`;

export async function createFood(farmId: string, data: FoodCreate): Promise<FoodResponse> {
  const response = await api.post<FoodResponse>(base(farmId), data);
  return response.data;
}

/**
 * 📖 Listar todos los alimentos de una finca
 * 
 * Llamada GET /api/v1/farms/{farm_id}/food
 * Retorna: Array de alimentos activos
 * 
 * ¿Por qué lista solo activos?
 * Porque los alimentos eliminados tienen is_active=false
 * El backend filtra automáticamente
 */
export async function listFoods(farmId: string): Promise<FoodResponse[]> {
  const response = await api.get<FoodResponse[]>(base(farmId));
  return response.data;
}

/**
 * 🔍 Obtener un alimento específico por su ID
 * 
 * Llamada GET /api/v1/farms/{farm_id}/food/{food_id}
 * Retorna: Un único alimento con todos sus detalles
 */
export async function getFood(
  farmId: string,
  foodId: string
): Promise<FoodResponse> {
export async function getFood(farmId: string, foodId: string): Promise<FoodResponse> {
  const response = await api.get<FoodResponse>(`${base(farmId)}/${foodId}`);
  return response.data;
}

/**
 * ✏️ Actualizar un alimento existente
 * 
 * Llamada PUT /api/v1/farms/{farm_id}/food/{food_id}
 * 
 * Ejemplo (actualizar solo el stock):
 * ```
 * await updateFood("farm-123", "food-456", {
 *   current_stock: 50
 * })
 * ```
 */
export async function updateFood(
  farmId: string,
  foodId: string,
  data: FoodUpdate
): Promise<FoodResponse> {
  const response = await api.put<FoodResponse>(
    `${base(farmId)}/${foodId}`,
    data
  );
  return response.data;
}

/**
 * 🗑️ Eliminar un alimento (soft delete)
 * 
 * Llamada DELETE /api/v1/farms/{farm_id}/food/{food_id}
 * 
 * ¿Qué es "soft delete"?
 * No borra la fila de la BD. Solo marca is_active=false
 * Así los historiales siguen existiendo en la BD (auditoría)
 */
export async function updateFood(farmId: string, foodId: string, data: FoodUpdate): Promise<FoodResponse> {
  const response = await api.put<FoodResponse>(`${base(farmId)}/${foodId}`, data);
  return response.data;
}

export async function deleteFood(farmId: string, foodId: string): Promise<void> {
  await api.delete(`${base(farmId)}/${foodId}`);
}

// ════════════════════════════════════════════════════════════════════════════════
// 🍽️ Funciones API para Consumos (registros de alimentación)
// ════════════════════════════════════════════════════════════════════════════════

/**
 * 📊 Registrar el consumo de un alimento
 * 
 * Llamada POST /api/v1/farms/{farm_id}/food/consumptions
 * 
 * ¿Qué ocurre?
 * 1. Se valida que haya stock suficiente
 * 2. Se descuenta automáticamente del current_stock
 * 3. Se registra el consumo en la tabla consumption
 * 4. Se audita (se guarda quién y cuándo)
 * 
 * Ejemplo:
 * ```
 * // La vaca "Bessie" comió 5kg de concentrado hoy
 * await createConsumption("farm-123", {
 *   food_id: "food-456",
 *   quantity: 5,
 *   feeding_date: "2026-05-31T10:30:00Z",
 *   bovine_id: "bovine-789"
 * })
 * ```
 */
export async function createConsumption(
  farmId: string,
  data: ConsumptionCreate
): Promise<ConsumptionResponse> {
  const response = await api.post<ConsumptionResponse>(
    `${base(farmId)}/consumptions`,
    data
  );
  return response.data;
}

/**
 * 📋 Listar consumos de una finca
 * 
 * Llamada GET /api/v1/farms/{farm_id}/food/consumptions?food_id={opcional}
 * 
 * ¿Qué es un consumo?
 * Un registro de "X kilogramos de este alimento fueron dados a este bovino/lote en esta fecha"
 * 
 * Ejemplo:
 * ```
 * // Ver todos los consumos
 * const allConsumptions = await listConsumptions("farm-123")
 * 
 * // Ver solo consumos de un alimento específico
 * const concentrateOnly = await listConsumptions("farm-123", "food-456")
 * ```
 */
export async function listConsumptions(
  farmId: string,
  foodId?: string
): Promise<ConsumptionResponse[]> {
  const params = foodId ? { food_id: foodId } : undefined;
export async function createConsumption(farmId: string, data: ConsumptionCreate): Promise<ConsumptionResponse> {
  const response = await api.post<ConsumptionResponse>(`${base(farmId)}/consumptions`, data);
  return response.data;
}

export async function listConsumptions(
  farmId: string,
  params?: { food_id?: string; bovine_id?: string }
): Promise<ConsumptionResponse[]> {
  const response = await api.get<ConsumptionResponse[]>(
    `${base(farmId)}/consumptions`,
    { params }
  );
  return response.data;
}
}
