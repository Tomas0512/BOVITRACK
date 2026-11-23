import { Filter, Plus, Trash2, X } from "lucide-react";
import type { FilterCondition, FilterFieldDef } from "./bovineColumns";
import { CATEGORIES, fieldOf } from "./bovineColumns";

interface Props {
  open: boolean;
  onClose: () => void;
  fields: FilterFieldDef[];
  conditions: FilterCondition[];
  onChange: (conditions: FilterCondition[]) => void;
  onQuickField: (key: string) => void;
}

const OP_LABELS: Record<string, string> = {
  eq: "es igual a",
  ne: "no es igual a",
  contains: "contiene",
  gt: "mayor que",
  gte: "mayor o igual a",
  lt: "menor que",
  lte: "menor o igual a",
  date_from: "desde",
  date_to: "hasta",
};

export default function AdvancedFiltersPanel({ open, onClose, fields, conditions, onChange, onQuickField }: Props) {
  if (!open) return null;

  const update = (id: string, patch: Partial<FilterCondition>) => {
    onChange(conditions.map((c) => (c.id === id ? { ...c, ...patch } : c)));
  };

  const remove = (id: string) => {
    onChange(conditions.filter((c) => c.id !== id));
  };

  const renderValue = (field: FilterFieldDef | undefined, cond: FilterCondition) => {
    const cls = "w-full rounded-lg border border-border bg-white px-2 py-1.5 text-sm focus:border-primary focus:outline-none";
    if (!field) return <input className={cls} value={cond.value} onChange={(e) => update(cond.id, { value: e.target.value })} placeholder="Valor" />;
    if (field.type === "boolean") {
      return (
        <select className={cls} value={cond.op} onChange={(e) => update(cond.id, { op: e.target.value as FilterCondition["op"] })}>
          <option value="gt">Sí</option>
          <option value="eq">No</option>
        </select>
      );
    }
    if (field.type === "select" && field.options && field.options.length > 0) {
      return (
        <select className={cls} value={cond.value} onChange={(e) => update(cond.id, { value: e.target.value })}>
          <option value="">Seleccionar…</option>
          {field.options.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
      );
    }
    if (field.type === "date") {
      return (
        <input type="date" className={cls} value={cond.value} onChange={(e) => update(cond.id, { value: e.target.value })} />
      );
    }
    return (
      <input
        type={field.type === "number" ? "number" : "text"}
        className={cls}
        value={cond.value}
        onChange={(e) => update(cond.id, { value: e.target.value })}
        placeholder="Valor"
      />
    );
  };

  const addFromCategory = (key: string) => {
    onQuickField(key);
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30" onClick={onClose}>
      <div
        className="flex h-full w-full flex-col bg-surface shadow-2xl sm:max-w-md"
        role="dialog"
        aria-label="Filtros avanzados"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-2 border-b border-border px-4 py-3">
          <Filter size={18} className="mt-0.5 text-primary" />
          <div className="min-w-0">
            <h2 className="text-sm font-bold text-text-primary">Filtros avanzados</h2>
            <p className="text-xs text-text-muted">Encuentra bovinos utilizando cualquier dato registrado.</p>
          </div>
          <button onClick={onClose} aria-label="Cerrar" className="ml-auto rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-3">
          {conditions.length > 0 ? (
            <div className="mb-4">
              <div className="mb-1.5 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Condiciones actuales</p>
                <button onClick={() => onChange([])} className="text-xs font-medium text-red-500 hover:underline">
                  Limpiar todo
                </button>
              </div>
              <div className="space-y-2">
                {conditions.map((cond, idx) => {
                  const field = fieldOf(fields, cond.field);
                  return (
                    <div key={cond.id} className="rounded-lg border border-border bg-surface-alt/50 p-2">
                      <div className="flex items-center gap-1.5">
                        <select
                          className="rounded-md border border-border bg-white px-1 py-1 text-xs font-medium focus:outline-none"
                          value={idx === 0 ? "AND" : cond.connector}
                          onChange={(e) => update(cond.id, { connector: e.target.value as "AND" | "OR" })}
                          disabled={idx === 0}
                          title={idx === 0 ? "Primera condición" : "Conector"}
                        >
                          <option value="AND">Y</option>
                          <option value="OR">O</option>
                        </select>
                        <span className="truncate text-xs font-medium text-text-primary">{field?.label ?? cond.field}</span>
                        <button onClick={() => remove(cond.id)} aria-label="Quitar condición" className="ml-auto rounded p-0.5 text-text-muted hover:text-red-500">
                          <Trash2 size={14} />
                        </button>
                      </div>
                      <div className="mt-1.5 grid grid-cols-[auto_1fr] items-center gap-1.5">
                        <select
                          className="rounded-md border border-border bg-white px-1 py-1.5 text-xs focus:outline-none"
                          value={cond.op}
                          onChange={(e) => update(cond.id, { op: e.target.value as FilterCondition["op"] })}
                        >
                          <option value="">…</option>
                          {field?.ops.map((o) => (
                            <option key={o} value={o}>{OP_LABELS[o] ?? o}</option>
                          ))}
                        </select>
                        {renderValue(field, cond)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <p className="mb-4 rounded-lg border border-dashed border-border px-3 py-2 text-xs text-text-muted">
              Aún no hay condiciones. Usa las categorías de abajo para construir tu consulta (Y / O).
            </p>
          )}

          <div className="mb-2 flex items-center gap-1.5">
            <Plus size={15} className="text-primary" />
            <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">Agregar filtro por categoría</p>
          </div>

          <div className="space-y-4">
            {CATEGORIES.map((cat) => {
              const catFields = fields.filter((f) => f.category === cat.id);
              if (catFields.length === 0) return null;
              return (
                <div key={cat.id}>
                  <p className="mb-1.5 border-b border-border pb-1 text-xs font-bold text-text-secondary">{cat.label}</p>
                  <div className="grid grid-cols-1 gap-1">
                    {catFields.map((f) => (
                      <button
                        key={f.key}
                        disabled={!f.available}
                        onClick={() => addFromCategory(f.key)}
                        className={`flex items-center justify-between rounded-lg border px-2.5 py-1.5 text-left text-sm transition-colors ${
                          f.available
                            ? "border-border text-text-secondary hover:border-primary hover:bg-primary/5 hover:text-primary"
                            : "cursor-not-allowed border-dashed border-border bg-surface-alt/40 text-text-muted/50"
                        }`}
                      >
                        <span className="truncate">{f.label}</span>
                        {f.available ? (
                          <Plus size={14} className="shrink-0" />
                        ) : (
                          <span className="shrink-0 rounded bg-surface-alt px-1 py-0.5 text-[10px] font-medium text-text-muted">
                            Próximamente
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}