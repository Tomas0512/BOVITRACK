import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { listWeights, type WeightResponse } from "../../api/weights";

interface Props {
  farmId: string;
  bovineId: string;
}

interface ChartPoint {
  fecha: string;      // "DD/MM/YYYY" para el eje X
  peso: number;       // weight_kg como número
  ganancia: number | null; // daily_gain como número
}

function toChartPoints(weights: WeightResponse[]): ChartPoint[] {
  // La API devuelve ordenado ASC por fecha — perfecto para el gráfico
  return weights.map((w) => {
    const [y, m, d] = w.measured_at.split("-");
    return {
      fecha: `${d}/${m}/${y}`,
      peso: Number(w.weight_kg),
      ganancia: w.daily_gain !== null ? Number(w.daily_gain) : null,
    };
  });
}

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number; dataKey: string }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const peso = payload.find((p) => p.dataKey === "peso");
  const ganancia = payload.find((p) => p.dataKey === "ganancia");
  return (
    <div className="rounded-xl border border-gray-100 bg-white p-3 shadow-md text-sm">
      <p className="mb-1 font-semibold text-gray-700">{label}</p>
      {peso && (
        <p className="text-primary font-medium">{peso.value.toFixed(1)} kg</p>
      )}
      {ganancia && ganancia.value !== null && (
        <p
          className={`text-xs ${
            ganancia.value >= 0 ? "text-green-600" : "text-red-500"
          }`}
        >
          {ganancia.value >= 0 ? "+" : ""}
          {ganancia.value.toFixed(2)} kg/día
        </p>
      )}
    </div>
  );
}

export default function WeightChart({ farmId, bovineId }: Props) {
  const [data, setData] = useState<ChartPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    listWeights(farmId, bovineId)
      .then((weights) => setData(toChartPoints(weights)))
      .catch(() => setError("No se pudo cargar el gráfico de pesos."))
      .finally(() => setLoading(false));
  }, [farmId, bovineId]);

  if (loading) {
    return (
      <div className="flex h-48 items-center justify-center rounded-2xl bg-white shadow-sm">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-48 items-center justify-center rounded-2xl bg-white shadow-sm">
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (data.length < 2) {
    return (
      <div className="flex h-48 items-center justify-center rounded-2xl bg-white shadow-sm">
        <p className="text-sm text-gray-400">
          Se necesitan al menos 2 pesajes para mostrar el gráfico.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-white p-6 shadow-sm">
      <h3 className="mb-4 font-bold text-gray-900">📈 Evolución de peso</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="fecha"
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            tickLine={false}
            axisLine={false}
            unit=" kg"
            width={60}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0} stroke="#e5e7eb" />
          <Line
            type="monotone"
            dataKey="peso"
            stroke="#16a34a"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "#16a34a", strokeWidth: 0 }}
            activeDot={{ r: 6 }}
            name="Peso"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
