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

export interface MilkProductionRequest {
  bovine_id?: string | null;
  land_plot_id?: string | null;
  milking_date: string;
  quantity_liters: number;
  milking_type: string;
  milking_session?: string | null;
  observations?: string | null;
}

export interface MilkSummary {
  total_liters: string;
  avg_daily_liters: string;
  total_records: number;
  milking_days: number;
  by_session: Record<string, string>;
  by_type: Record<string, string>;
  top_bovines: { bovine_id: string; total_liters: string }[];
}

export interface MilkListParams {
  bovine_id?: string;
  date_from?: string;
  date_to?: string;
  milking_session?: string;
  milking_type?: string;
}

export async function listMilkProduction(
  farmId: string,
  params: MilkListParams = {}
): Promise<MilkProductionResponse[]> {
  const response = await api.get<MilkProductionResponse[]>(
    `/farms/${farmId}/milk-production`,
    { params }
  );
  return response.data;
}

export async function getMilkProduction(
  farmId: string,
  recordId: string
): Promise<MilkProductionResponse> {
  const response = await api.get<MilkProductionResponse>(
    `/farms/${farmId}/milk-production/${recordId}`
  );
  return response.data;
}

export async function createMilkProduction(
  farmId: string,
  data: MilkProductionRequest
): Promise<MilkProductionResponse> {
  const response = await api.post<MilkProductionResponse>(
    `/farms/${farmId}/milk-production`,
    data
  );
  return response.data;
}

export async function updateMilkProduction(
  farmId: string,
  recordId: string,
  data: Partial<MilkProductionRequest>
): Promise<MilkProductionResponse> {
  const response = await api.put<MilkProductionResponse>(
    `/farms/${farmId}/milk-production/${recordId}`,
    data
  );
  return response.data;
}

export async function deleteMilkProduction(
  farmId: string,
  recordId: string
): Promise<void> {
  await api.delete(`/farms/${farmId}/milk-production/${recordId}`);
}

export async function getMilkSummary(
  farmId: string,
  dateFrom?: string,
  dateTo?: string
): Promise<MilkSummary> {
  const response = await api.get<MilkSummary>(`/farms/${farmId}/milk-production/summary`, {
    params: { date_from: dateFrom, date_to: dateTo },
  });
  return response.data;
}