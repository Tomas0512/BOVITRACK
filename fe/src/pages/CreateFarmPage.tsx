import { useEffect, useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { CheckCircle2 } from "lucide-react";
import {
  createFarm,
  listDepartments,
  listCities,
  listPurposes,
  type CityOption,
  type DepartmentOption,
  type FarmRequest,
  type PurposeOption,
} from "../api/farms";

const AREA_UNITS = [
  { value: "hectareas", label: "Hectáreas" },
  { value: "metros_cuadrados", label: "Metros cuadrados" },
  { value: "fanegadas", label: "Fanegadas" },
];

export default function CreateFarmPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [loadingCatalogs, setLoadingCatalogs] = useState(true);
  const [loadingCities, setLoadingCities] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState<{ id: string; name: string } | null>(null);
  const [departments, setDepartments] = useState<DepartmentOption[]>([]);
  const [cities, setCities] = useState<CityOption[]>([]);
  const [purposes, setPurposes] = useState<PurposeOption[]>([]);

  const [form, setForm] = useState<FarmRequest>({
    name: "",
    address: "",
    department_id: "",
    city_municipality: "",
    total_area: 0,
    area_unit: "hectareas",
    purpose_id: "",
    farm_identifier: "",
    phone: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => {
      const updated = {
        ...prev,
        [name]: name === "total_area" ? Number(value) : value,
      };
      if (name === "department_id") {
        updated.city_municipality = "";
      }
      return updated;
    });
  };

  // Cargar catálogos iniciales
  useEffect(() => {
    const loadCatalogs = async () => {
      setLoadingCatalogs(true);
      setError("");
      try {
        const [deps, purs] = await Promise.all([listDepartments(), listPurposes()]);
        setDepartments(deps);
        setPurposes(purs);
      } catch (err) {
        setError(err instanceof Error ? err.message : "No fue posible cargar los catálogos");
      } finally {
        setLoadingCatalogs(false);
      }
    };
    loadCatalogs();
  }, []);

  // Cargar ciudades cuando cambia el departamento
  useEffect(() => {
    if (!form.department_id) {
      setCities([]);
      return;
    }
    const load = async () => {
      setLoadingCities(true);
      try {
        const cits = await listCities(form.department_id);
        setCities(cits);
      } catch {
        setCities([]);
      } finally {
        setLoadingCities(false);
      }
    };
    load();
  }, [form.department_id]);

  const isFormComplete =
    form.name.trim() !== "" &&
    form.address.trim() !== "" &&
    form.department_id !== "" &&
    form.city_municipality !== "" &&
    form.total_area > 0 &&
    form.purpose_id !== "" &&
    form.farm_identifier.trim() !== "";

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!isFormComplete) return;
    setError("");
    setLoading(true);
    try {
      const farm = await createFarm(form);
      setSuccess({ id: farm.id, name: farm.name });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear la finca");
    } finally {
      setLoading(false);
    }
  };

  const inputClass =
    "w-full rounded-lg border-[1.5px] border-border bg-surface px-3 py-2 text-sm text-text-primary outline-none transition-colors placeholder:text-text-muted focus:border-primary focus:ring-2 focus:ring-primary/10";

  // Estado de éxito
  if (success) {
    return (
      <div className="flex justify-center pt-12">
        <div className="w-full max-w-md rounded-2xl bg-surface p-8 text-center shadow-lg">
          <CheckCircle2 size={48} className="text-green-500 mx-auto mb-3" />
          <h2 className="mb-1 text-xl font-bold text-primary">¡Finca creada!</h2>
          <p className="mb-6 text-sm text-text-secondary">
            La finca <strong>{success.name}</strong> ha sido registrada exitosamente.
          </p>
          <button
            onClick={() => navigate(`/farms/${success.id}`)}
            className="w-full rounded-lg bg-primary py-2.5 text-base font-bold text-white transition-colors hover:bg-primary-light"
          >
            Ver finca
          </button>
          <Link
            to="/dashboard"
            className="mt-3 block text-sm font-semibold text-primary no-underline hover:text-primary-light"
          >
            ← Volver al dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center">
      <div className="w-full max-w-lg rounded-2xl bg-surface p-8 shadow-lg">
        <h2 className="mb-1 text-center text-xl font-bold text-primary">Registrar finca</h2>
        <p className="mb-6 text-center text-sm text-text-secondary">
          Ingresa los datos de tu nueva finca ganadera.
        </p>

        {loadingCatalogs && (
          <p className="mb-4 text-center text-sm text-text-secondary">Cargando catálogos...</p>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {error && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-center text-sm text-red-600">
              {error}
            </div>
          )}

          {/* Nombre */}
          <div className="mb-4">
            <label htmlFor="name" className="mb-1 block text-sm font-semibold text-text-primary">
              Nombre de la finca <span className="text-red-600">*</span>
            </label>
            <input
              id="name" name="name" required maxLength={255}
              value={form.name} onChange={handleChange}
              placeholder="Ej: Hacienda El Porvenir" className={inputClass}
            />
            <span className="mt-0.5 block text-right text-xs text-text-muted">{form.name.length}/255</span>
          </div>

          {/* Dirección */}
          <div className="mb-4">
            <label htmlFor="address" className="mb-1 block text-sm font-semibold text-text-primary">
              Dirección <span className="text-red-600">*</span>
            </label>
            <input
              id="address" name="address" required maxLength={500}
              value={form.address} onChange={handleChange}
              placeholder="Ej: Vereda La Esperanza, Km 5" className={inputClass}
            />
            <span className="mt-0.5 block text-right text-xs text-text-muted">{form.address.length}/500</span>
          </div>

          {/* Departamento y Ciudad */}
          <div className="mb-4 grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="department_id" className="mb-1 block text-sm font-semibold text-text-primary">
                Departamento <span className="text-red-600">*</span>
              </label>
              <select
                id="department_id" name="department_id" required
                value={form.department_id}
                onChange={handleChange}
                className={inputClass}
                disabled={loadingCatalogs}
              >
                <option value="">Seleccione un departamento</option>
                {departments.map((department) => (
                  <option key={department.id} value={department.id}>
                    {department.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="city_municipality" className="mb-1 block text-sm font-semibold text-text-primary">
                Ciudad o municipio <span className="text-red-600">*</span>
              </label>
              <select
                id="city_municipality" name="city_municipality" required
                value={form.city_municipality}
                onChange={handleChange}
                className={inputClass}
                disabled={!form.department_id || loadingCities}
              >
                <option value="">
                  {loadingCities ? "Cargando..." : form.department_id ? "Seleccione una ciudad" : "Primero seleccione departamento"}
                </option>
                {cities.map((city) => (
                  <option key={city.id} value={city.name}>
                    {city.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Área y unidad */}
          <div className="mb-4 grid grid-cols-2 gap-3">
            <div>
              <label htmlFor="total_area" className="mb-1 block text-sm font-semibold text-text-primary">
                Área total <span className="text-red-600">*</span>
              </label>
              <input
                id="total_area" name="total_area" required
                type="number" min="0.01" step="0.01"
                value={form.total_area || ""} onChange={handleChange}
                placeholder="Ej: 150" className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="area_unit" className="mb-1 block text-sm font-semibold text-text-primary">
                Unidad
              </label>
              <select id="area_unit" name="area_unit" value={form.area_unit} onChange={handleChange} className={inputClass}>
                {AREA_UNITS.map((u) => (
                  <option key={u.value} value={u.value}>{u.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Propósito */}
          <div className="mb-4">
            <label htmlFor="purpose_id" className="mb-1 block text-sm font-semibold text-text-primary">
              Propósito <span className="text-red-600">*</span>
            </label>
            <select
              id="purpose_id" name="purpose_id" required
              value={form.purpose_id}
              onChange={handleChange}
              className={inputClass}
              disabled={loadingCatalogs}
            >
              <option value="">Seleccione un propósito</option>
              {purposes.map((purpose) => (
                <option key={purpose.id} value={purpose.id}>
                  {purpose.name}
                </option>
              ))}
            </select>
          </div>

          {/* Identificador */}
          <div className="mb-4">
            <label htmlFor="farm_identifier" className="mb-1 block text-sm font-semibold text-text-primary">
              Identificador de la finca <span className="text-red-600">*</span>
            </label>
            <input
              id="farm_identifier" name="farm_identifier" required maxLength={100}
              value={form.farm_identifier} onChange={handleChange}
              placeholder="Ej: FIN-001" className={inputClass}
            />
            <span className="mt-0.5 block text-right text-xs text-text-muted">{form.farm_identifier.length}/100</span>
          </div>

          {/* Teléfono */}
          <div className="mb-4">
            <label htmlFor="phone" className="mb-1 block text-sm font-semibold text-text-primary">
              Teléfono
            </label>
            <input
              id="phone" name="phone" maxLength={20}
              value={form.phone ?? ""} onChange={handleChange}
              placeholder="Ej: 3001234567" className={inputClass}
            />
            <span className="mt-0.5 block text-right text-xs text-text-muted">{(form.phone ?? "").length}/20</span>
          </div>

          <button
            type="submit"
            disabled={!isFormComplete || loading}
            className={`mt-2 w-full rounded-lg py-2.5 text-base font-bold text-white transition-all active:scale-[0.98] ${
              !isFormComplete || loading
                ? "cursor-not-allowed bg-gray-400 opacity-70"
                : "bg-primary hover:bg-primary-light"
            }`}
          >
            {loading ? "Registrando..." : "Registrar finca"}
          </button>
        </form>

        <div className="mt-5 flex justify-center">
          <Link to="/dashboard" className="text-sm font-semibold text-primary no-underline hover:text-primary-light">
            ← Volver al dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
