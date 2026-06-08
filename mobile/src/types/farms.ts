export interface FarmResponse {
  id: string;
  name: string;
  address: string;
  city: string;
  department: string;
  hectares: number;
  purpose?: string;
  is_active?: boolean;
}

export interface FarmCreate {
  name: string;
  address: string;
  city_id: string;
  hectares: number;
  purpose_id?: string;
}

export interface FarmCreate {
  name: string;
  address: string;
  city_id: string;
  hectares: number;
  purpose_id?: string;
}