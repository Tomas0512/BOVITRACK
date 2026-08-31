/**
 * ╔════════════════════════════════════════════════════════════════════════╗
 * ║ COMPONENTE: src/components/calves/GrowthChart.tsx                    ║
 * ║ PROPÓSITO: Gráfica de crecimiento del ternero (HU007 Task 7.4)       ║
 * ║                                                                        ║
 * ║ WHAT?                                                                  ║
 * ║   Componente React que renderiza una gráfica de línea mostrando:      ║
 * ║   - Evolución del peso del ternero en el tiempo                       ║
 * ║   - Ganancia diaria (línea secundaria)                                ║
 * ║   - Peso esperado según raza (línea de referencia)                    ║
 * ║                                                                        ║
 * ║ WHY?                                                            ║
 * ║   - HU007 Task 7.4: Curva de crecimiento del ternero                  ║
 * ║   - Visualizar si el ternero crece adecuadamente                      ║
 * ║   - Detectar anomalías en el crecimiento                              ║
 * ║                                                                        ║
 * ║ ¿LIBRERÍAS?                                                           ║
 * ║   - Chart.js: Librería de gráficas                                    ║
 * ║   - react-chartjs-2: Wrapper React para Chart.js                      ║
 * ╚════════════════════════════════════════════════════════════════════════╝
 */

import { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { getCalfWeightHistory, IWeightRecord } from "../../api/calves";

// ═══════════════════════════════════════════════════════════════════════════
// 🔧 REGISTRAR COMPONENTES DE CHART.JS
// ═══════════════════════════════════════════════════════════════════════════

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface IGrowthChartProps {
  farmId: string;
  bovineId: string;
  calfName: string;
  calfBreed: string | null;
}

/**
 * Componente Principal: GrowthChart
 * Why? Mostrar la gráfica de crecimiento del ternero
 */
export const GrowthChart: React.FC<IGrowthChartProps> = ({
  farmId,
  bovineId,
  calfName,
  calfBreed,
}) => {
  // ═══════════════════════════════════════════════════════════════════════
  // 🎯 ESTADO LOCAL
  // ═══════════════════════════════════════════════════════════════════════

  // Historial de pesajes
  const [weightHistory, setWeightHistory] = useState<IWeightRecord[]>([]);

  // Indicador de carga
  const [loading, setLoading] = useState(true);

  // Mensaje de error
  const [error, setError] = useState<string | null>(null);

  // Rango de días a mostrar
  const [daysRange, setDaysRange] = useState<30 | 90 | 180 | 365>(365);

  // ═══════════════════════════════════════════════════════════════════════
  // 🔄 EFECTOS
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * What? Se ejecuta al montar o cambiar daysRange.
   * Why? Cargar historial de pesajes del servidor.
   */
  useEffect(() => {
    const loadWeightHistory = async () => {
      try {
        setLoading(true);
        setError(null);

        const history = await getCalfWeightHistory(
          farmId,
          bovineId,
          daysRange
        );

        setWeightHistory(history);
      } catch (err) {
        setError("Error al cargar historial de pesajes");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadWeightHistory();
  }, [farmId, bovineId, daysRange]);

  // ═══════════════════════════════════════════════════════════════════════
  // 📊 PROCESAMIENTO DE DATOS PARA LA GRÁFICA
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * What? Prepara los datos para Chart.js
   * Why? Convertir array de pesajes en estructura que Chart.js entiende
   */
  const chartData = {
    // Etiquetas del eje X (fechas)
    labels: weightHistory.map((w) => {
      // Formato: "15 Jun" (día abreviado del mes)
      const date = new Date(w.date);
      return date.toLocaleDateString("es-ES", {
        month: "short",
        day: "numeric",
      });
    }),

    // Datasets (líneas en la gráfica)
    datasets: [
      {
        // LÍNEA 1: Peso actual del ternero
        label: "Peso Actual (kg)",
        data: weightHistory.map((w) => w.weight_kg),
        borderColor: "#3b82f6", // Azul
        backgroundColor: "rgba(59, 130, 246, 0.1)", // Azul claro semi-transparente
        fill: true,
        tension: 0.4, // Suavizar línea
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: "#3b82f6",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
      },

      {
        // LÍNEA 2: Ganancia diaria (si está disponible)
        label: "Ganancia Diaria (kg/día)",
        data: weightHistory.map((w) => (w.daily_gain_kg ? w.daily_gain_kg * 10 : null)), // Multiplicar por 10 para escala
        borderColor: "#10b981", // Verde
        backgroundColor: "rgba(16, 185, 129, 0.1)", // Verde claro
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: "#10b981",
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        yAxisID: "y1", // Usar eje Y secundario
      },

      {
        // LÍNEA 3: Peso esperado (referencia)
        label: "Peso Esperado (referencia)",
        data: calculateExpectedWeights(),
        borderColor: "#f59e0b", // Naranja
        backgroundColor: "transparent",
        fill: false,
        borderDash: [5, 5], // Línea punteada
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 0,
      },
    ],
  };

  /**
   * What? Calcula pesos esperados según edad.
   * Why? Mostrar como referencia en la gráfica.
   */
  function calculateExpectedWeights(): (number | null)[] {
    if (weightHistory.length === 0) return [];

    // Asumimos que el ternero nació hace X días
    // Usamos una fórmula simple: peso esperado = 30 + (0.2 * días_edad)
    return weightHistory.map((w, _idx) => {
      // Calcular edad aproximada en ese momento
      const lastDate = new Date(weightHistory[weightHistory.length - 1].date);
      const currentDate = new Date(w.date);
      const daysAgo = Math.floor(
        (lastDate.getTime() - currentDate.getTime()) / (1000 * 60 * 60 * 24)
      );

      // Calcular edad aproximada (hoy - daysAgo)
      const calfAge = daysAgo; // Simplified

      // Peso esperado: 30kg + 0.2kg/día
      return 30 + calfAge * 0.2;
    });
  }

  // ═══════════════════════════════════════════════════════════════════════
  // ⚙️ OPCIONES DE LA GRÁFICA
  // ═══════════════════════════════════════════════════════════════════════

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      title: {
        display: true,
        text: `📊 Curva de Crecimiento - ${calfName || "Ternero"} (${calfBreed || "Raza desconocida"})`,
        font: { size: 16, weight: "bold" as const },
      },
      legend: {
        display: true,
        position: "top" as const,
        labels: { usePointStyle: true },
      },
      tooltip: {
        callbacks: {
          // Mostrar valores con formato personalizado
          label: function (context: any) {
            let label = context.dataset.label || "";
            if (label) {
              label += ": ";
            }

            if (context.parsed.y !== null) {
              label += context.parsed.y.toFixed(2);

              // Agregar unidad según el dataset
              if (context.datasetIndex === 1) {
                label += " kg/día";
              } else {
                label += " kg";
              }
            }
            return label;
          },
        },
      },
    },
    scales: {
      y: {
        type: "linear" as const,
        display: true,
        position: "left" as const,
        title: {
          display: true,
          text: "Peso (kg)",
        },
      },
      y1: {
        type: "linear" as const,
        display: true,
        position: "right" as const,
        title: {
          display: true,
          text: "Ganancia Diaria (kg/día × 10)",
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  // ═══════════════════════════════════════════════════════════════════════
  // 🎨 RENDERIZADO
  // ═══════════════════════════════════════════════════════════════════════

  if (loading) {
    return (
      <div className="bg-surface rounded-lg shadow p-6">
        <div className="flex justify-center items-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-surface rounded-lg shadow p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          <p className="font-semibold">⚠️ Error</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (weightHistory.length === 0) {
    return (
      <div className="bg-surface rounded-lg shadow p-6">
        <div className="text-center text-text-muted">
          <p className="text-lg mb-2">📊 No hay datos de pesajes disponibles</p>
          <p className="text-sm">
            Registra al menos 2 pesajes para ver la curva de crecimiento
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface rounded-lg shadow p-6">
      {/* CONTROLES DE RANGO */}
      <div className="mb-6 flex gap-2 flex-wrap">
        <p className="w-full text-sm font-semibold text-text-secondary">
          Mostrar últimos:
        </p>
        {([30, 90, 180, 365] as const).map((days) => (
          <button
            key={days}
            onClick={() => setDaysRange(days)}
            className={`px-4 py-2 rounded font-semibold transition ${
              daysRange === days
                ? "bg-blue-600 text-white"
                : "bg-surface-alt text-text-secondary hover:bg-border"
            }`}
          >
            {days === 30 && "30 días"}
            {days === 90 && "3 meses"}
            {days === 180 && "6 meses"}
            {days === 365 && "1 año"}
          </button>
        ))}
      </div>

      {/* GRÁFICA */}
      <div className="relative h-96">
        <Line data={chartData} options={chartOptions} />
      </div>

      {/* ESTADÍSTICAS */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Peso inicial */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-blue-600 text-sm font-semibold">Peso Inicial</p>
          <p className="text-2xl font-bold text-blue-700">
            {weightHistory[0]?.weight_kg.toFixed(1)} kg
          </p>
          <p className="text-xs text-blue-600 mt-1">
            {new Date(weightHistory[0]?.date).toLocaleDateString("es-ES")}
          </p>
        </div>

        {/* Peso actual */}
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-green-600 text-sm font-semibold">Peso Actual</p>
          <p className="text-2xl font-bold text-green-700">
            {weightHistory[weightHistory.length - 1]?.weight_kg.toFixed(1)} kg
          </p>
          <p className="text-xs text-green-600 mt-1">
            {new Date(
              weightHistory[weightHistory.length - 1]?.date
            ).toLocaleDateString("es-ES")}
          </p>
        </div>

        {/* Ganancia total */}
        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
          <p className="text-orange-600 text-sm font-semibold">Ganancia Total</p>
          <p className="text-2xl font-bold text-orange-700">
            {(
              weightHistory[weightHistory.length - 1]?.weight_kg -
              weightHistory[0]?.weight_kg
            ).toFixed(1)}{" "}
            kg
          </p>
          <p className="text-xs text-orange-600 mt-1">
            {weightHistory.length} pesajes registrados
          </p>
        </div>
      </div>

      {/* LEYENDA DE COLORES */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-6 h-1 bg-blue-600 rounded"></div>
          <span className="text-text-secondary">
            <strong>Azul:</strong> Peso real del ternero
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-6 h-1 bg-green-600 rounded"></div>
          <span className="text-text-secondary">
            <strong>Verde:</strong> Ganancia diaria (kg/día)
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-6 h-1 border-b-2 border-orange-600"
            style={{ borderStyle: "dashed" }}
          ></div>
          <span className="text-text-secondary">
            <strong>Naranja punteada:</strong> Referencia esperada
          </span>
        </div>
      </div>
    </div>
  );
};

export default GrowthChart;
