<<<<<<<<< Temporary merge branch 1
import api from "./axios";

=========
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
>>>>>>>>> Temporary merge branch 2
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

<<<<<<<<< Temporary merge branch 1
export interface FoodUpdate extends Partial<FoodCreate> {}

=========
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
>>>>>>>>> Temporary merge branch 2
export interface FoodResponse extends FoodCreate {
  id: string;
  farm_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

<<<<<<<<< Temporary merge branch 1
=========
/**
 * ConsumptionCreate — Datos para REGISTRAR el consumo de un alimento
 * 
 * ¿Qué significa?
 * Si una vaca comió 5kg de concentrado, eso es un "consumo"
 * que DESCUENTA automáticamente del stock de ese alimento.
 */
>>>>>>>>> Temporary merge branch 2
export interface ConsumptionCreate {
  food_id: string;
  quantity: number;
  feeding_date: string;
  land_plot_id?: string | null;
  bovine_id?: string | null;
  observations?: string | null;
}

<<<<<<<<< Temporary merge branch 1
=========
/**
 * ConsumptionResponse — Datos que retorna el backend para un consumo registrado
 */
>>>>>>>>> Temporary merge branch 2
export interface ConsumptionResponse extends ConsumptionCreate {
  id: string;
  farm_id: string;
  registered_by: string;
  created_at: string;
}

<<<<<<<<< Temporary merge branch 1
const base = (farmId: string) => `/farms/${farmId}/food`;

export async function createFood(farmId: string, data: FoodCreate): Promise<FoodResponse> {
=========
// ════════════════════════════════════════════════════════════════════════════════
// 🔌 Funciones API para CRUD de Alimentos
// ════════════════════════════════════════════════════════════════════════════════

/**
 * Función auxiliar para construir la URL base
 * 
 * Ejemplo: base("farm-123") retorna "/farms/farm-123/food"
 */
const base = (farmId: string) => `/farms/${farmId}/food`;

export async function createFood(
  farmId: string,
  data: FoodCreate
): Promise<FoodResponse> {
>>>>>>>>> Temporary merge branch 2
  const response = await api.post<FoodResponse>(base(farmId), data);
  return response.data;
}

<<<<<<<<< Temporary merge branch 1
=========
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
>>>>>>>>> Temporary merge branch 2
export async function listFoods(farmId: string): Promise<FoodResponse[]> {
  const response = await api.get<FoodResponse[]>(base(farmId));
  return response.data;
}

<<<<<<<<< Temporary merge branch 1
export async function getFood(farmId: string, foodId: string): Promise<FoodResponse> {
=========
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
>>>>>>>>> Temporary merge branch 2
  const response = await api.get<FoodResponse>(`${base(farmId)}/${foodId}`);
  return response.data;
}

<<<<<<<<< Temporary merge branch 1
export async function updateFood(farmId: string, foodId: string, data: FoodUpdate): Promise<FoodResponse> {
  const response = await api.put<FoodResponse>(`${base(farmId)}/${foodId}`, data);
  return response.data;
}

=========
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
>>>>>>>>> Temporary merge branch 2
export async function deleteFood(farmId: string, foodId: string): Promise<void> {
  await api.delete(`${base(farmId)}/${foodId}`);
}

<<<<<<<<< Temporary merge branch 1
export async function createConsumption(farmId: string, data: ConsumptionCreate): Promise<ConsumptionResponse> {
  const response = await api.post<ConsumptionResponse>(`${base(farmId)}/consumptions`, data);
  return response.data;
}

export async function listConsumptions(
  farmId: string,
  params?: { food_id?: string; bovine_id?: string }
): Promise<ConsumptionResponse[]> {
=========
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

export async function listConsumptions(
  farmId: string,
  params?: { food_id?: string; bovine_id?: string }
): Promise<ConsumptionResponse[]> {
  const params = foodId ? { food_id: foodId } : undefined;
>>>>>>>>> Temporary merge branch 2
  const response = await api.get<ConsumptionResponse[]>(
    `${base(farmId)}/consumptions`,
    { params }
  );
  return response.data;
<<<<<<<<< Temporary merge branch 1
}
=========
}
