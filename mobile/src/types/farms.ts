export interface FarmResponse {
  id: string;
  name: string;
  address: string;
  department_id: string;
  city_municipality: string;
  total_area: number;
  area_unit: string;
  purpose_id: string;
  farm_identifier: string;
  phone?: string | null;
  is_active?: boolean;
  my_role_name?: string | null;
}

export interface FarmCreate {
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
