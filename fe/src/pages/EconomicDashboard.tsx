import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, TrendingUp, TrendingDown, Wallet, DollarSign, Calendar, type LucideIcon } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend,
} from "recharts";
import { getIndicators, listRecords, type EconomicIndicators, type EconomicRecordResponse } from "../api/economics";

interface CategoryItem {
  name: string;
  value: number;
}

const CATEGORY_LABELS: Record<string, string> = {
  venta_leche: "Venta de leche",
  venta_animal: "Venta de animal",
  venta_cria: "Venta de cría",
  subsidio: "Subsidio",
  otro_ingreso: "Otro ingreso",
  compra_insumo: "Compra de insumo",
  compra_animal: "Compra de animal",
  servicio_veterinario: "Servicio veterinario",
  transporte: "Transporte",
  personal: "Personal",
  mantenimiento: "Mantenimiento",
  impuesto: "Impuesto",
  otro_gasto: "Otro gasto",
};

function fmt(n: number): string {
  return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", minimumFractionDigits: 0 }).format(n);
}

function toCategoryData(record: Record<string, number>): CategoryItem[] {
  return Object.entries(record)
    .map(([k, v]) => ({ name: CATEGORY_LABELS[k] || k, value: v }))
    .sort((a, b) => b.value - a.value);
}

interface MonthlyPoint {
  month: string;
  income: number;
  expense: number;
}

function toMonthlyData(records: EconomicRecordResponse[]): MonthlyPoint[] {
  const map = new Map<string, { income: number; expense: number }>();
  for (const r of records) {
    const key = r.record_date.slice(0, 7);
    const entry = map.get(key) || { income: 0, expense: 0 };
    if (r.record_type === "ingreso") entry.income += Number(r.amount);
    else entry.expense += Number(r.amount);
    map.set(key, entry);
  }
  return Array.from(map.entries())
    .map(([month, v]) => ({ month, ...v }))
    .sort((a, b) => a.month.localeCompare(b.month));
}

export default function EconomicDashboard() {
  const { farmId } = useParams<{ farmId: string }>();
  const [indicators, setIndicators] = useState<EconomicIndicators | null>(null);
  const [records, setRecords] = useState<EconomicRecordResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const load = async () => {
    if (!farmId) return;
    setLoading(true);
    setError("");
    try {
      const params = dateFrom || dateTo ? { date_from: dateFrom || undefined, date_to: dateTo || undefined } : undefined;
      const [ind, recs] = await Promise.all([
        getIndicators(farmId, params),
        listRecords(farmId, params),
      ]);
      setIndicators(ind);
      setRecords(recs);
    } catch {
      setError("No se pudieron cargar los indicadores económicos.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [farmId]);

  const incomeCategories = indicators ? toCategoryData(indicators.income_by_category) : [];
  const expenseCategories = indicators ? toCategoryData(indicators.expense_by_category) : [];
  const monthlyData = toMonthlyData(records);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to={`/farms/${farmId}`} className="rounded-lg p-2 text-text-muted hover:bg-surface-alt hover:text-text-primary">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Dashboard Económico</h1>
            <p className="text-sm text-text-muted">Indicadores financieros de la finca</p>
          </div>
        </div>
      </div>

      <div className="mb-6 flex flex-wrap items-end gap-4 rounded-2xl bg-surface p-4 shadow-sm">
        <div>
          <label className="mb-1 block text-xs font-medium text-text-muted">Desde</label>
          <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)}
            className="rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-text-muted">Hasta</label>
          <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)}
            className="rounded-lg border border-border px-3 py-2 text-sm focus:border-primary focus:outline-none" />
        </div>
        <button onClick={load}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light">
          <Calendar size={16} className="mr-1 inline align-text-bottom" />
          Filtrar
        </button>
        {dateFrom || dateTo ? (
          <button onClick={() => { setDateFrom(""); setDateTo(""); }}
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt">
            Limpiar
          </button>
        ) : null}
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : error ? (
        <div className="rounded-2xl bg-surface p-8 text-center shadow-sm">
          <p className="text-sm text-red-500">{error}</p>
        </div>
      ) : indicators ? (
        <>
          <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <SummaryCard icon={TrendingUp} label="Total Ingresos" value={fmt(indicators.total_income)} color="text-green-600" />
            <SummaryCard icon={TrendingDown} label="Total Egresos" value={fmt(indicators.total_expense)} color="text-red-600" />
            <SummaryCard icon={Wallet} label="Balance" value={fmt(indicators.balance)} color={indicators.balance >= 0 ? "text-green-600" : "text-red-600"} />
            <SummaryCard icon={DollarSign} label="Promedio diario" value={`${fmt(indicators.avg_income_per_day)} / ${fmt(indicators.avg_expense_per_day)}`} color="text-text-secondary" />
          </div>

          <div className="mb-6 grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl bg-surface p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-bold text-text-primary">Ingresos por categoría</h2>
              {incomeCategories.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={incomeCategories} layout="vertical" margin={{ left: 0, right: 16 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eae5d9" />
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#9c8e7b" }} tickLine={false} axisLine={false} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#6b5a45" }} tickLine={false} axisLine={false} width={120} />
                    <Tooltip formatter={(v) => fmt(Number(v))} />
                    <Bar dataKey="value" fill="#b3541e" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="py-8 text-center text-sm text-text-muted">Sin ingresos registrados</p>
              )}
            </div>

            <div className="rounded-2xl bg-surface p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-bold text-text-primary">Egresos por categoría</h2>
              {expenseCategories.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={expenseCategories} layout="vertical" margin={{ left: 0, right: 16 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#eae5d9" />
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#9c8e7b" }} tickLine={false} axisLine={false} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#6b5a45" }} tickLine={false} axisLine={false} width={120} />
                    <Tooltip formatter={(v) => fmt(Number(v))} />
                    <Bar dataKey="value" fill="#dc2626" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="py-8 text-center text-sm text-text-muted">Sin egresos registrados</p>
              )}
            </div>
          </div>

          <div className="rounded-2xl bg-surface p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-text-primary">Balance mensual</h2>
            {monthlyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={monthlyData} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#eae5d9" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#9c8e7b" }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#9c8e7b" }} tickLine={false} axisLine={false} width={80} />
                  <Tooltip formatter={(v) => fmt(Number(v))} />
                  <Legend />
                  <Line type="monotone" dataKey="income" stroke="#b3541e" strokeWidth={2} name="Ingresos" dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="expense" stroke="#dc2626" strokeWidth={2} name="Egresos" dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="py-8 text-center text-sm text-text-muted">Sin datos mensuales para mostrar</p>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}

function SummaryCard({ icon: Icon, label, value, color }: { icon: LucideIcon; label: string; value: string; color: string }) {
  return (
    <div className="rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-2 flex items-center gap-2">
        <Icon size={20} className={color} />
        <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">{label}</p>
      </div>
      <p className={`text-xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
