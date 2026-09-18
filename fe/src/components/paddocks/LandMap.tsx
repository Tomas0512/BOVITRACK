/*
 * LandMap.tsx
 * What? Mapa orgánico (croquis SVG) de la finca: lotes y potreros como parcelas
 *       de formas irregulares sobre un terreno con textura, senderos, casa,
 *       árboles, charco y brújula.
 * Why?  Leer la distribución del terreno de un vistazo: el tamaño de cada
 *       parcela es proporcional a sus hectáreas y el color, NATURAL, sigue el
 *       uso del lote y la cobertura del potrero (el estado libre/ocupado/en
 *       descanso NO se refleja en el color del terreno, solo como información).
 * Impacto? Se muestra al inicio de la pestaña "Lotes y potreros". No altera
 *       las listas existentes; solo usa los mismos endpoints ya disponibles.
 */

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { AlertTriangle } from "lucide-react";
import { listPaddocks, type PaddockResponse } from "../../api/paddocks";
import { listLandPlots, type LandPlotResponse } from "../../api/land_plots";
import { getApiErrorMessage } from "../../api/errors";
import { squarifiedTreemap, type TreemapInput, type TreemapRect } from "./treemapLayout";
import {
  USAGE_BASE,
  USAGE_LABEL,
  hashRange,
  parcelFillColor,
  parcelPath,
  rectToParcel,
  type Point,
} from "./parcelGeometry";

interface Props {
  farmId: string;
}

const STATUS_LABEL: Record<string, string> = {
  libre: "Libre",
  ocupado: "Ocupado",
  en_descanso: "En descanso",
};

const DEFAULT_STATUS = "libre";

/* Las hectáreas mínimas que representa un potrero en el esquema (evita parcelas de área 0). */
const MIN_UNITS = 0.1;
/* Área mínima para dibujar la etiqueta dentro del potrero. */
const LABEL_MIN_W = 84;

/* Colores de la finca (terreno). */
const SOIL = "#c9b693";
const SOIL_DEEP = "#7a5a34";
const FERTILE = "#e4d9b9";
const CANOPY = "#3f6b3f";
const CANOPY_LIGHT = "#5d8a55";
const LABEL_TEXT = "#fefcf5";

/* Márgenes que rodean las parcelas (casa, camino, charco y brújula viven ahí). */
const MARGIN = { top: 54, side: 30, bottom: 48 };
/* Ancho del sendero de tierra que separa dos parcelas vecinas. */
const DIRT_GAP = 8;

function areaTotal(items: PaddockResponse[]): number {
  return items.reduce((acc, p) => acc + Math.max(Number(p.area_hectares) || 0, MIN_UNITS), 0);
}

function statusOf(p: PaddockResponse): string {
  return p.status in STATUS_LABEL ? p.status : DEFAULT_STATUS;
}

export default function LandMap({ farmId }: Props) {
  const [paddocks, setPaddocks] = useState<PaddockResponse[]>([]);
  const [plots, setPlots] = useState<LandPlotResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

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

  const byPlot = useMemo(() => {
    const map = new Map<string, PaddockResponse[]>();
    for (const p of paddocks) {
      const list = map.get(p.land_plot_id) ?? [];
      list.push(p);
      map.set(p.land_plot_id, list);
    }
    return map;
  }, [paddocks]);

  const activePlots = useMemo(
    () => [...plots].filter((lot) => lot.is_active !== false)
      .sort((a, b) => a.name.localeCompare(b.name, "es")),
    [plots]
  );

  /* Distribución de los lotes dentro del terreno (márgenes aparte). */
  const layout = useMemo(() => {
    const width = 1000;
    const innerW = width - MARGIN.side * 2;
    const totalUnits = activePlots.reduce((acc, lot) => acc + areaTotal(byPlot.get(lot.id) ?? []), 0);
    const height = Math.max(380, Math.min(960, Math.round(240 + totalUnits * 6)));
    const innerH = height - MARGIN.top - MARGIN.bottom;
    const inputs: TreemapInput[] = activePlots.map((lot) => ({
      key: lot.id,
      value: areaTotal(byPlot.get(lot.id) ?? []),
    }));
    const rects = squarifiedTreemap(inputs, innerW, innerH).map((r) => ({
      key: r.key,
      x: r.x + MARGIN.side,
      y: r.y + MARGIN.top,
      width: r.width,
      height: r.height,
    }));
    return {
      width,
      height,
      innerX: MARGIN.side,
      innerY: MARGIN.top,
      innerW,
      innerH,
      rects,
    };
  }, [activePlots, byPlot]);

  const selected = paddocks.find((p) => p.id === selectedId) ?? null;

  const summaryTotal = useMemo(() => {
    const hectares = paddocks.reduce((acc, p) => acc + Math.max(Number(p.area_hectares) || 0, 0), 0);
    return { hectares, total: paddocks.length };
  }, [paddocks]);

  const statusCount = (status: string): number => paddocks.filter((p) => statusOf(p) === status).length;

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
    <div className="rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-text-primary">Mapa de la finca</h2>
          <p className="text-xs text-text-muted">
            {activePlots.length} lote{activePlots.length !== 1 ? "s" : ""} · {summaryTotal.total} potrero{summaryTotal.total !== 1 ? "s" : ""} ·{" "}
            {summaryTotal.hectares.toFixed(1)} ha
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
          {Object.entries(USAGE_BASE).map(([usage, color]) => (
            <span key={usage} className="inline-flex items-center gap-1.5 text-xs text-text-secondary">
              <span className="h-3 w-3 rounded-sm" style={{ backgroundColor: color }} aria-hidden="true" />
              {USAGE_LABEL(usage)}
            </span>
          ))}
          <span className="inline-flex items-center gap-1.5 text-xs text-text-secondary">
            <span className="h-3 w-3 rounded-sm" style={{ backgroundColor: parcelFillColor(USAGE_BASE.pastoreo, "malo") }} aria-hidden="true" />
            tramado = cobertura mala
          </span>
        </div>
      </div>

      {error && <div className="mb-3 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>}

      {activePlots.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">No hay lotes registrados en esta finca.</p>
          <p className="mt-1 text-xs text-text-muted">Cree un lote con sus potreros para ver el mapa.</p>
        </div>
      ) : (
        <>
          <svg
            viewBox={`0 0 ${layout.width} ${layout.height}`}
            className="w-full select-none"
            role="img"
            aria-label={`Mapa de la finca con ${activePlots.length} lotes y ${paddocks.length} potreros`}
          >
            <defs>
              {/* Textura de pasto: grano sutil sobre todo el terreno. */}
              <filter id="pasture-grain" x="0" y="0" width="100%" height="100%">
                <feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="3" result="noise" />
                <feColorMatrix
                  in="noise"
                  type="matrix"
                  values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.07 0"
                />
              </filter>
              {/* Tramado que marca cobertura mala. */}
              <pattern id="coverage-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                <line x1="0" y1="0" x2="0" y2="9" stroke="#3a2a16" strokeWidth="2" opacity="0.45" />
              </pattern>
            </defs>

            {/* Terreno: límite exterior ondulado tipo cerca doble. */}
            <BoundaryBox x={layout.innerX} y={layout.innerY} width={layout.innerW} height={layout.innerH} />

{/* Decoración de terreno bajo las parcelas: casa, camino y
                 brújula se dibujan PRIMERO para no tapar potreros. */}
            <HouseAndPath innerX={layout.innerX} innerY={layout.innerY} />
            <Compass cx={layout.width - 44} cy={20} />

            {/* Parcelas (lotes) */}
            {layout.rects.map((lotRect) => {
              const lot = activePlots.find((l) => l.id === lotRect.key);
              if (!lot) return null;
              const lotPaddocks = byPlot.get(lot.id) ?? [];
              const outer = rectToParcel(lotRect, { amp: 9 });
              return (
                <g key={lot.id} clipPath={`url(#clip-${lot.id})`}>
                  <clipPath id={`clip-${lot.id}`}>
                    <path d={parcelPath(outer)} />
                  </clipPath>

                  {/* Fondo del lote (tono tierra más profundo) + línea interior de contorno. */}
                  <path
                    d={parcelPath(outer)}
                    fill={FERTILE}
                    stroke={SOIL}
                    strokeWidth={DIRT_GAP + 7}
                    strokeLinejoin="round"
                  />
                  <path
                    d={parcelPath(scaleCentroid(outer, 0.92))}
                    fill="none"
                    stroke={SOIL_DEEP}
                    strokeWidth={1.6}
                    strokeDasharray="8 5"
                    opacity={0.7}
                  />

                  {lotPaddocks.length === 0 ? (
                    <text
                      x={lotRect.x + lotRect.width / 2}
                      y={lotRect.y + lotRect.height / 2 + 10}
                      textAnchor="middle"
                      fill={LABEL_TEXT}
                      fontSize={13}
                      stroke="rgba(20,24,16,0.65)"
                      strokeWidth={3}
                      paintOrder="stroke"
                    >
                      Sin potreros
                    </text>
                  ) : (
                    <>
                      <LotPaddocks
                        lotRect={lotRect}
                        paddocks={lotPaddocks}
                        usage={lot.usage_type}
                        onSelect={setSelectedId}
                        onHover={setHoveredId}
                        hoveredId={hoveredId}
                        selectedId={selectedId}
                      />
                      {/* Mancha de bosque en terrenos arbolados. */}
                      <ForestPatch lotId={lot.id} usage={lot.usage_type} rect={lotRect} />
                    </>
                  )}

                  {/* Placa/letrero del lote con texto integrado al terreno. */}
                  <LotLabel lot={lot} rect={lotRect} area={areaTotal(lotPaddocks)} />
                </g>
              );
            })}

            {/* Grano de pasto sobre todo el dibujo (no interfiere con clics). */}
            <rect width={layout.width} height={layout.height} filter="url(#pasture-grain)" pointerEvents="none" />
          </svg>

          {selected ? (
            <div className="mt-4 rounded-xl border border-border bg-surface-alt/60 p-4" aria-live="polite">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <h3 className="text-sm font-bold text-text-primary">{selected.name}</h3>
                <span className="rounded-full bg-neutral-200 px-2 py-0.5 text-xs font-medium text-neutral-700">
                  {STATUS_LABEL[statusOf(selected)]}
                </span>
                <span className="text-xs text-text-muted">{selected.land_plot_name ?? ""}</span>
              </div>
              <div className="grid gap-x-6 gap-y-1 text-xs text-text-secondary sm:grid-cols-2 lg:grid-cols-3">
                <p><span className="font-semibold text-text-primary">Área:</span> {Number(selected.area_hectares).toFixed(2)} ha</p>
                <p><span className="font-semibold text-text-primary">Capacidad:</span> {selected.max_capacity} animales</p>
                <p>
                  <span className="font-semibold text-text-primary">Ocupación:</span> {selected.animal_count ?? 0}
                  {selected.max_capacity ? ` de ${selected.max_capacity}` : ""}
                </p>
                <p><span className="font-semibold text-text-primary">Cobertura:</span> {selected.coverage_status}</p>
                {selected.pasture_type && (
                  <p><span className="font-semibold text-text-primary">Pasto:</span> {selected.pasture_type.replace(/_/g, " ")}</p>
                )}
                <p>
                  <span className="font-semibold text-text-primary">Resto activo:</span> {statusCount(statusOf(selected))} potrero{statusCount(statusOf(selected)) !== 1 ? "s" : ""} {STATUS_LABEL[statusOf(selected)].toLowerCase()}
                </p>
              </div>
              <div className="mt-3 rounded-lg bg-surface p-2">
                <p className="text-xs font-semibold text-text-secondary">
                  Animales en el potrero: {selected.animal_count ?? 0}
                </p>
                {selected.animals && selected.animals.length > 0 ? (
                  <div className="mt-1 flex flex-wrap gap-1">
                    {selected.animals.map((a) => (
                      <span key={a.id} className="rounded bg-surface-alt px-1.5 py-0.5 text-[11px] text-text-secondary">
                        #{a.identification_number}{a.name ? ` · ${a.name}` : ""}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-1 text-xs text-text-muted">Sin animales asignados.</p>
                )}
              </div>
            </div>
          ) : (
            <p className="mt-3 text-xs text-text-muted">
              <AlertTriangle size={12} className="mr-1 inline-block -mt-0.5" />
              Seleccione un potrero en el mapa para ver su detalle.
            </p>
          )}
        </>
      )}
    </div>
  );
}

/* Límite exterior del terreno: sendero ancho + cerca punteada. */
function BoundaryBox({ x, y, width, height }: { x: number; y: number; width: number; height: number }) {
  const d = parcelPath(rectToParcel({ x, y, width, height }, { amp: 10 }));
  return (
    <g>
      <path d={d} fill="none" stroke={SOIL} strokeWidth={16} strokeLinejoin="round" />
      <path d={d} fill="none" stroke={SOIL_DEEP} strokeWidth={2} strokeDasharray="16 9" strokeLinecap="round" />
    </g>
  );
}

/* Mancha de bosque orgánica: grupo de copas y siluetas de árbol (reserva / cultivo). */
function ForestPatch({ lotId, usage, rect }: { lotId: string; usage: string; rect: TreemapRect }) {
  if (usage !== "reserva" && usage !== "cultivo") return null;
  const pad = 26;
  const bx = rect.x + pad;
  const by = rect.y + pad;
  const bxw = Math.max(40, rect.width - pad * 2);
  const byh = Math.max(40, rect.height * 0.5 - pad);
  const cx = hashRange(`forest:${lotId}:x`, bx, bx + bxw);
  const cy = hashRange(`forest:${lotId}:y`, by, by + byh);
  const n = 6;
  const trunks: ReactNode[] = [];
  const canopies: ReactNode[] = [];
  for (let i = 0; i < n; i++) {
    const a = hashRange(`forest:${lotId}:a:${i}`, 0, Math.PI * 2);
    const rr = hashRange(`forest:${lotId}:r:${i}`, 0, 16);
    const rad = hashRange(`forest:${lotId}:rad:${i}`, 10, 17);
    const x = cx + Math.cos(a) * rr;
    const y = cy + Math.sin(a) * rr;
    trunks.push(<line key={`t${i}`} x1={x} y1={y + rad * 0.35} x2={x - 2} y2={y - rad * 0.85} stroke="#6b4a2b" strokeWidth={4} strokeLinecap="round" />);
    canopies.push(<circle key={`c${i}`} cx={x} cy={y} r={rad} fill={CANOPY} />);
  }
  return (
    <g aria-hidden="true">
      {trunks}
      {canopies}
      <circle cx={cx - 8} cy={cy - 9} r={6} fill={CANOPY_LIGHT} opacity={0.5} />
    </g>
  );
}

/* Escala un polígono respecto a su centroide. */
function scaleCentroid(pts: Point[], f: number): Point[] {
  const cx = pts.reduce((s, p) => s + p.x, 0) / pts.length;
  const cy = pts.reduce((s, p) => s + p.y, 0) / pts.length;
  return pts.map((p) => ({ x: cx + (p.x - cx) * f, y: cy + (p.y - cy) * f }));
}

/* Etiqueta de texto claro integrada al terreno (estilo del diseño). */
function LotLabel({ lot, rect, area }: { lot: LandPlotResponse; rect: TreemapRect; area: number }) {
  if (rect.width < 210 || rect.height < 96) {
    return (
      <text x={rect.x + 14} y={rect.y + 20} fill={LABEL_TEXT} fontSize={15} fontWeight={700} stroke="rgba(20,24,16,0.7)" strokeWidth={3} paintOrder="stroke">
        {lot.name}
      </text>
    );
  }
  const angle = hashRange(`placard:${lot.id}`, -2.5, 2.5);
  const cx = rect.x + rect.width / 2;
  const cy = rect.y + 26;
  return (
    <g transform={`translate(${cx} ${cy}) rotate(${angle.toFixed(1)})`} aria-hidden="true">
      <text x={0} y={-3} textAnchor="middle" fill={LABEL_TEXT} fontSize={14} fontWeight={700} stroke="rgba(20,24,16,0.7)" strokeWidth={3} paintOrder="stroke">
        {lot.name}
      </text>
      <text x={0} y={13} textAnchor="middle" fill="#f0e2c8" fontSize={11} stroke="rgba(20,24,16,0.7)" strokeWidth={3} paintOrder="stroke">
        {USAGE_LABEL(lot.usage_type)} · {area.toFixed(1)} ha
      </text>
    </g>
  );
}

/* Casa de la finca con el camino de entrada (solo en el margen, no cruza las parcelas). */
function HouseAndPath({ innerX, innerY }: { innerX: number; innerY: number }) {
  const hx = innerX + 18;
  const hy = 6;
  const doorX = hx + 17;
  const doorY = hy + 22;
  return (
    <g aria-hidden="true">
      <path
        d={`M ${doorX} ${doorY} Q ${Math.round(innerX * 0.6)} ${Math.round(innerY * 0.55)} ${innerX + 8} ${innerY}`}
        fill="none"
        stroke={SOIL}
        strokeWidth={10}
        strokeLinecap="round"
        opacity={0.9}
      />
      <g transform={`translate(${hx} ${hy})`}>
        <rect x="0" y="12" width="34" height="22" rx="2" fill="#c9a06a" />
        <path d="M -3 14 L 17 2 L 37 14 Z" fill="#a4512a" stroke="#6d2f16" strokeWidth={1.5} strokeLinejoin="round" />
        <rect x="12" y="20" width="10" height="14" rx="1.5" fill="#5a4024" />
        <rect x="4" y="17" width="6" height="6" rx="1" fill="#f4e7c8" />
      </g>
    </g>
  );
}

/* Brújula con el norte señalado. */
function Compass({ cx, cy }: { cx: number; cy: number }) {
  return (
    <g aria-label="Norte" role="img">
      <circle cx={cx} cy={cy} r={17} fill="#f5edda" stroke={SOIL_DEEP} strokeWidth={1.5} />
      <line x1={cx} y1={cy - 12} x2={cx} y2={cy + 12} stroke="#b9a178" strokeWidth={2} />
      <polygon points={`${cx - 4.5},${cy} ${cx},${cy - 11} ${cx + 4.5},${cy}`} fill="#b5412a" />
      <polygon points={`${cx - 4.5},${cy} ${cx},${cy + 11} ${cx + 4.5},${cy}`} fill="#7a8a6a" />
      <text x={cx} y={cy + 24} textAnchor="middle" fill={SOIL_DEEP} fontSize={12} fontWeight={700}>
        N
      </text>
    </g>
  );
}

/* Reparto y render de los potreros dentro de un lote, como parcelas orgánicas. */
function LotPaddocks({
  lotRect,
  paddocks,
  usage,
  onSelect,
  onHover,
  hoveredId,
  selectedId,
}: {
  lotRect: TreemapRect;
  paddocks: PaddockResponse[];
  usage: string;
  onSelect: (id: string | null) => void;
  onHover: (id: string | null) => void;
  hoveredId: string | null;
  selectedId: string | null;
}) {
  if (lotRect.width < 60 || lotRect.height < 40) {
    return (
      <text x={lotRect.x + lotRect.width / 2} y={lotRect.y + lotRect.height / 2} textAnchor="middle" fill={LABEL_TEXT} fontSize={12} stroke="rgba(20,24,16,0.65)" strokeWidth={3} paintOrder="stroke">
        {paddocks.length} potrero{paddocks.length !== 1 ? "s" : ""}
      </text>
    );
  }

  const items: TreemapInput[] = paddocks.map((p) => ({
    key: p.id,
    value: Math.max(Number(p.area_hectares) || 0, MIN_UNITS),
  }));

  return (
    <g>
      {squarifiedTreemap(items, lotRect.width, lotRect.height).map((rect) => {
        const r = { x: rect.x + lotRect.x, y: rect.y + lotRect.y, width: rect.width, height: rect.height };
        const p = paddocks.find((x) => x.id === rect.key)!;
        const status = statusOf(p);
        const isActive = selectedId === p.id;
        const isHover = hoveredId === p.id;
        const fill = parcelFillColor(usage, p.coverage_status);
        const fg = LABEL_TEXT;
        const polygon = rectToParcel(r);
        const d = parcelPath(polygon);
        const showLabel = r.width >= LABEL_MIN_W && r.height >= 28;
        const showArea = r.width >= 132 && r.height >= 44;
        const centerX = r.x + r.width / 2;
        const centerY = r.y + r.height / 2;
        const labelY = showArea ? centerY - 1 : centerY;
        const angle = hashRange(`rot:${p.id}`, -2.5, 2.5);
        return (
          <g
            key={p.id}
            role="button"
            tabIndex={0}
            aria-label={`Potrero ${p.name}, ${Number(p.area_hectares).toFixed(1)} hectáreas, ${STATUS_LABEL[status]}`}
            onClick={() => onSelect(isActive ? null : p.id)}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(isActive ? null : p.id); } }}
            onMouseEnter={() => onHover(p.id)}
            onMouseLeave={() => onHover(null)}
            className="cursor-pointer outline-none"
          >
            <title>{`${p.name} — ${Number(p.area_hectares).toFixed(1)} ha · ${STATUS_LABEL[status]}${p.animal_count ? ` · ${p.animal_count} animales` : ""}`}</title>
            {/* Terreno: relleno de pasto con borde de sendero (y resaltado si está seleccionado). */}
            <path
              d={d}
              fill={fill}
              stroke={isActive ? "#ffffff" : SOIL}
              strokeWidth={isActive ? DIRT_GAP + 2 : DIRT_GAP}
              strokeLinejoin="round"
              opacity={isHover && !isActive ? 0.82 : 1}
            />
            {/* Cerca de la parcela. */}
            <path d={d} fill="none" stroke="#3f2f18" strokeWidth={1} strokeDasharray="5 4" opacity={0.55} />
            {/* Cobertura mala: tramado de pasto degradado. */}
            {p.coverage_status === "malo" && (
              <path d={d} fill="url(#coverage-hatch)" opacity={0.6} pointerEvents="none" />
            )}
            {showLabel && (
              <g transform={`rotate(${angle.toFixed(1)} ${centerX} ${labelY})`}>
                <text
                  x={centerX}
                  y={labelY}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill={fg}
                  stroke="rgba(20,24,16,0.65)"
                  strokeWidth={3}
                  paintOrder="stroke"
                  fontSize={13}
                  fontWeight="700"
                >
                  {p.name}
                </text>
                {showArea && (
                  <text
                    x={centerX}
                    y={labelY + 14}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fill={fg}
                    stroke="rgba(20,24,16,0.65)"
                    strokeWidth={3}
                    paintOrder="stroke"
                    fontSize={11}
                    opacity={0.92}
                  >
                    {Number(p.area_hectares).toFixed(1)} ha · {p.max_capacity} cap.
                  </text>
                )}
              </g>
            )}
          </g>
        );
      })}
    </g>
  );
}