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

// ─── HU014: Preferencias de notificación ────────────────────────────────────

export interface NotificationPref {
  id: string;
  farm_id: string;
  channel: "email" | "in_app" | "ambos";
  frequency: "real_time" | "daily" | "weekly";
  notify_sanitary: boolean;
  notify_low_stock: boolean;
  notify_reproductive: boolean;
  notify_birth: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationPrefUpdate {
  channel?: "email" | "in_app" | "ambos";
  frequency?: "real_time" | "daily" | "weekly";
  notify_sanitary?: boolean;
  notify_low_stock?: boolean;
  notify_reproductive?: boolean;
  notify_birth?: boolean;
}

export async function getNotificationPrefs(
  farmId: string,
): Promise<NotificationPref> {
  const res = await api.get<NotificationPref>(
    `/farms/${farmId}/alerts/preferences`,
  );
  return res.data;
}

export async function updateNotificationPrefs(
  farmId: string,
  data: NotificationPrefUpdate,
): Promise<NotificationPref> {
  const res = await api.put<NotificationPref>(
    `/farms/${farmId}/alerts/preferences`,
    data,
  );
  return res.data;
}

// ─── HU014: Historial de notificaciones ────────────────────────────────────

export interface NotificationLog {
  id: string;
  farm_id: string;
  user_id: string | null;
  type: string;
  title: string;
  message: string | null;
  channel: "email" | "in_app" | "ambos" | string;
  status: string;
  reference_id: string | null;
  sent_at: string | null;
  read_at: string | null;
  created_at: string;
}

export interface NotificationHistory {
  items: NotificationLog[];
  total: number;
  limit: number;
  offset: number;
}

export async function listNotificationHistory(
  farmId: string,
  params?: {
    type?: string;
    unread_only?: boolean;
    limit?: number;
    offset?: number;
  },
): Promise<NotificationHistory> {
  const res = await api.get<NotificationHistory>(
    `/farms/${farmId}/alerts/history`,
    { params },
  );
  return res.data;
}

export async function markNotificationRead(
  farmId: string,
  notificationId: string,
): Promise<void> {
  await api.put(`/farms/${farmId}/alerts/history/${notificationId}/read`);
}
