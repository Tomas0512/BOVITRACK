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

export interface FoodUpdate extends Partial<FoodCreate> {}

export interface FoodResponse extends FoodCreate {
  id: string;
  farm_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ConsumptionCreate {
  food_id: string;
  quantity: number;
  feeding_date: string;
  land_plot_id?: string | null;
  bovine_id?: string | null;
  observations?: string | null;
}

export interface ConsumptionResponse extends ConsumptionCreate {
  id: string;
  farm_id: string;
  registered_by: string;
  created_at: string;
}

const base = (farmId: string) => `/farms/${farmId}/food`;

export async function createFood(
  farmId: string,
  data: FoodCreate,
): Promise<FoodResponse> {
  const response = await api.post<FoodResponse>(base(farmId), data);
  return response.data;
}

export async function listFoods(
  farmId: string,
): Promise<FoodResponse[]> {
  const response = await api.get<FoodResponse[]>(base(farmId));
  return response.data;
}

export async function getFood(
  farmId: string,
  foodId: string,
): Promise<FoodResponse> {
  const response = await api.get<FoodResponse>(`${base(farmId)}/${foodId}`);
  return response.data;
}

export async function updateFood(
  farmId: string,
  foodId: string,
  data: FoodUpdate,
): Promise<FoodResponse> {
  const response = await api.put<FoodResponse>(
    `${base(farmId)}/${foodId}`,
    data,
  );
  return response.data;
}

export async function deleteFood(
  farmId: string,
  foodId: string,
): Promise<void> {
  await api.delete(`${base(farmId)}/${foodId}`);
}

export async function createConsumption(
  farmId: string,
  data: ConsumptionCreate,
): Promise<ConsumptionResponse> {
  const response = await api.post<ConsumptionResponse>(
    `${base(farmId)}/consumptions`,
    data,
  );
  return response.data;
}

export async function listConsumptions(
  farmId: string,
  params?: { food_id?: string; bovine_id?: string },
): Promise<ConsumptionResponse[]> {
  const response = await api.get<ConsumptionResponse[]>(
    `${base(farmId)}/consumptions`,
    { params },
  );
  return response.data;
}

export interface PurchaseCreate {
  food_id: string;
  quantity: number;
  unit_cost: number;
  movement_date?: string | null;
  notes?: string | null;
}

export interface StockMovementResponse {
  id: string;
  farm_id: string;
  food_id: string;
  movement_type: string;
  quantity: number;
  unit_cost: number | null;
  total_cost: number | null;
  stock_before: number;
  stock_after: number;
  reference_type: string | null;
  reference_id: string | null;
  notes: string | null;
  registered_by: string;
  movement_date: string;
  created_at: string;
}

export interface StockAdjustmentCreate {
  food_id: string;
  quantity: number;
  reason: string;
  movement_date?: string | null;
}

export async function recordPurchase(
  farmId: string,
  data: PurchaseCreate,
): Promise<{ food: FoodResponse; movement: StockMovementResponse }> {
  const response = await api.post<{ food: FoodResponse; movement: StockMovementResponse }>(
    `${base(farmId)}/purchases`,
    data,
  );
  return response.data;
}

export async function adjustStock(
  farmId: string,
  data: StockAdjustmentCreate,
): Promise<{ food: FoodResponse; movement: StockMovementResponse }> {
  const response = await api.post<{ food: FoodResponse; movement: StockMovementResponse }>(
    `${base(farmId)}/adjust-stock`,
    data,
  );
  return response.data;
}

export async function listStockMovements(
  farmId: string,
  params?: { food_id?: string; movement_type?: string; limit?: number },
): Promise<StockMovementResponse[]> {
  const response = await api.get<StockMovementResponse[]>(
    `${base(farmId)}/movements`,
    { params },
  );
  return response.data;
}

export async function getLowStockAlerts(
  farmId: string,
): Promise<FoodResponse[]> {
  const response = await api.get<FoodResponse[]>(
    `${base(farmId)}/low-stock`,
  );
  return response.data;
}
