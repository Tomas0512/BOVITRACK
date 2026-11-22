import api from "./axios";

export interface EconomicRecordCreate {
  record_type: "ingreso" | "egreso";
  category: string;
  amount: number;
  record_date: string;
  description?: string | null;
  reference_type?: string | null;
  reference_id?: string | null;
}

export interface EconomicRecordUpdate {
  category?: string;
  amount?: number;
  record_date?: string;
  description?: string | null;
}

export interface EconomicRecordResponse extends EconomicRecordCreate {
  id: string;
  farm_id: string;
  registered_by: string;
  created_at: string;
  updated_at: string;
}

export interface EconomicIndicators {
  total_income: number;
  total_expense: number;
  balance: number;
  income_by_category: Record<string, number>;
  expense_by_category: Record<string, number>;
  monthly_income: number;
  monthly_expense: number;
  monthly_balance: number;
  avg_income_per_day: number;
  avg_expense_per_day: number;
}

const base = (farmId: string) => `/farms/${farmId}/economics`;

export async function createRecord(
  farmId: string,
  data: EconomicRecordCreate,
): Promise<EconomicRecordResponse> {
  const response = await api.post<EconomicRecordResponse>(base(farmId), data);
  return response.data;
}

export async function listRecords(
  farmId: string,
  params?: {
    record_type?: string;
    category?: string;
    date_from?: string;
    date_to?: string;
  },
): Promise<EconomicRecordResponse[]> {
  const response = await api.get<EconomicRecordResponse[]>(base(farmId), {
    params,
  });
  return response.data;
}

export async function getRecord(
  farmId: string,
  recordId: string,
): Promise<EconomicRecordResponse> {
  const response = await api.get<EconomicRecordResponse>(
    `${base(farmId)}/${recordId}`,
  );
  return response.data;
}

export async function updateRecord(
  farmId: string,
  recordId: string,
  data: EconomicRecordUpdate,
): Promise<EconomicRecordResponse> {
  const response = await api.put<EconomicRecordResponse>(
    `${base(farmId)}/${recordId}`,
    data,
  );
  return response.data;
}

export async function deleteRecord(
  farmId: string,
  recordId: string,
): Promise<void> {
  await api.delete(`${base(farmId)}/${recordId}`);
}

export async function getIndicators(
  farmId: string,
  params?: { date_from?: string; date_to?: string },
): Promise<EconomicIndicators> {
  const response = await api.get<EconomicIndicators>(
    `${base(farmId)}/indicators`,
    { params },
  );
  return response.data;
}
