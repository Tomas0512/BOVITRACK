/**
 * Componente: FoodList
 * 
 * ¿Qué hace?
 * Muestra una TABLA con todos los alimentos (inventario) de una finca
 * Permite crear, editar, eliminar alimentos
 * Alerta si el stock está bajo
 * 
 * ¿Por qué existe?
 * El usuario necesita una pantalla para gestionar el inventario de alimentos
 * sin entrar a un formulario individual.
 * 
 * ¿Cómo se usa?
 * <FoodList farmId="farm-123" />
 */

import { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import {
  listFoods,
  deleteFood,
  type FoodResponse,
} from "../../api/food";
import FoodFormModal from "./FoodFormModal";

interface Props {
  farmId: string;
}

/**
 * Colores para las categorías de alimentos
 * Mapea cada categoría a un color de badge
 */
const CATEGORY_BADGE: Record<string, string> = {
  concentrado: "bg-amber-50 text-amber-700",
  forraje: "bg-green-50 text-green-700",
  vitaminas: "bg-purple-50 text-purple-700",
  suplementos: "bg-blue-50 text-blue-700",
  medicamentos: "bg-red-50 text-red-700",
};

export default function FoodList({ farmId }: Props) {
  // ════════════════════════════════════════════════════════════════════════════════
  // 📊 Estado del componente
  // ════════════════════════════════════════════════════════════════════════════════

  /**
   * foods — Lista de alimentos cargados del backend
   * loading — Mientras se carga la lista
   * error — Mensaje de error si algo falla
   * showModal — Mostrar/ocultar el formulario modal
   * editing — Si es null, se crea uno nuevo. Si tiene datos, se edita ese
   * actionLoading — ID del alimento que se está eliminando (para mostrar spinner)
   * categoryFilter — Filtro por categoría (todos, concentrado, forraje, etc.)
   */
  const [foods, setFoods] = useState<FoodResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<FoodResponse | undefined>();
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState("");

  // ════════════════════════════════════════════════════════════════════════════════
  // 🔄 Cargar datos del backend
  // ════════════════════════════════════════════════════════════════════════════════

  /**
   * fetchFoods() — Obtiene la lista de alimentos del backend
   * 
   * ¿Qué hace?
   * 1. Muestra un spinner (loading=true)
   * 2. Limpia errores anteriores
   * 3. Llama a listFoods() (definido en api/food.ts)
   * 4. Guarda los datos en el state
   * 5. Filtra por categoría si hay uno seleccionado
   * 6. Maneja errores si la llamada falla
   */
  const fetchFoods = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listFoods(farmId);
      
      // Filtrar por categoría si hay uno seleccionado
      const filtered = categoryFilter
        ? data.filter((f) => f.category === categoryFilter)
        : data;
      
      setFoods(filtered);
    } catch {
      setError("No se pudieron cargar los alimentos");
    } finally {
      setLoading(false);
    }
  };

  /**
   * useEffect — Se ejecuta cuando:
   * 1. El componente se monta (se abre la página)
   * 2. Cambia farmId (cambias de finca)
   * 3. Cambia categoryFilter (cambias el filtro)
   */
  useEffect(() => {
    fetchFoods();
  }, [farmId, categoryFilter]);

  // ════════════════════════════════════════════════════════════════════════════════
  // 🗑️ Eliminar un alimento
  // ════════════════════════════════════════════════════════════════════════════════

  const handleDelete = async (food: FoodResponse) => {
    /**
     * Paso 1: Pedir confirmación
     * Si el usuario no confirma, no hacer nada
     */
    if (!confirm(`¿Eliminar el alimento "${food.name}"?`)) return;

    /**
     * Paso 2: Mostrar que se está eliminando (spinner en el botón)
     */
    setActionLoading(food.id);

    try {
      /**
       * Paso 3: Llamar al backend para eliminar
       * Esto hace un DELETE a /api/v1/farms/{farm_id}/food/{food_id}
       */
      await deleteFood(farmId, food.id);

      /**
       * Paso 4: Recargar la lista (sin el alimento eliminado)
       */
      await fetchFoods();
    } catch {
      /**
       * Si algo falla, mostrar error
       */
      setError("No se pudo eliminar el alimento");
    } finally {
      /**
       * Paso 5: Dejar de mostrar el spinner
       */
      setActionLoading(null);
    }
  };

  // ════════════════════════════════════════════════════════════════════════════════
  // ✅ Después de crear/editar un alimento
  // ════════════════════════════════════════════════════════════════════════════════

  const handleSuccess = () => {
    /**
     * El modal llamará a esta función cuando el usuario
     * presione "Guardar" en el formulario
     * 
     * Entonces:
     * 1. Cerramos el modal
     * 2. Limpiamos la edición actual
     * 3. Recargamos la lista desde el backend
     */
    setShowModal(false);
    setEditing(undefined);
    fetchFoods();
  };

  // ════════════════════════════════════════════════════════════════════════════════
  // 📊 Calcular estadísticas
  // ════════════════════════════════════════════════════════════════════════════════

  /**
   * Contar cuántos alimentos hay con stock bajo
   * (donde current_stock <= min_stock_alert)
   */
  const lowStockCount = foods.filter((f) => 
    f.min_stock_alert && f.current_stock <= f.min_stock_alert
  ).length;

  /**
   * Agrupar alimentos por categoría para mostrar en botones
   * Ejemplo: {concentrado: 5, forraje: 3, vitaminas: 1}
   */
  const categoryCounts = foods.reduce(
    (acc, f) => {
      acc[f.category] = (acc[f.category] ?? 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  // ════════════════════════════════════════════════════════════════════════════════
  // 🎨 Renderizar la UI
  // ════════════════════════════════════════════════════════════════════════════════

  return (
    <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm">
      {/* ─── HEADER (Título + Botón Nuevo) ─── */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-900">Inventario de Alimentos</h2>
          <p className="text-xs text-gray-400">
            {foods.length} alimento{foods.length !== 1 ? "s" : ""}
            {lowStockCount > 0 && (
              <> · <span className="text-amber-600"><AlertTriangle size={12} className="inline-block mr-0.5 -mt-0.5" /> {lowStockCount} con stock bajo</span></>
            )}
          </p>
        </div>
        <button
          onClick={() => {
            setEditing(undefined);
            setShowModal(true);
          }}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light"
        >
          + Nuevo alimento
        </button>
      </div>

      {/* ─── FILTROS POR CATEGORÍA ─── */}
      <div className="mb-4 flex flex-wrap gap-2">
        {/* Botón "Todos" */}
        <button
          onClick={() => setCategoryFilter("")}
          className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
            categoryFilter === ""
              ? "bg-primary text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Todos
        </button>

        {/* Botón para cada categoría */}
        {Object.entries(categoryCounts).map(([category, count]) => (
          <button
            key={category}
            onClick={() => setCategoryFilter(category)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              categoryFilter === category
                ? "bg-primary text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {category} ({count})
          </button>
        ))}
      </div>

      {/* ─── MENSAJE DE ERROR ─── */}
      {error && (
        <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* ─── ESTADO DE CARGA ─── */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : foods.length === 0 ? (
        /* ─── ESTADO VACÍO ─── */
        <div className="rounded-lg border border-dashed border-gray-200 py-10 text-center">
          <p className="text-sm text-gray-400">
            {categoryFilter
              ? "No hay alimentos en esta categoría"
              : "No hay alimentos registrados"}
          </p>
        </div>
      ) : (
        /* ─── TABLA DE ALIMENTOS ─── */
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-left text-xs font-semibold uppercase tracking-wide text-gray-400">
                <th className="pb-2 pr-4">Nombre</th>
                <th className="pb-2 pr-4">Categoría</th>
                <th className="pb-2 pr-4">Unidad</th>
                <th className="pb-2 pr-4">Stock actual</th>
                <th className="pb-2 pr-4">Stock mínimo</th>
                <th className="pb-2 pr-4">Precio unitario</th>
                <th className="pb-2 pr-4">Proveedor</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {foods.map((food) => {
                /**
                 * Detectar si el stock está bajo
                 * Si current_stock <= min_stock_alert, mostrar en rojo
                 */
                const isLowStock =
                  food.min_stock_alert &&
                  food.current_stock <= food.min_stock_alert;

                return (
                  <tr
                    key={food.id}
                    className={`hover:bg-gray-50 ${isLowStock ? "bg-amber-50" : ""}`}
                  >
                    <td className="py-3 pr-4 font-medium text-gray-800">
                      {food.name}
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                          CATEGORY_BADGE[food.category] ??
                          "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {food.category}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-gray-500">
                      {food.unit_of_measure}
                    </td>
                    <td
                      className={`py-3 pr-4 font-semibold ${
                        isLowStock ? "text-amber-700" : "text-gray-700"
                      }`}
                    >
                      {food.current_stock}
                      {isLowStock && <AlertTriangle size={12} className="inline-block ml-0.5 -mt-0.5 text-amber-600" />}
                    </td>
                    <td className="py-3 pr-4 text-gray-500">
                      {food.min_stock_alert ?? "—"}
                    </td>
                    <td className="py-3 pr-4 text-gray-500">
                      {food.cost_per_unit
                        ? `$${parseFloat(
                            food.cost_per_unit.toString()
                          ).toLocaleString("es-CO", {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 2,
                          })}`
                        : "—"}
                    </td>
                    <td className="py-3 pr-4 text-gray-500">
                      {food.supplier ?? "—"}
                    </td>
                    <td className="py-3">
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setEditing(food);
                            setShowModal(true);
                          }}
                          className="rounded px-2 py-1 text-xs font-medium text-gray-500 hover:bg-gray-100"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleDelete(food)}
                          disabled={actionLoading === food.id}
                          className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50 disabled:opacity-50"
                        >
                          {actionLoading === food.id ? "..." : "Eliminar"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ─── MODAL (Crear/Editar) ─── */}
      <FoodFormModal
        farmId={farmId}
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          setEditing(undefined);
        }}
        onSuccess={handleSuccess}
        existing={editing}
      />
    </div>
  );
}
