/*
 * MapaInteractivoFinca.tsx
 * What? Foto aérea de la finca (el archivo se muestra tal cual, sin modificar)
 *       con 8 zonas transparentes encima, una por lote. Hover → resaltado
 *       sutil + tooltip con datos vivos. Click → panel de detalle inline.
 * Why?  Vista general tipo "croquis aéreo real" de los lotes de la finca.
 * Impacto? Se muestra al inicio de la pestaña "Lotes y potreros", antes del
 *       mapa SVG (LandMap). No modifica la imagen ni las listas existentes;
 *       usa el mismo endpoint de lotes/potreros ya disponible.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { listPaddocks, type PaddockResponse } from "../../api/paddocks";
import { listLandPlots, type LandPlotResponse } from "../../api/land_plots";
import { getApiErrorMessage } from "../../api/errors";
import { USAGE_LABEL } from "./parcelGeometry";

interface Props {
  farmId: string;
}

/** Zonas sobre la imagen (en % del ancho/alto). Posiciones ajustadas sobre el mapa real. */
interface Zone {
  left: number;
  top: number;
  width: number;
  height: number;
}

const ZONES: Zone[] = [
  { left: 6, top: 2, width: 46, height: 31 }, // 1
  { left: 52, top: 3, width: 43, height: 30 }, // 2
  { left: 5, top: 33, width: 46, height: 27 }, // 3
  { left: 51, top: 33, width: 43, height: 27 }, // 4
  { left: 4, top: 61, width: 45, height: 32 }, // 5
  { left: 50, top: 60, width: 45, height: 34 }, // 6
];

const MAX_ZONES = ZONES.length;

const STATUS_LABEL: Record<string, string> = {
  libre: "Libre",
  ocupado: "Ocupado",
  en_descanso: "En descanso",
};

const COVERAGE_BADGE: Record<string, string> = {
  bueno: "bg-green-50 text-green-700",
  regular: "bg-amber-50 text-amber-700",
  malo: "bg-red-50 text-red-700",
};

const DEFAULT_STATUS = "libre";

/* Colores de los contornos en el modo inspección (?edit=1). */
const EDIT_COLORS = [
  "#eab308", "#22c55e", "#3b82f6", "#f97316",
  "#ef4444", "#a855f7", "#06b6d4", "#ec4899",
];

interface TooltipState {
  ix: number;
  x: number;
  y: number;
  cw: number;
}

function statusOf(p: PaddockResponse): string {
  return p.status in STATUS_LABEL ? p.status : DEFAULT_STATUS;
}

function coverageLabel(p: PaddockResponse): string {
  const c = p.coverage_status;
  if (c === "bueno") return "Cobertura buena";
  if (c === "regular") return "Cobertura regular";
  if (c === "malo") return "Cobertura mala";
  return "Cobertura —";
}

export default function MapaInteractivoFinca({ farmId }: Props) {
  const [searchParams] = useSearchParams();
  const editMode = searchParams.get("edit") === "1";
  const containerRef = useRef<HTMLDivElement>(null);

  const [paddocks, setPaddocks] = useState<PaddockResponse[]>([]);
  const [plots, setPlots] = useState<LandPlotResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [tip, setTip] = useState<TooltipState | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    setSelectedId(null);
    (async () => {
      try {
        const [p, l] = await Promise.all([listPaddocks(farmId), listLandPlots(farmId, true)]);
        if (cancelled) return;
        setPaddocks(p.filter((x) => x.is_active !== false));
        setPlots(l);
      } catch (err: unknown) {
        if (!cancelled) setError(getApiErrorMessage(err, "No se pudo cargar el mapa de la finca"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [farmId]);

  const activePlots = useMemo(
    () => [...plots]
      .filter((lot) => lot.is_active !== false)
      .sort((a, b) => new Date(a.created_at).valueOf() - new Date(b.created_at).valueOf()),
    [plots]
  );

  const zonePlots = activePlots.slice(0, MAX_ZONES);

  const byPlot = useMemo(() => {
    const map = new Map<string, PaddockResponse[]>();
    for (const p of paddocks) {
      const list = map.get(p.land_plot_id) ?? [];
      list.push(p);
      map.set(p.land_plot_id, list);
    }
    return map;
  }, [paddocks]);

  const selected = selectedId ? activePlots.find((lot) => lot.id === selectedId) ?? null : null;
  const selectedPaddocks = selected ? byPlot.get(selected.id) ?? [] : [];

  const summary = useMemo(() => {
    const hectares = paddocks.reduce((acc, p) => acc + Math.max(Number(p.area_hectares) || 0, 0), 0);
    return { hectares, total: paddocks.length };
  }, [paddocks]);

  const handleMouseMove = (ix: number, e: React.MouseEvent<HTMLButtonElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(rect.width, e.clientX - rect.left));
    const y = Math.max(0, Math.min(rect.height, e.clientY - rect.top));
    setTip({ ix, x, y, cw: rect.width });
  };

  const toggleZone = (id: string) => {
    setSelectedId((cur) => (cur === id ? null : id));
    setTip(null);
  };

  if (loading) {
    return (
      <div className="rounded-2xl bg-surface p-6 shadow-sm">
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </div>
    );
  }

  return (
    <section className="rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4">
        <h2 className="text-lg font-bold text-text-primary">Mapa interactivo de la finca</h2>
        <p className="text-xs text-text-muted">
          {zonePlots.length} zona{zonePlots.length !== 1 ? "s" : ""} · {paddocks.length} potrero{paddocks.length !== 1 ? "s" : ""} ·{" "}
          {summary.hectares.toFixed(1)} ha · pase el cursor o toque un lote para ver su información
        </p>
        {activePlots.length > MAX_ZONES && (
          <p className="mt-1 text-xs text-amber-600">Mostrando los primeros {MAX_ZONES} lotes sobre el mapa.</p>
        )}
      </div>

      {error && <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

      {activePlots.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">No hay lotes registrados en esta finca.</p>
          <p className="mt-1 text-xs text-text-muted">Cree un lote con sus potreros para ver el mapa.</p>
        </div>
      ) : (
        <div
          ref={containerRef}
          className="relative mx-auto w-full max-w-[1312px] overflow-hidden"
        >
          <img
            src="/imagenes/finca_ganadera.svg"
            alt="Mapa aéreo interactivo de la finca ganadera"
            className="block h-auto w-full select-none"
            draggable={false}
          />

          {zonePlots.map((lot, ix) => {
            const zone = ZONES[ix];
            const isSelected = selectedId === lot.id;
            return (
              <button
                key={lot.id}
                type="button"
                onClick={() => toggleZone(lot.id)}
                onMouseMove={(e) => handleMouseMove(ix, e)}
                onMouseLeave={() => setTip(null)}
                aria-label={`Ver información de ${lot.name}`}
                aria-pressed={isSelected}
                title={`${lot.name} (${lot.area} ${lot.area_unit})`}
                className="absolute z-10 block cursor-pointer rounded-sm border-0 bg-transparent p-0 transition duration-200 hover:bg-white/10 focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/90"
                style={{
                  left: `${zone.left}%`,
                  top: `${zone.top}%`,
                  width: `${zone.width}%`,
                  height: `${zone.height}%`,
                }}
              />
            );
          })}

          {tip && zonePlots[tip.ix] && (
            <div
              role="tooltip"
              className="pointer-events-none absolute z-20 rounded-lg bg-black/85 px-3 py-1.5 text-xs font-semibold text-white shadow-lg"
              style={{
                left: `${Math.max(0, Math.min(tip.x + 14, tip.cw - 190))}px`,
                top: `${tip.y + 14}px`,
              }}
            >
              {zonePlots[tip.ix].name} — {zonePlots[tip.ix].area} {zonePlots[tip.ix].area_unit}
              {byPlot.get(zonePlots[tip.ix].id)?.length
                ? ` · ${byPlot.get(zonePlots[tip.ix].id)?.length} potreros`
                : ""}
            </div>
          )}

          {editMode && (
            <div className="pointer-events-none absolute inset-0 z-30" aria-hidden="true">
              {zonePlots.map((lot, ix) => (
                <div
                  key={lot.id}
                  className="absolute flex items-center justify-center border-2 font-bold"
                  style={{
                    left: `${ZONES[ix].left}%`,
                    top: `${ZONES[ix].top}%`,
                    width: `${ZONES[ix].width}%`,
                    height: `${ZONES[ix].height}%`,
                    borderColor: EDIT_COLORS[ix % EDIT_COLORS.length],
                    color: EDIT_COLORS[ix % EDIT_COLORS.length],
                  }}
                >
                  <span className="rounded bg-black/60 px-1.5 py-0.5 text-xs">{ix + 1}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {selected && (
        <div className="mt-4 rounded-2xl border border-border bg-surface-alt p-4" data-testid="lote-detalle">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="text-base font-bold text-text-primary">{selected.name}</h3>
              <p className="text-xs text-text-secondary">
                {USAGE_LABEL(selected.usage_type)} · {selected.area} {selected.area_unit} · Cap. {selected.max_capacity} cabezas
              </p>
            </div>
            <button
              type="button"
              onClick={() => setSelectedId(null)}
              className="rounded-lg px-2 py-1 text-xs font-semibold text-text-secondary hover:bg-surface hover:text-text-primary"
            >
              Cerrar
            </button>
          </div>

          {selectedPaddocks.length === 0 ? (
            <p className="mt-3 text-sm text-text-muted">Este lote aún no tiene potreros.</p>
          ) : (
            <ul className="mt-3 grid gap-2 sm:grid-cols-2">
              {selectedPaddocks.map((p) => (
                <li key={p.id} className="rounded-xl bg-surface px-3 py-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-semibold text-text-primary">{p.name}</span>
                    <span className="text-xs text-text-secondary">{Number(p.area_hectares || 0).toFixed(2)} ha · Cap. {p.max_capacity}</span>
                  </div>
                  <div className="mt-1 flex flex-wrap gap-1.5">
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-medium text-primary">
                      {STATUS_LABEL[statusOf(p)]}
                    </span>
                    <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${COVERAGE_BADGE[p.coverage_status] ?? "bg-surface text-text-secondary"}`}>
                      {coverageLabel(p)}
                    </span>
                    {typeof p.animal_count === "number" && (
                      <span className="rounded-full bg-surface px-2 py-0.5 text-[11px] text-text-secondary">
                        {p.animal_count} bovino{p.animal_count !== 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  );
}