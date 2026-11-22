import api from "./axios";

export interface SanitaryPlanCreate {
  bovine_id?: string | null;
  land_plot_id?: string | null;
  vaccine_or_treatment_name: string;
  treatment_type: string;
  administration_route: string;
  dose?: string | null;
  frequency_days: number;
  next_scheduled_date?: string | null;
  observations?: string | null;
}

export interface SanitaryPlanUpdate {
  vaccine_or_treatment_name?: string;
  treatment_type?: string;
  administration_route?: string;
  dose?: string | null;
  frequency_days?: number;
  last_applied_date?: string | null;
  next_scheduled_date?: string | null;
  is_active?: boolean;
  observations?: string | null;
}

export interface SanitaryPlanResponse {
  id: string;
  farm_id: string;
  bovine_id: string | null;
  land_plot_id: string | null;
  vaccine_or_treatment_name: string;
  treatment_type: string;
  administration_route: string;
  dose: string | null;
  frequency_days: number;
  last_applied_date: string | null;
  next_scheduled_date: string | null;
  is_active: boolean;
  observations: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

const base = (farmId: string) => `/farms/${farmId}/sanitary-plans`;

export async function createSanitaryPlan(
  farmId: string,
  data: SanitaryPlanCreate,
): Promise<SanitaryPlanResponse> {
  const response = await api.post<SanitaryPlanResponse>(base(farmId), data);
  return response.data;
}

export async function listSanitaryPlans(
  farmId: string,
): Promise<SanitaryPlanResponse[]> {
  const response = await api.get<SanitaryPlanResponse[]>(base(farmId));
  return response.data;
}

export async function getSanitaryPlan(
  farmId: string,
  planId: string,
): Promise<SanitaryPlanResponse> {
  const response = await api.get<SanitaryPlanResponse>(
    `${base(farmId)}/${planId}`,
  );
  return response.data;
}

export async function updateSanitaryPlan(
  farmId: string,
  planId: string,
  data: SanitaryPlanUpdate,
): Promise<SanitaryPlanResponse> {
  const response = await api.put<SanitaryPlanResponse>(
    `${base(farmId)}/${planId}`,
    data,
  );
  return response.data;
}

export async function markSanitaryPlanAsApplied(
  farmId: string,
  planId: string,
): Promise<SanitaryPlanResponse> {
  const response = await api.post<SanitaryPlanResponse>(
    `${base(farmId)}/${planId}/apply`,
  );
  return response.data;
}

export async function deleteSanitaryPlan(
  farmId: string,
  planId: string,
): Promise<void> {
  await api.delete(`${base(farmId)}/${planId}`);
}
