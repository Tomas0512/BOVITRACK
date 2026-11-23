/*
 * parcelGeometry.ts
 * What? Geometría y color para el mapa orgánico de la finca.
 * Why?  Convertir los rectángulos del treemap en parcelas de formas irregulares
 *       (croquis de finca) y definir una paleta natural según el uso del lote
 *       y su estado de cobertura. Funciones puras y deterministas para poder
 *       probarlas y para que parcelas vecinas compartan exactamente la misma
 *       línea de frontera (sin huecos ni solapamientos).
 * Impacto? Sin dependencias externas. El estado (libre/ocupado/en descanso) NO
 *       participa en el color del terreno.
 */

export interface Point {
  x: number;
  y: number;
}

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

/* ── Números seudoaleatorios deterministas ─────────────────────────────── */

export function hash01(seed: string): number {
  let h = 1779033703 ^ seed.length;
  for (let i = 0; i < seed.length; i++) {
    h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
    h = (h << 13) | (h >>> 19);
  }
  h = Math.imul(h ^ (h >>> 16), 2246822507);
  h = Math.imul(h ^ (h >>> 13), 3266489909);
  const x = (h ^ (h >>> 16)) >>> 0;
  return x / 4294967296;
}

export function hashRange(seed: string, min: number, max: number): number {
  return min + hash01(seed) * (max - min);
}

const round2 = (n: number): string => n.toFixed(3);

/* ── Geometría de parcelas orgánicas ───────────────────────────────────── */

/**
 * Clave estable para una arista: se ordenan los extremos para que el vecino
 * que comparte la misma arista (en orientación contraria) calcule el mismo id.
 */
function edgeKey(a: Point, b: Point): string {
  const isForward = a.x < b.x || (a.x === b.x && a.y <= b.y);
  const p = isForward ? a : b;
  const q = isForward ? b : a;
  return `${round2(p.x)}:${round2(p.y)}:${round2(q.x)}:${round2(q.y)}`;
}

/** Desplazamiento determinista de una esquina según su coordenada absoluta. */
function cornerShift(px: number, py: number, amp: number): { dx: number; dy: number } {
  return {
    dx: hashRange(`cx:${round2(px)}:${round2(py)}`, -amp, amp),
    dy: hashRange(`cy:${round2(px)}:${round2(py)}`, -amp, amp),
  };
}

/**
 * Puntos intermedios de una arista ondulada. El posicionamiento y la
 * ondulación se calculan SIEMPRE en la orientación canónica de la arista
 * (recorrida de arriba hacia abajo en verticales y de izquierda a derecha en
 * horizontales), de modo que la parcela vecina que comparte la arista —aunque
 * la dibuje en sentido contrario— genera exactamente los mismos puntos.
 */
function wavyEdge(a: Point, b: Point, nPts: number, amp: number): Point[] {
  const isForward = a.x < b.x || (a.x === b.x && a.y <= b.y);
  const p = isForward ? a : b;
  const q = isForward ? b : a;
  const dx = q.x - p.x;
  const dy = q.y - p.y;
  const len = Math.hypot(dx, dy) || 1;
  const nx = -dy / len;
  const ny = dx / len;
  const key = edgeKey(p, q);
  const raw: Point[] = [];
  for (let i = 1; i < nPts; i++) {
    const t = i / nPts;
    const off = hashRange(`${key}:${i}`, -amp, amp);
    raw.push({ x: p.x + dx * t + nx * off, y: p.y + dy * t + ny * off });
  }
  /* Se devuelven en el orden de recorrido pedido (a→b) para no romper el polígono. */
  return isForward ? raw : raw.reverse();
}

export interface ParcelOptions {
  /** Amplitud del desplazamiento de esquinas (px). */
  amp?: number;
  /** Segmentos por arista (2 = un solo punto intermedio). */
  segments?: number;
}

/**
 * Convierte un rectángulo del treemap en un polígono orgánico (parcela).
 * El desplazamiento de esquinas depende de su coordenada absoluta y el de las
 * aristas de edgeKey, garantizando que parcelas adyacentes coinciden borde a
 * borde.
 */
export function rectToParcel(rect: Rect, opts: ParcelOptions = {}): Point[] {
  const minSide = Math.min(rect.width, rect.height);
  const amp = opts.amp ?? Math.max(2, Math.min(minSide * 0.07, 7));
  const edgeAmp = amp * 0.55;

  const { x, y, w, h } = { x: rect.x, y: rect.y, w: rect.width, h: rect.height };
  const cTL = cornerShift(x, y, amp);
  const cTR = cornerShift(x + w, y, amp);
  const cBR = cornerShift(x + w, y + h, amp);
  const cBL = cornerShift(x, y + h, amp);

  const TL: Point = { x: x + cTL.dx, y: y + cTL.dy };
  const TR: Point = { x: x + w + cTR.dx, y: y + cTR.dy };
  const BR: Point = { x: x + w + cBR.dx, y: y + h + cBR.dy };
  const BL: Point = { x: x + cBL.dx, y: y + h + cBL.dy };

  const hSeg = opts.segments ?? Math.max(2, Math.round(w / 26));
  const vSeg = opts.segments ?? Math.max(2, Math.round(h / 26));

  const pts: Point[] = [];
  pts.push(TL);
  pts.push(...wavyEdge(TL, TR, hSeg, edgeAmp));
  pts.push(TR);
  pts.push(...wavyEdge(TR, BR, vSeg, edgeAmp));
  pts.push(BR);
  pts.push(...wavyEdge(BR, BL, hSeg, edgeAmp));
  pts.push(BL);
  pts.push(...wavyEdge(BL, TL, vSeg, edgeAmp));
  return pts;
}

/** Trazo SVG (path) a partir de los puntos de una parcela. */
export function parcelPath(pts: Point[]): string {
  if (pts.length === 0) return "";
  const d = pts.map((p) => `${round2(p.x)} ${round2(p.y)}`).join(" L");
  return `M${d} Z`;
}

/* ── Paleta natural por uso del lote ───────────────────────────────────── */

export const USAGE_BASE: Record<string, string> = {
  pastoreo: "#7fae63",
  cultivo: "#c7a44f",
  reserva: "#5d8a5b",
  infraestructura: "#9a9288",
  otro: "#a6a086",
};

export const USAGE_LABEL = (usage: string): string =>
  USAGE_BASE[usage] ? usage.replace(/_/g, " ") : "otro";

/** Color de referencia del terreno: verde por defecto si el uso es desconocido. */
export function usageToHex(usage: string): string {
  return USAGE_BASE[usage] ?? USAGE_BASE.otro;
}

/* ── Color ─────────────────────────────────────────────────────────────── */

type RGB = [number, number, number];

export function hexToRgb(hex: string): RGB {
  const h = hex.replace("#", "");
  const full = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  const n = parseInt(full, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function rgbToHex([r, g, b]: RGB): string {
  const c = (v: number) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0");
  return `#${c(r)}${c(g)}${c(b)}`;
}

/** Mezcla dos colores; t=0 → a, t=1 → b. */
export function mixHex(a: string, b: string, t: number): string {
  const A = hexToRgb(a);
  const B = hexToRgb(b);
  return rgbToHex([
    A[0] + (B[0] - A[0]) * t,
    A[1] + (B[1] - A[1]) * t,
    A[2] + (B[2] - A[2]) * t,
  ]);
}

/** Luz relativa (0 oscuro → 1 claro), para elegir texto legible sobre el terreno. */
export function luminance(hex: string): number {
  const [r, g, b] = hexToRgb(hex);
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255;
}

export function textOnColor(hex: string): string {
  return luminance(hex) > 0.55 ? "#31210f" : "#ffffff";
}

/* Gris con el que se desatura el terreno cuando la cobertura empeora. */
const DRY_GRAY = "#8f9385";

/** Color final del terreno según uso y cobertura (sin variación por estado). */
export function parcelFillColor(usage: string, coverage: string): string {
  const base = usageToHex(usage);
  const t =
    coverage === "malo" ? 0.5
    : coverage === "regular" ? 0.25
    : 0;
  return mixHex(base, DRY_GRAY, t);
}