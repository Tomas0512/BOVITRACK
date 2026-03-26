import api from "./axios";

export interface FarmRequest {
  name: string;
  address: string;
  department_id: string;
  city_municipality: string;
  total_area: number;
  area_unit: string;
  purpose_id: string;
  farm_identifier: string;
  phone?: string | null;
}

export interface DepartmentOption {
  id: string;
  name: string;
  code: string | null;
}

export interface PurposeOption {
  id: string;
  name: string;
  description: string | null;
}

export interface FarmResponse {
  id: string;
  owner_id: string;
  name: string;
  address: string;
  department_id: string;
  city_municipality: string;
  total_area: number;
  area_unit: string;
  purpose_id: string;
  farm_identifier: string;
  phone: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const FARMS = "/farms";

export async function createFarm(data: FarmRequest): Promise<FarmResponse> {
  const response = await api.post<FarmResponse>(FARMS, data);
  return response.data;
}

export async function listDepartments(): Promise<DepartmentOption[]> {
  const response = await api.get<DepartmentOption[]>(`${FARMS}/departments`);
  return response.data;
}

export async function listPurposes(): Promise<PurposeOption[]> {
  const response = await api.get<PurposeOption[]>(`${FARMS}/purposes`);
  return response.data;
}

export async function listFarms(): Promise<FarmResponse[]> {
  const response = await api.get<FarmResponse[]>(FARMS);
  return response.data;
}

export async function getFarm(farmId: string): Promise<FarmResponse> {
  const response = await api.get<FarmResponse>(`${FARMS}/${farmId}`);
  return response.data;
}
