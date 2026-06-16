/**
 * ╔════════════════════════════════════════════════════════════════════════╗
 * ║ CLIENTE HTTP: src/api/calves.ts                                       ║
 * ║ PROPÓSITO: Peticiones HTTP para gestión de terneros (HU007)           ║
 * ║                                                                        ║
 * ║ ¿QUÉ?                                                                  ║
 * ║   Funciones que hacen peticiones GET/POST al backend sobre terneros    ║
 * ║                                                                        ║
 * ║ ¿PARA QUÉ?                                                            ║
 * ║   Que los componentes React (CalfList, GrowthChart) puedan:           ║
 * ║   - Obtener lista de terneros                                         ║
 * ║   - Obtener detalle y métricas                                        ║
 * ║   - Registrar pesajes                                                 ║
 * ║   - Obtener gráfica de crecimiento                                    ║
 * ║                                                                        ║
 * ║ ¿IMPACTO?                                                             ║
 * ║   Cada función retorna una Promise que se resuelve con los datos      ║
 * ║   del servidor. Se maneja con async/await o .then()                  ║
 * ╚════════════════════════════════════════════════════════════════════════╝
 */

import axios from "axios";
import { apiClient } from "./axios";

// ═══════════════════════════════════════════════════════════════════════════
// 📋 TIPOS DE DATOS (TypeScript Interfaces)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * ¿Qué? Interfaz para un ternero en la lista.
 * ¿Para qué? Tipificar los datos que retorna listCalves()
 */
export interface ICalf {
  id: string;
  identification_number: string;
  name: string | null;
  sex: string;
  birth_date: string; // YYYY-MM-DD
  current_weight_kg: number;
  age_days: number;
}

/**
 * ¿Qué? Interfaz para las métricas de crecimiento.
 * ¿Para qué? Tipificar los indicadores de un ternero.
 */
export interface ICalfMetrics {
  current_weight_kg: number;
  birth_weight_kg: number | null;
  days_old: number;
  daily_gain_kg: number | null;
  expected_weight_kg: number;
  growth_percentage: number;
  feeding_plan: string | null;
}

/**
 * ¿Qué? Interfaz para el detalle de un ternero.
 * ¿Para qué? Tipificar la respuesta de getCalfDetails()
 */
export interface ICalfDetail {
  bovine: {
    id: string;
    identification_number: string;
    name: string | null;
    sex: string;
    birth_date: string;
    current_weight_kg: number;
    breed: string | null;
  };
  metrics: ICalfMetrics;
}

/**
 * ¿Qué? Interfaz para un registro de pesaje.
 * ¿Para qué? Tipificar los datos de weight history.
 */
export interface IWeightRecord {
  id: string;
  date: string; // YYYY-MM-DD
  weight_kg: number;
  daily_gain_kg: number | null;
}

/**
 * ¿Qué? Interfaz para el resumen global de terneros.
 * ¿Para qué? Tipificar el resumen por finca.
 */
export interface ICalfSummary {
  total_calves: number;
  calves_0_30_days: number;
  calves_31_90_days: number;
  calves_91_365_days: number;
  average_weight_kg: number;
  average_daily_gain: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// 🔍 FUNCIONES DE LECTURA (GET)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * ¿Qué? Lista todos los terneros de una finca con filtros.
 *
 * ¿Para qué?
 *   - HU007 Task 7.1: Mostrar lista de terneros
 *   - Componente: CalfList.tsx
 *
 * ¿Parámetros?
 *   farmId: UUID de la finca
 *   maxAgeDays: Edad máxima en días (default 365)
 *   minAgeDays: Edad mínima en días (default 0)
 *   status: Filtro por estado (opcional)
 *
 * ¿Retorna?
 *   Promise<ICalf[]> - Array de terneros
 *
 * ¿Ejemplo de uso?
 *   const calves = await listCalves(farmId);
 *   // Luego mostrar en <CalfList calves={calves} />
 */
export const listCalves = async (
  farmId: string,
  maxAgeDays: number = 365,
  minAgeDays: number = 0,
  status?: string
): Promise<ICalf[]> => {
  const params = {
    max_age_days: maxAgeDays,
    min_age_days: minAgeDays,
    ...(status && { status }),
  };

  const response = await apiClient.get<ICalf[]>(
    `/api/v1/farms/${farmId}/calves`,
    { params }
  );

  return response.data;
};

/**
 * ¿Qué? Obtiene un ternero específico con todas sus métricas.
 *
 * ¿Para qué?
 *   - HU007 Task 7.5: Integración con ficha general
 *   - Mostrar detalle en BovineDetailPage
 *
 * ¿Retorna?
 *   Promise<ICalfDetail> - Bovino + métricas
 */
export const getCalfDetails = async (
  farmId: string,
  bovineId: string
): Promise<ICalfDetail> => {
  const response = await apiClient.get<ICalfDetail>(
    `/api/v1/farms/${farmId}/calves/${bovineId}`
  );

  return response.data;
};

/**
 * ¿Qué? Obtiene el historial de pesajes de un ternero.
 *
 * ¿Para qué?
 *   - HU007 Task 7.4: Graficar curva de crecimiento
 *   - Componente: GrowthChart.tsx
 *
 * ¿Retorna?
 *   Promise<IWeightRecord[]> - Array de pesajes ordenados cronológicamente
 *
 * ¿Ejemplo?
 *   const history = await getCalfWeightHistory(farmId, bovineId);
 *   // Luego pasar a <GrowthChart data={history} />
 */
export const getCalfWeightHistory = async (
  farmId: string,
  bovineId: string,
  daysBack: number = 365
): Promise<IWeightRecord[]> => {
  const response = await apiClient.get<IWeightRecord[]>(
    `/api/v1/farms/${farmId}/calves/${bovineId}/weights`,
    { params: { days_back: daysBack } }
  );

  return response.data;
};

/**
 * ¿Qué? Obtiene resumen global de terneros.
 *
 * ¿Para qué?
 *   - HU007 Task 7.3: Componente CalfList con indicadores
 *   - Dashboard con estadísticas
 *
 * ¿Retorna?
 *   Promise<ICalfSummary> - Totales y promedios
 */
export const getCalfSummary = async (
  farmId: string
): Promise<ICalfSummary> => {
  const response = await apiClient.get<ICalfSummary>(
    `/api/v1/farms/${farmId}/calves/summary`
  );

  return response.data;
};

// ═══════════════════════════════════════════════════════════════════════════
// ➕ FUNCIONES DE ESCRITURA (POST/PUT)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * ¿Qué? Registra un nuevo pesaje para un ternero.
 *
 * ¿Para qué?
 *   - HU007 Task 7.2: Registro de crecimiento (peso)
 *   - Formulario en BovineDetailPage
 *
 * ¿Parámetros?
 *   farmId: UUID de la finca
 *   bovineId: UUID del ternero
 *   weightData: {
 *     weight_kg: number,
 *     measured_date: string (YYYY-MM-DD),
 *     body_condition?: 1-5,
 *     observations?: string
 *   }
 *
 * ¿Retorna?
 *   Promise<IWeightRecord> - El pesaje guardado
 *
 * ¿Validaciones automáticas?
 *   - weight_kg > 0
 *   - measured_date no puede ser futuro
 *   - body_condition entre 1 y 5
 *   - Calcula automáticamente daily_gain
 *
 * ¿Ejemplo?
 *   const result = await recordCalfWeight(farmId, bovineId, {
 *     weight_kg: 45.5,
 *     measured_date: "2026-06-15",
 *     body_condition: 3,
 *     observations: "Ganancia normal"
 *   });
 */
export const recordCalfWeight = async (
  farmId: string,
  bovineId: string,
  weightData: {
    weight_kg: number;
    measured_date: string;
    body_condition?: number;
    observations?: string;
  }
): Promise<IWeightRecord> => {
  const response = await apiClient.post<IWeightRecord>(
    `/api/v1/farms/${farmId}/calves/${bovineId}/weights`,
    weightData
  );

  return response.data;
};

/**
 * ¿Qué? Actualiza el plan de alimentación de un ternero.
 *
 * ¿Para qué?
 *   - HU007 Task 7.2: Registro de alimentación
 *   - Registrar qué alimentos recibe el ternero
 *
 * ¿Parámetros?
 *   farmId, bovineId
 *   feedingData: {
 *     food_id: string,
 *     quantity_kg_per_day: number,
 *     start_date: string,
 *     end_date?: string,
 *     notes?: string
 *   }
 *
 * ¿Retorna?
 *   Promise<any> - Los datos guardados
 */
export const updateCalfFeedingPlan = async (
  farmId: string,
  bovineId: string,
  feedingData: {
    food_id: string;
    quantity_kg_per_day: number;
    start_date: string;
    end_date?: string;
    notes?: string;
  }
): Promise<any> => {
  const response = await apiClient.post(
    `/api/v1/farms/${farmId}/calves/${bovineId}/feeding-plan`,
    feedingData
  );

  return response.data;
};

// ═══════════════════════════════════════════════════════════════════════════
// 🔧 MANEJO DE ERRORES
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Función auxiliar para manejar errores de forma consistente.
 * ¿Para qué? Mostrar mensajes de error amigables al usuario.
 */
export const handleCalfError = (error: any): string => {
  if (axios.isAxiosError(error)) {
    // Error del servidor
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.status === 404) {
      return "Ternero no encontrado";
    }
    if (error.response?.status === 403) {
      return "No tienes acceso a esta finca";
    }
  }
  return "Error al procesar terneros. Intenta de nuevo.";
};
