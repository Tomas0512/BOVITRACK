import api from "./axios";

export interface WeightCreate {
  weight_kg: number;
  measured_at: string; // "YYYY-MM-DD"
  body_condition?: number | null;
  observations?: string | null;
}

export interface WeightResponse {
  id: string;
  farm_id: string;
  bovine_id: string;
  weight_kg: number;
  measured_at: string;
  daily_gain: number | null;
  body_condition: number | null;
  observations: string | null;
  registered_by: string;
  synchronized: boolean;
  created_at: string;
}

export async function listWeights(
  farmId: string,
  bovineId: string
): Promise<WeightResponse[]> {
  const response = await api.get<WeightResponse[]>(
    `/farms/${farmId}/bovines/${bovineId}/weights`
  );
  return response.data;
}

export async function createWeight(
  farmId: string,
  bovineId: string,
  data: WeightCreate
): Promise<WeightResponse> {
  const response = await api.post<WeightResponse>(
    `/farms/${farmId}/bovines/${bovineId}/weights`,
    data
  );
  return response.data;
}

export async function getWeight(
  farmId: string,
  bovineId: string,
  weightId: string
): Promise<WeightResponse> {
  const response = await api.get<WeightResponse>(
    `/farms/${farmId}/bovines/${bovineId}/weights/${weightId}`
  );
  return response.data;
}

export async function deleteWeight(
  farmId: string,
  bovineId: string,
  weightId: string
): Promise<void> {
  await api.delete(`/farms/${farmId}/bovines/${bovineId}/weights/${weightId}`);
}
