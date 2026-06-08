import api from "./axios";

export interface AlertItem {
  id: string;
  vaccine_or_treatment_name: string;
  treatment_type: string;
  next_scheduled_date: string | null;
  bovine_id: string | null;
  land_plot_id: string | null;
}

export interface AlertsResponse {
  overdue: AlertItem[];
  upcoming: AlertItem[];
}

export async function listAlerts(
  farmId: string,
  days: number = 7,
): Promise<AlertsResponse> {
  const response = await api.get<AlertsResponse>(
    `/farms/${farmId}/alerts`,
    { params: { days } },
  );
  return response.data;
}
