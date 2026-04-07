import api from "./axios";

export interface BovineRequest {
  identification_number: string;
  name?: string | null;
  sex: string;
  breed?: string | null;
  color?: string | null;
  markings?: string | null;
  birth_date: string;
  birth_weight?: number | null;
  current_weight?: number | null;
  father_id?: string | null;
  mother_id?: string | null;
  purpose?: string | null;
  status?: string;
  entry_type: string;
  entry_date: string;
  land_plot_id?: string | null;
  observations?: string | null;
}

export interface BovineResponse {
  id: string;
  farm_id: string;
  land_plot_id: string | null;
  name: string | null;
  identification_number: string;
  sex: string;
  breed: string | null;
  color: string | null;
  markings: string | null;
  birth_date: string;
  birth_weight: number | null;
  current_weight: number | null;
  father_id: string | null;
  mother_id: string | null;
  purpose: string | null;
  status: string;
  entry_type: string;
  entry_date: string;
  exit_date: string | null;
  exit_reason: string | null;
  observations: string | null;
  is_active: boolean;
  registered_by: string;
  created_at: string;
  updated_at: string;
}

const base = (farmId: string) => `/farms/${farmId}/bovines`;

export async function listBovines(
  farmId: string,
  filters?: { sex?: string; status?: string; purpose?: string }
): Promise<BovineResponse[]> {
  const response = await api.get<BovineResponse[]>(base(farmId), { params: filters });
  return response.data;
}

export async function getBovine(farmId: string, bovineId: string): Promise<BovineResponse> {
  const response = await api.get<BovineResponse>(`${base(farmId)}/${bovineId}`);
  return response.data;
}

export async function createBovine(farmId: string, data: BovineRequest): Promise<BovineResponse> {
  const response = await api.post<BovineResponse>(base(farmId), data);
  return response.data;
}

export async function updateBovine(farmId: string, bovineId: string, data: Partial<BovineRequest>): Promise<BovineResponse> {
  const response = await api.put<BovineResponse>(`${base(farmId)}/${bovineId}`, data);
  return response.data;
}

export async function deleteBovine(farmId: string, bovineId: string): Promise<void> {
  await api.delete(`${base(farmId)}/${bovineId}`);
}
