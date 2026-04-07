import api from "./axios";

export interface PaddockRequest {
  name: string;
  area_hectares: number;
  max_capacity: number;
  coverage_status: string;
  pasture_type?: string | null;
  status: string;
  rest_start_date?: string | null;
  rest_end_date?: string | null;
}

export interface PaddockResponse {
  id: string;
  farm_id: string;
  name: string;
  area_hectares: number;
  max_capacity: number;
  coverage_status: string;
  pasture_type: string | null;
  status: string;
  rest_start_date: string | null;
  rest_end_date: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const base = (farmId: string) => `/farms/${farmId}/paddocks`;

export async function listPaddocks(farmId: string, status?: string): Promise<PaddockResponse[]> {
  const params = status ? { status } : {};
  const response = await api.get<PaddockResponse[]>(base(farmId), { params });
  return response.data;
}

export async function createPaddock(farmId: string, data: PaddockRequest): Promise<PaddockResponse> {
  const response = await api.post<PaddockResponse>(base(farmId), data);
  return response.data;
}

export async function updatePaddock(farmId: string, paddockId: string, data: Partial<PaddockRequest>): Promise<PaddockResponse> {
  const response = await api.put<PaddockResponse>(`${base(farmId)}/${paddockId}`, data);
  return response.data;
}

export async function deletePaddock(farmId: string, paddockId: string): Promise<void> {
  await api.delete(`${base(farmId)}/${paddockId}`);
}
