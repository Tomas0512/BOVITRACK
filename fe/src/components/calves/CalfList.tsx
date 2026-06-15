/**
 * ╔════════════════════════════════════════════════════════════════════════╗
 * ║ COMPONENTE: src/components/calves/CalfList.tsx                       ║
 * ║ PROPÓSITO: Lista y dashboard de terneros (HU007)                      ║
 * ║                                                                        ║
 * ║ ¿QUÉ?                                                                  ║
 * ║   Componente React que:                                                ║
 * ║   - Muestra lista de terneros con filtros                             ║
 * ║   - Calcula edad de cada ternero                                      ║
 * ║   - Muestra indicadores de crecimiento                                ║
 * ║   - Permite registrar pesajes                                         ║
 * ║                                                                        ║
 * ║ ¿PARA QUÉ?                                                            ║
 * ║   - HU007 Task 7.1: Endpoint/vista de terneros                        ║
 * ║   - HU007 Task 7.3: Componente CalfList con indicadores               ║
 * ║                                                                        ║
 * ║ ¿ESTADO?                                                              ║
 * ║   - calves: Lista de terneros                                         ║
 * ║   - summary: Resumen global                                           ║
 * ║   - loading: Indicador de carga                                       ║
 * ║   - selectedCalf: Ternero seleccionado                                ║
 * ║   - showWeightModal: Mostrar formulario pesaje                        ║
 * ╚════════════════════════════════════════════════════════════════════════╝
 */

import { useEffect, useState } from "react";
import {
  listCalves,
  getCalfSummary,
  recordCalfWeight,
  handleCalfError,
  ICalf,
  ICalfSummary,
} from "../../api/calves";

interface ICalfListProps {
  farmId: string;
}

/**
 * Componente Principal: CalfList
 * ¿Para qué? Mostrar la lista de terneros con todas sus funcionalidades
 */
export const CalfList: React.FC<ICalfListProps> = ({ farmId }) => {
  // ═══════════════════════════════════════════════════════════════════════
  // 🎯 ESTADO LOCAL
  // ═══════════════════════════════════════════════════════════════════════

  // Lista de terneros obtenida del servidor
  const [calves, setCalves] = useState<ICalf[]>([]);

  // Resumen global (totales, promedios)
  const [summary, setSummary] = useState<ICalfSummary | null>(null);

  // Indicador de carga
  const [loading, setLoading] = useState(true);

  // Mensaje de error si algo sale mal
  const [error, setError] = useState<string | null>(null);

  // Ternero seleccionado para ver detalles o registrar pesaje
  const [selectedCalf, setSelectedCalf] = useState<ICalf | null>(null);

  // Mostrar modal para registrar pesaje
  const [showWeightModal, setShowWeightModal] = useState(false);

  // Datos del formulario para registrar peso
  const [weightFormData, setWeightFormData] = useState({
    weight_kg: "",
    measured_date: new Date().toISOString().split("T")[0], // YYYY-MM-DD
    body_condition: "3",
    observations: "",
  });

  // Indicador de carga al guardar pesaje
  const [savingWeight, setSavingWeight] = useState(false);

  // Filtro por rango de edad
  const [ageFilter, setAgeFilter] = useState<"all" | "0_30" | "31_90" | "91_365">(
    "all"
  );

  // ═══════════════════════════════════════════════════════════════════════
  // 🔄 EFECTOS
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * ¿Qué? Se ejecuta al montar el componente.
   * ¿Para qué? Cargar lista de terneros y resumen.
   */
  useEffect(() => {
    const loadCalvesData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Obtener parámetros de edad según filtro
        let maxAge = 365;
        let minAge = 0;

        if (ageFilter === "0_30") {
          maxAge = 30;
        } else if (ageFilter === "31_90") {
          minAge = 31;
          maxAge = 90;
        } else if (ageFilter === "91_365") {
          minAge = 91;
          maxAge = 365;
        }

        // Llamadas paralelas al servidor
        const [calvesData, summaryData] = await Promise.all([
          listCalves(farmId, maxAge, minAge),
          getCalfSummary(farmId),
        ]);

        setCalves(calvesData);
        setSummary(summaryData);
      } catch (err) {
        setError(handleCalfError(err));
      } finally {
        setLoading(false);
      }
    };

    loadCalvesData();
  }, [farmId, ageFilter]); // Se re-ejecuta si cambian farmId o ageFilter

  // ═══════════════════════════════════════════════════════════════════════
  // 💾 MANEJADORES DE EVENTOS
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * ¿Qué? Abre el modal para registrar un pesaje.
   * ¿Para qué? HU007 Task 7.2: Registro de crecimiento
   */
  const handleOpenWeightModal = (calf: ICalf) => {
    setSelectedCalf(calf);
    setShowWeightModal(true);
    // Resetear formulario
    setWeightFormData({
      weight_kg: "",
      measured_date: new Date().toISOString().split("T")[0],
      body_condition: "3",
      observations: "",
    });
  };

  /**
   * ¿Qué? Cierra el modal.
   */
  const handleCloseWeightModal = () => {
    setShowWeightModal(false);
    setSelectedCalf(null);
  };

  /**
   * ¿Qué? Registra un nuevo pesaje.
   * ¿Para qué? Guardar el pesaje en el servidor.
   * ¿Validaciones?
   *   - Validadas por Pydantic en el servidor
   *   - weight_kg > 0
   *   - measured_date no puede ser futuro
   *   - body_condition 1-5
   */
  const handleSaveWeight = async () => {
    if (!selectedCalf) return;

    try {
      setSavingWeight(true);

      // Validación básica en el frontend
      const weightKg = parseFloat(weightFormData.weight_kg);
      if (isNaN(weightKg) || weightKg <= 0) {
        setError("El peso debe ser un número mayor a 0");
        return;
      }

      // Llamar al API para guardar
      await recordCalfWeight(farmId, selectedCalf.id, {
        weight_kg: weightKg,
        measured_date: weightFormData.measured_date,
        body_condition: parseInt(weightFormData.body_condition),
        observations: weightFormData.observations,
      });

      // Recargar lista de terneros (para actualizar current_weight)
      const updatedCalves = await listCalves(farmId);
      setCalves(updatedCalves);

      // Cerrar modal
      handleCloseWeightModal();

      // Mostrar mensaje de éxito
      alert("Pesaje registrado correctamente");
    } catch (err) {
      setError(handleCalfError(err));
    } finally {
      setSavingWeight(false);
    }
  };

  // ═══════════════════════════════════════════════════════════════════════
  // 📊 FUNCIONES AUXILIARES
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * ¿Qué? Calcula porcentaje de crecimiento esperado.
   * ¿Para qué? Mostrar indicador visual de salud.
   */
  const calculateGrowthPercentage = (calf: ICalf): number => {
    // Peso esperado simplificado: 30kg + 0.2kg/día
    const expectedWeight = 30 + calf.age_days * 0.2;
    return Math.round((calf.current_weight_kg / expectedWeight) * 100);
  };

  /**
   * ¿Qué? Obtiene color de indicador según crecimiento.
   * ¿Para qué? Visualizar si el ternero crece bien (verde), normal (amarillo) o lento (rojo)
   */
  const getGrowthColor = (percentage: number): string => {
    if (percentage >= 90) return "text-green-600"; // Bueno
    if (percentage >= 70) return "text-yellow-600"; // Normal
    return "text-red-600"; // Bajo
  };

  // ═══════════════════════════════════════════════════════════════════════
  // 🎨 RENDERIZADO
  // ═══════════════════════════════════════════════════════════════════════

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ENCABEZADO */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          🐄 Gestión de Terneros
        </h2>
        <p className="text-gray-600">
          Seguimiento del crecimiento y desarrollo de crías bovinas
        </p>
      </div>

      {/* RESUMEN GLOBAL */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {/* Total */}
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <p className="text-blue-600 text-sm font-semibold">Total Terneros</p>
            <p className="text-3xl font-bold text-blue-700">{summary.total_calves}</p>
          </div>

          {/* 0-30 días */}
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <p className="text-red-600 text-sm font-semibold">0-30 días</p>
            <p className="text-3xl font-bold text-red-700">{summary.calves_0_30_days}</p>
          </div>

          {/* 31-90 días */}
          <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
            <p className="text-orange-600 text-sm font-semibold">31-90 días</p>
            <p className="text-3xl font-bold text-orange-700">
              {summary.calves_31_90_days}
            </p>
          </div>

          {/* 91-365 días */}
          <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
            <p className="text-yellow-600 text-sm font-semibold">91-365 días</p>
            <p className="text-3xl font-bold text-yellow-700">
              {summary.calves_91_365_days}
            </p>
          </div>

          {/* Promedio de peso */}
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <p className="text-green-600 text-sm font-semibold">Peso Promedio</p>
            <p className="text-3xl font-bold text-green-700">
              {summary.average_weight_kg.toFixed(1)} kg
            </p>
          </div>
        </div>
      )}

      {/* FILTROS */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-semibold text-gray-700 mb-3">Filtrar por edad:</h3>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setAgeFilter("all")}
            className={`px-4 py-2 rounded font-semibold transition ${
              ageFilter === "all"
                ? "bg-green-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            Todos
          </button>
          <button
            onClick={() => setAgeFilter("0_30")}
            className={`px-4 py-2 rounded font-semibold transition ${
              ageFilter === "0_30"
                ? "bg-red-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            0-30 días
          </button>
          <button
            onClick={() => setAgeFilter("31_90")}
            className={`px-4 py-2 rounded font-semibold transition ${
              ageFilter === "31_90"
                ? "bg-orange-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            31-90 días
          </button>
          <button
            onClick={() => setAgeFilter("91_365")}
            className={`px-4 py-2 rounded font-semibold transition ${
              ageFilter === "91_365"
                ? "bg-yellow-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-gray-300"
            }`}
          >
            91-365 días
          </button>
        </div>
      </div>

      {/* MENSAJES DE ERROR */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          <p className="font-semibold">⚠️ Error</p>
          <p>{error}</p>
        </div>
      )}

      {/* LISTA DE TERNEROS */}
      {calves.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 text-lg">
            No hay terneros en este rango de edad
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-100 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                  Identificación
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                  Edad
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                  Peso Actual
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                  Crecimiento
                </th>
                <th className="px-6 py-3 text-center text-sm font-semibold text-gray-700">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody>
              {calves.map((calf, idx) => {
                const growthPercentage = calculateGrowthPercentage(calf);
                const growthColor = getGrowthColor(growthPercentage);

                return (
                  <tr
                    key={calf.id}
                    className={`border-b hover:bg-gray-50 ${
                      idx % 2 === 0 ? "bg-white" : "bg-gray-50"
                    }`}
                  >
                    {/* Identificación */}
                    <td className="px-6 py-4 font-semibold text-gray-800">
                      {calf.identification_number}
                    </td>

                    {/* Nombre */}
                    <td className="px-6 py-4 text-gray-700">
                      {calf.name || "Sin nombre"}
                    </td>

                    {/* Edad */}
                    <td className="px-6 py-4 text-gray-700">
                      {calf.age_days} días
                      <br />
                      <span className="text-xs text-gray-500">
                        ({Math.round(calf.age_days / 30)} meses)
                      </span>
                    </td>

                    {/* Peso */}
                    <td className="px-6 py-4 text-gray-700">
                      <span className="font-semibold">
                        {calf.current_weight_kg.toFixed(1)} kg
                      </span>
                    </td>

                    {/* Indicador de crecimiento */}
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {/* Barra de progreso */}
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all ${
                              growthPercentage >= 90
                                ? "bg-green-600"
                                : growthPercentage >= 70
                                ? "bg-yellow-600"
                                : "bg-red-600"
                            }`}
                            style={{ width: `${Math.min(growthPercentage, 100)}%` }}
                          ></div>
                        </div>
                        {/* Porcentaje */}
                        <span className={`font-semibold ${growthColor}`}>
                          {growthPercentage}%
                        </span>
                      </div>
                    </td>

                    {/* Acciones */}
                    <td className="px-6 py-4 text-center">
                      <button
                        onClick={() => handleOpenWeightModal(calf)}
                        className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition"
                      >
                        📊 Pesar
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* MODAL: REGISTRAR PESAJE */}
      {showWeightModal && selectedCalf && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-gray-800 mb-4">
              Registrar pesaje - {selectedCalf.identification_number}
            </h3>

            {/* Peso */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Peso (kg) *
              </label>
              <input
                type="number"
                step="0.1"
                value={weightFormData.weight_kg}
                onChange={(e) =>
                  setWeightFormData({
                    ...weightFormData,
                    weight_kg: e.target.value,
                  })
                }
                className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                placeholder="45.5"
              />
            </div>

            {/* Fecha */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Fecha *
              </label>
              <input
                type="date"
                value={weightFormData.measured_date}
                onChange={(e) =>
                  setWeightFormData({
                    ...weightFormData,
                    measured_date: e.target.value,
                  })
                }
                className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            {/* Condición corporal */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Condición corporal (1-5)
              </label>
              <select
                value={weightFormData.body_condition}
                onChange={(e) =>
                  setWeightFormData({
                    ...weightFormData,
                    body_condition: e.target.value,
                  })
                }
                className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="1">1 - Muy delgado</option>
                <option value="2">2 - Delgado</option>
                <option value="3">3 - Normal</option>
                <option value="4">4 - Gordito</option>
                <option value="5">5 - Muy gordo</option>
              </select>
            </div>

            {/* Observaciones */}
            <div className="mb-6">
              <label className="block text-sm font-semibold text-gray-700 mb-1">
                Observaciones
              </label>
              <textarea
                value={weightFormData.observations}
                onChange={(e) =>
                  setWeightFormData({
                    ...weightFormData,
                    observations: e.target.value,
                  })
                }
                className="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                placeholder="Ej: Ganancia normal, buena condición"
                rows={3}
              ></textarea>
            </div>

            {/* Botones */}
            <div className="flex gap-3">
              <button
                onClick={handleCloseWeightModal}
                disabled={savingWeight}
                className="flex-1 px-4 py-2 border border-gray-300 rounded font-semibold text-gray-700 hover:bg-gray-100 transition disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveWeight}
                disabled={savingWeight}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded font-semibold hover:bg-blue-700 transition disabled:opacity-50"
              >
                {savingWeight ? "Guardando..." : "Guardar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalfList;
