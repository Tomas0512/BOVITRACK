import api from "./axios";

export interface MovementRequest {
  bovine_id?: string | null;
  movement_type: string;
  movement_date: string;
  price?: number | null;
  counterparty_name?: string | null;
  counterparty_document?: string | null;
  counterparty_phone?: string | null;
  origin_farm_name?: string | null;
  destination_farm_name?: string | null;
  reason?: string | null;
  observations?: string | null;
}

export interface MovementResponse extends MovementRequest {
  id: string;
  farm_id: string;
  registered_by: string;
  created_at: string;
  updated_at: string;
}

const base = (farmId: string) => `/farms/${farmId}/movements`;

export function listMovements(
  farmId: string,
  params?: {
    bovine_id?: string;
    movement_type?: string;
    date_from?: string;
    date_to?: string;
  }
): Promise<MovementResponse[]> {
  return api.get(base(farmId), { params }).then((r) => r.data);
}

export function getMovement(farmId: string, movementId: string): Promise<MovementResponse> {
  return api.get(`${base(farmId)}/${movementId}`).then((r) => r.data);
}

export function createMovement(farmId: string, data: MovementRequest): Promise<MovementResponse> {
  return api.post(base(farmId), data).then((r) => r.data);
}

export function updateMovement(farmId: string, movementId: string, data: Partial<MovementRequest>): Promise<MovementResponse> {
  return api.put(`${base(farmId)}/${movementId}`, data).then((r) => r.data);
}

export function deleteMovement(farmId: string, movementId: string): Promise<void> {
  return api.delete(`${base(farmId)}/${movementId}`);
}
