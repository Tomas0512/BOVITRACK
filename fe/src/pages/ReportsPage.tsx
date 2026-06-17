import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Download, FileText, FileSpreadsheet, Loader2 } from "lucide-react";
import { generateReport, downloadReport, type ReportResponse, type ReportCategory } from "../api/reports";

const CATEGORY_LABELS: Record<string, string> = {
  productivo: "Productivo",
  sanitario: "Sanitario",
  economico: "Economico",
};

export default function ReportsPage() {
  const { farmId } = useParams<{ farmId: string }>();
  const [category, setCategory] = useState<ReportCategory | "">("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!farmId) return;
    setLoading(true);
    setError("");
    try {
      const data = await generateReport(farmId, {
        category: category || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });
      setReport(data as ReportResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al generar reporte");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (format: "pdf" | "excel") => {
    if (!farmId) return;
    downloadReport(farmId, format, {
      category: category || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    });
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <div className="flex items-center gap-3">
        <Link to={`/farms/${farmId}`} className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Reportes</h1>
      </div>

      <div className="rounded-xl border border-gray-200 bg-surface p-6 shadow-sm">
        <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Categoria</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as ReportCategory | "")}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            >
              <option value="">Todas</option>
              {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Fecha inicio</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Fecha fin</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
            />
          </div>
          <div className="flex items-end gap-2">
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : null}
              Generar
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>
        )}

        {report && (
          <>
            <div className="mb-4 flex items-center justify-between border-b border-gray-200 pb-3">
              <h2 className="text-lg font-bold text-gray-900">{report.farm_name}</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => handleDownload("pdf")}
                  className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:bg-gray-50"
                >
                  <FileText size={15} />
                  PDF
                </button>
                <button
                  onClick={() => handleDownload("excel")}
                  className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm hover:bg-gray-50"
                >
                  <FileSpreadsheet size={15} />
                  Excel
                </button>
              </div>
            </div>

            {report.productive && (
              <div className="mb-6">
                <h3 className="mb-2 text-base font-bold text-primary">Productivo</h3>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Bovinos</p>
                    <p className="text-xl font-bold text-gray-900">{report.productive.total_bovines}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Machos</p>
                    <p className="text-xl font-bold text-gray-900">{report.productive.males}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Hembras</p>
                    <p className="text-xl font-bold text-gray-900">{report.productive.females}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Peso Prom.</p>
                    <p className="text-xl font-bold text-gray-900">{report.productive.avg_weight ?? "-"}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Leche (L)</p>
                    <p className="text-xl font-bold text-gray-900">{report.productive.total_milk_liters.toFixed(1)}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Terneros</p>
                    <p className="text-xl font-bold text-gray-900">{report.productive.total_calves}</p>
                  </div>
                </div>
                {Object.keys(report.productive.calves_by_age_group).length > 0 && (
                  <div className="mt-3">
                    <h4 className="mb-1 text-sm font-semibold text-gray-700">Terneros por edad</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(report.productive.calves_by_age_group).map(([group, count]) => (
                        <span key={group} className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800">
                          {group}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {report.sanitary && (
              <div className="mb-6">
                <h3 className="mb-2 text-base font-bold text-primary">Sanitario</h3>
                <div className="grid grid-cols-3 gap-3 sm:grid-cols-3 lg:grid-cols-3">
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Tratamientos</p>
                    <p className="text-xl font-bold text-gray-900">{report.sanitary.total_treatments}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Planes Activos</p>
                    <p className="text-xl font-bold text-gray-900">{report.sanitary.active_sanitary_plans}</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3 text-center">
                    <p className="text-xs text-gray-500">Pendientes</p>
                    <p className="text-xl font-bold text-gray-900">{report.sanitary.pending_treatments}</p>
                  </div>
                </div>
                {Object.keys(report.sanitary.treatments_by_type).length > 0 && (
                  <div className="mt-3">
                    <h4 className="mb-1 text-sm font-semibold text-gray-700">Por tipo</h4>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(report.sanitary.treatments_by_type).map(([type, count]) => (
                        <span key={type} className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800">
                          {type}: {count}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {report.economic && (
              <div>
                <h3 className="mb-2 text-base font-bold text-primary">Economico</h3>
                <div className="mb-3 grid grid-cols-3 gap-3">
                  <div className="rounded-lg bg-green-50 p-3 text-center">
                    <p className="text-xs text-green-600">Ingresos</p>
                    <p className="text-xl font-bold text-green-800">${report.economic.total_income.toLocaleString("es-CO", { minimumFractionDigits: 2 })}</p>
                  </div>
                  <div className="rounded-lg bg-red-50 p-3 text-center">
                    <p className="text-xs text-red-600">Egresos</p>
                    <p className="text-xl font-bold text-red-800">${report.economic.total_expense.toLocaleString("es-CO", { minimumFractionDigits: 2 })}</p>
                  </div>
                  <div className="rounded-lg bg-blue-50 p-3 text-center">
                    <p className="text-xs text-blue-600">Balance</p>
                    <p className="text-xl font-bold text-blue-800">${report.economic.balance.toLocaleString("es-CO", { minimumFractionDigits: 2 })}</p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
