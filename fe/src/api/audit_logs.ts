import api from "./axios";

export interface AuditLogEntry {
  id: string;
  user_id: string | null;
  action: string;
  entity: string;
  entity_id: string | null;
  details: string | null;
  created_at: string;
  user_email: string | null;
  user_full_name: string | null;
}

export async function listAuditLogs(farmId: string): Promise<AuditLogEntry[]> {
  const res = await api.get<AuditLogEntry[]>(`/farms/${farmId}/audit-logs`);
  return res.data;
}
