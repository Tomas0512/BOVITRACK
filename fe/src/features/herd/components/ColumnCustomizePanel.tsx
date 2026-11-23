import { useRef, useState } from "react";
import { GripVertical, Settings2, RotateCcw, X } from "lucide-react";
import { COLUMN_DEFS, DEFAULT_VISIBLE_COLUMNS } from "./bovineColumns";

interface Props {
  onClose: () => void;
  orderedKeys: string[];
  visible: Set<string>;
  onApply: (orderedKeys: string[], visible: Set<string>) => void;
}

function orderFromDefs(keys: string[]): string[] {
  const byDef = COLUMN_DEFS.map((c) => c.key);
  const set = new Set(keys.filter((k) => byDef.includes(k)));
  return byDef.filter((k) => set.has(k)).concat(byDef.filter((k) => !set.has(k)));
}

export default function ColumnCustomizePanel({ onClose, orderedKeys, visible, onApply }: Props) {
  const [keys, setKeys] = useState<string[]>(() => orderFromDefs(orderedKeys));
  const [vis, setVis] = useState<Set<string>>(new Set(visible));
  const dragIndex = useRef<number | null>(null);

  const toggle = (key: string) => {
    setVis((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  };

  const move = (from: number, to: number) => {
    setKeys((prev) => {
      const next = [...prev];
      const [item] = next.splice(from, 1);
      next.splice(to, 0, item);
      return next;
    });
  };

  const reset = () => {
    setKeys(orderFromDefs(DEFAULT_VISIBLE_COLUMNS));
    setVis(new Set(DEFAULT_VISIBLE_COLUMNS));
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/30" onClick={onClose}>
      <div
        className="flex h-full w-full flex-col bg-surface shadow-2xl sm:w-96"
        role="dialog"
        aria-label="Personalizar columnas"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <Settings2 size={18} className="text-primary" />
          <h2 className="text-sm font-bold text-text-primary">Personalizar columnas</h2>
          <button onClick={onClose} aria-label="Cerrar" className="ml-auto rounded-lg p-1 text-text-muted hover:bg-surface-alt hover:text-text-secondary">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-3">
          <p className="mb-3 text-xs text-text-muted">Marca qué columnas ver y arrástralas para cambiar el orden.</p>

          <div className="space-y-1">
            {keys.map((key, index) => {
              const def = COLUMN_DEFS.find((c) => c.key === key);
              if (!def) return null;
              const checked = vis.has(key);
              return (
                <div
                  key={key}
                  draggable
                  onDragStart={() => (dragIndex.current = index)}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={() => {
                    if (dragIndex.current !== null && dragIndex.current !== index) move(dragIndex.current, index);
                    dragIndex.current = null;
                  }}
                  onDragEnd={() => (dragIndex.current = null)}
                  className={`flex cursor-grab items-center gap-2 rounded-lg border px-2 py-2 transition-colors active:cursor-grabbing ${
                    checked ? "border-border bg-surface" : "border-dashed border-border bg-surface-alt/40 text-text-muted"
                  }`}
                >
                  <GripVertical size={16} className="shrink-0 text-text-muted" />
                  <label className="flex min-w-0 flex-1 cursor-pointer items-center gap-2">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggle(key)}
                      className="h-4 w-4 accent-primary"
                    />
                    <span className="truncate text-sm font-medium text-text-primary">{def.label}</span>
                  </label>
                  <span className="shrink-0 rounded bg-surface-alt px-1.5 py-0.5 text-[10px] font-medium text-text-muted">
                    {def.group}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex items-center justify-between gap-2 border-t border-border px-4 py-3">
          <button
            onClick={reset}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium text-text-secondary hover:bg-surface-alt"
          >
            <RotateCcw size={15} /> Restablecer
          </button>
          <button
            onClick={() => onApply(keys, vis)}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light"
          >
            Aplicar
          </button>
        </div>
      </div>
    </div>
  );
}