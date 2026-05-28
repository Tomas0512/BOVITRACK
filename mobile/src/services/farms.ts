import { apiClient } from './api';
import type { FarmResponse } from '../types/farms';

export const listFarms = () =>
  apiClient.get<FarmResponse[]>('/farms').then((r) => r.data);