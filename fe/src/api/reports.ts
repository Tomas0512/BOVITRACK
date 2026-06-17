import apiClient from "./axios";

export type ReportCategory = "productivo" | "sanitario" | "economico";
export type ExportFormat = "json" | "pdf" | "excel";

export interface ProductiveReport {
  total_bovines: number;
  males: number;
  females: number;
  avg_weight: number | null;
  total_milk_liters: number;
  avg_milk_per_day: number;
  total_calves: number;
  calves_by_age_group: Record<string, number>;
}

export interface SanitaryReport {
  total_treatments: number;
  active_sanitary_plans: number;
  pending_treatments: number;
  treatments_by_type: Record<string, number>;
}

export interface EconomicReport {
  total_income: number;
  total_expense: number;
  balance: number;
  income_by_activity: Record<string, number>;
  expense_by_activity: Record<string, number>;
}

export interface ReportResponse {
  farm_id: string;
  farm_name: string;
  category: ReportCategory | null;
  start_date: string | null;
  end_date: string | null;
  productive: ProductiveReport | null;
  sanitary: SanitaryReport | null;
  economic: EconomicReport | null;
}

export async function generateReport(
  farmId: string,
  params?: {
    category?: ReportCategory;
    start_date?: string;
    end_date?: string;
    export?: ExportFormat;
  }
): Promise<ReportResponse | Blob> {
  if (params?.export && params.export !== "json") {
    const response = await apiClient.get(`/farms/${farmId}/reports`, {
      params,
      responseType: "blob",
    });
    return response.data;
  }

  const response = await apiClient.get<ReportResponse>(`/farms/${farmId}/reports`, {
    params,
  });
  return response.data;
}

export async function downloadReport(
  farmId: string,
  format: "pdf" | "excel",
  params?: { category?: ReportCategory; start_date?: string; end_date?: string }
): Promise<void> {
  const response = await apiClient.get(`/farms/${farmId}/reports`, {
    params: { ...params, export: format },
    responseType: "blob",
  });

  const blob = new Blob([response.data]);
  const ext = format === "pdf" ? "pdf" : "xlsx";
  const link = document.createElement("a");
  link.href = window.URL.createObjectURL(blob);
  link.download = `reporte_${farmId}.${ext}`;
  link.click();
  window.URL.revokeObjectURL(link.href);
}
