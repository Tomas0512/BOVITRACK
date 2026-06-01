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

export async function createFood(farmId: string, data: FoodCreate): Promise<FoodResponse> {
  const response = await api.post<FoodResponse>(base(farmId), data);
  return response.data;
}

export async function listFoods(farmId: string): Promise<FoodResponse[]> {
  const response = await api.get<FoodResponse[]>(base(farmId));
  return response.data;
}

export async function getFood(farmId: string, foodId: string): Promise<FoodResponse> {
  const response = await api.get<FoodResponse>(`${base(farmId)}/${foodId}`);
  return response.data;
}

export async function updateFood(farmId: string, foodId: string, data: FoodUpdate): Promise<FoodResponse> {
  const response = await api.put<FoodResponse>(`${base(farmId)}/${foodId}`, data);
  return response.data;
}

export async function deleteFood(farmId: string, foodId: string): Promise<void> {
  await api.delete(`${base(farmId)}/${foodId}`);
}

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