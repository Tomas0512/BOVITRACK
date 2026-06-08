import { apiClient } from './api';
import type { FarmResponse, FarmCreate } from '../types/farms';

export const listFarms = () =>
  apiClient.get<FarmResponse[]>('/farms').then((r) => r.data);

export const getFarm = (farmId: string) =>
  apiClient.get<FarmResponse>(`/farms/${farmId}`).then((r) => r.data);

export const createFarm = (data: FarmCreate) =>
  apiClient.post<FarmResponse>('/farms', data).then((r) => r.data);
