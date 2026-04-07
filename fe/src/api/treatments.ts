import api from "./axios";

export interface TreatmentResponse {
  id: string;
  farm_id: string;
  bovine_id: string | null;
  land_plot_id: string | null;
  treatment_type: string;
  product_name: string;
  dose: string;
  administration_route: string;
  application_date: string;
  next_application_date: string | null;
  diagnosis: string | null;
  symptoms: string | null;
  observations: string | null;
  applied_by: string;
  created_at: string;
}

export async function listTreatments(farmId: string, bovineId?: string): Promise<TreatmentResponse[]> {
  const params = bovineId ? { bovine_id: bovineId } : {};
  const response = await api.get<TreatmentResponse[]>(`/farms/${farmId}/treatments`, { params });
  return response.data;
}
