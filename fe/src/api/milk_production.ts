import api from "./axios";

export interface MilkProductionResponse {
  id: string;
  farm_id: string;
  bovine_id: string | null;
  land_plot_id: string | null;
  milking_date: string;
  quantity_liters: number;
  milking_type: string;
  milking_session: string | null;
  observations: string | null;
  registered_by: string;
  created_at: string;
}

export async function listMilkProduction(farmId: string, bovineId?: string): Promise<MilkProductionResponse[]> {
  const params = bovineId ? { bovine_id: bovineId } : {};
  const response = await api.get<MilkProductionResponse[]>(`/farms/${farmId}/milk-production`, { params });
  return response.data;
}
