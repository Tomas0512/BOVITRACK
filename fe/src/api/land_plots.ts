import api from "./axios";

export interface LandPlotRequest {
  name: string;
  area: number;
  area_unit: string;
  usage_type: string;
  max_capacity: number;
  location?: string | null;
}

export interface LandPlotUpdateRequest {
  name?: string;
  area?: number;
  area_unit?: string;
  usage_type?: string;
  max_capacity?: number;
  location?: string | null;
  is_active?: boolean;
}

export interface LandPlotResponse {
  id: string;
  farm_id: string;
  name: string;
  area: number;
  area_unit: string;
  usage_type: string;
  max_capacity: number;
  location: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const base = (farmId: string) => `/farms/${farmId}/land-plots`;

export async function listLandPlots(farmId: string, isActive?: boolean): Promise<LandPlotResponse[]> {
  const params = isActive !== undefined ? { is_active: isActive } : {};
  const response = await api.get<LandPlotResponse[]>(base(farmId), { params });
  return response.data;
}

export async function createLandPlot(farmId: string, data: LandPlotRequest): Promise<LandPlotResponse> {
  const response = await api.post<LandPlotResponse>(base(farmId), data);
  return response.data;
}

export async function updateLandPlot(farmId: string, landPlotId: string, data: LandPlotUpdateRequest): Promise<LandPlotResponse> {
  const response = await api.put<LandPlotResponse>(`${base(farmId)}/${landPlotId}`, data);
  return response.data;
}

export async function deleteLandPlot(farmId: string, landPlotId: string): Promise<void> {
  await api.delete(`${base(farmId)}/${landPlotId}`);
}
