/*
 * treemapLayout.ts
 * What? Algoritmo "squarified treemap" para repartir rectángulos proporcionales
 *       al valor de cada elemento dentro de un área (ancho x alto).
 * Why?  El mapa de la finca reparte los potreros dentro del área de su lote de
 *       forma que la superficie de cada rectángulo sea proporcional a su área
 *       en hectáreas. Es un esquema representativo, no cartográfico.
 * Impacto? Sin dependencias externas; funciones puras y unit-testables.
 */

export interface TreemapInput {
  key: string;
  value: number;
}

export interface TreemapRect {
  key: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

const sumValues = (items: TreemapInput[]): number =>
  items.reduce((acc, it) => acc + it.value, 0);

/**
 * Peor proporción (aspect ratio) de una fila candidata. El squarified treemap
 * agrega elementos a la fila actual mientras esta proporción no empeore; así se
 * obtienen rectángulos lo más cuadrados posible.
 */
function worstRatio(items: TreemapInput[], side: number): number {
  const total = sumValues(items);
  if (total <= 0 || side <= 0 || items.length === 0) return Number.POSITIVE_INFINITY;
  const values = items.map((it) => it.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const s2 = side * side;
  const t2 = total * total;
  return Math.max((s2 * max) / t2, t2 / (s2 * min));
}

/**
 * Coloca una fila de elementos en la franja. Cuando la franja es más ancha que
 * alta se reparte horizontalmente (usa el ancho); en caso contrario, vertical.
 */
function layoutRow(
  row: TreemapInput[],
  x: number,
  y: number,
  width: number,
  height: number,
  out: TreemapRect[]
): void {
  const total = sumValues(row);
  const horizontal = width >= height;
  let cursor = horizontal ? x : y;
  for (const it of row) {
    const ratio = total > 0 ? it.value / total : 1 / row.length;
    if (horizontal) {
      const itemWidth = width * ratio;
      out.push({ key: it.key, x: cursor, y, width: itemWidth, height });
      cursor += itemWidth;
    } else {
      const itemHeight = height * ratio;
      out.push({ key: it.key, x, y: cursor, width, height: itemHeight });
      cursor += itemHeight;
    }
  }
}

/**
 * Calcula los rectángulos que ocupa cada elemento dentro de [0,0,width,height].
 * La superficie de cada rectángulo es proporcional a su `value`.
 * Devuelve una lista vacía si no hay elementos o las dimensiones no son válidas.
 */
export function squarifiedTreemap(
  items: TreemapInput[],
  width: number,
  height: number
): TreemapRect[] {
  if (items.length === 0 || width <= 0 || height <= 0) return [];

  const raw = [...items].sort((a, b) => b.value - a.value);
  // Valores no positivos: sin áreas reales que repartir, se distribuyen de forma
  // equitativa para que ningún elemento desaparezca del esquema.
  const sorted = sumValues(raw) <= 0 ? raw.map((it) => ({ key: it.key, value: 1 })) : raw;
  const out: TreemapRect[] = [];
  let x = 0;
  let y = 0;
  let w = width;
  let h = height;
  let index = 0;
  let rest = sumValues(sorted);

  while (index < sorted.length && rest > 0) {
    const side = Math.min(w, h);
    const row: TreemapInput[] = [sorted[index]];
    index += 1;
    let rowTotal = row[0].value;

    while (index < sorted.length) {
      const candidate = worstRatio([...row, sorted[index]], side);
      if (candidate > worstRatio(row, side)) break;
      row.push(sorted[index]);
      rowTotal += sorted[index].value;
      index += 1;
    }

    // La franja consume la proporción del área restante igual a su valor.
    if (w >= h) {
      const stripHeight = h * (rowTotal / rest);
      layoutRow(row, x, y, w, stripHeight, out);
      y += stripHeight;
      h -= stripHeight;
    } else {
      const stripWidth = w * (rowTotal / rest);
      layoutRow(row, x, y, stripWidth, h, out);
      x += stripWidth;
      w -= stripWidth;
    }
    rest -= rowTotal;
  }

  return out;
}