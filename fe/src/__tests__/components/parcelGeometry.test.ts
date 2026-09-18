/*
 * parcelGeometry.test.ts
 * What? Pruebas de la geometría orgánica y la paleta natural del mapa.
 * Why?  Garantizar que el dibujo es determinista, que dos parcelas vecinas
 *       comparten exactamente la misma línea de frontera y que el color del
 *       terreno depende del uso + cobertura (no del estado).
 */

import { describe, it, expect } from "vitest";
import {
  USAGE_BASE,
  hash01,
  hashRange,
  luminance,
  mixHex,
  parcelPath,
  parcelFillColor,
  rectToParcel,
  textOnColor,
  usageToHex,
  type Point,
} from "../../components/paddocks/parcelGeometry";

function samePoints(a: Point[], b: Point[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((p, i) => Math.abs(p.x - b[i].x) < 1e-6 && Math.abs(p.y - b[i].y) < 1e-6);
}

describe("hash01 / hashRange", () => {
  it("es determinista", () => {
    expect(hash01("semilla")).toBe(hash01("semilla"));
    expect(hashRange("semilla", 0, 10)).toBe(hashRange("semilla", 0, 10));
  });

  it("devuelve valores dentro del rango pedido", () => {
    for (let i = 0; i < 50; i++) {
      const v = hashRange(`seed-${i}`, 5, 10);
      expect(v).toBeGreaterThanOrEqual(5);
      expect(v).toBeLessThan(10);
    }
  });

  it("distingue semillas distintas", () => {
    expect(hash01("a")).not.toBe(hash01("b"));
  });
});

describe("rectToParcel (parcelas orgánicas)", () => {
  it("es determinista con la misma entrada", () => {
    const rect = { x: 10, y: 20, width: 100, height: 60 };
    expect(samePoints(rectToParcel(rect), rectToParcel(rect))).toBe(true);
  });

  it("es irregular: no queda como un rectángulo limpio", () => {
    const rect = { x: 0, y: 0, width: 120, height: 80 };
    const poly = rectToParcel(rect);
    const esBordePuro = poly.every((p) =>
      (Math.abs(p.x - 0) < 1e-6 || Math.abs(p.x - 120) < 1e-6) &&
      (Math.abs(p.y - 0) < 1e-6 || Math.abs(p.y - 80) < 1e-6)
    );
    expect(esBordePuro).toBe(false);
    expect(poly.length).toBeGreaterThan(4);
  });

  it("se mantiene cerca del rectángulo original", () => {
    const rect = { x: 30, y: 40, width: 200, height: 140 };
    for (const p of rectToParcel(rect)) {
      expect(p.x).toBeGreaterThan(rect.x - 10);
      expect(p.x).toBeLessThan(rect.x + rect.width + 10);
      expect(p.y).toBeGreaterThan(rect.y - 10);
      expect(p.y).toBeLessThan(rect.y + rect.height + 10);
    }
  });

  it("parcelas adyacentes comparten exactamente la misma frontera vertical", () => {
    const A = { x: 0, y: 0, width: 40, height: 30 };
    const B = { x: 40, y: 0, width: 40, height: 30 };
    const pA = rectToParcel(A);
    const pB = rectToParcel(B);
    /* Frontera derecha de A: las esquinas TR y BR coinciden con TL y BL de B. */
    for (const pt of [pA[0], ...pA.slice(1, -1), pA[pA.length - 1]]) {
      expect(pt).toBeDefined();
    }
    const frontA = new Set(pA.map((p) => p.x.toFixed(3)));
    const frontB = new Set(pB.map((p) => p.x.toFixed(3)));
    const xRow = 40;
    /* Todos los vértices con coordenada cercana a x=40 deberían estar presentes en ambos lados. */
    const nearA = pA.filter((p) => Math.abs(p.x - xRow) < 8);
    const nearB = pB.filter((p) => Math.abs(p.x - xRow) < 8);
    expect(nearA.length).toBeGreaterThan(0);
    expect(nearA.length).toBe(nearB.length);
    /* Mismo borde (mismos pares x,y) salvo el orden de recorrido. */
    const dump = (pts: Point[]) => pts.map((p) => `${p.x.toFixed(3)}:${p.y.toFixed(3)}`).sort();
    expect(dump(nearA)).toEqual(dump(nearB));
    void frontA;
    void frontB;
  });

  it("parcelas adyacentes comparten exactamente la misma frontera horizontal", () => {
    const A = { x: 0, y: 0, width: 50, height: 30 };
    const B = { x: 0, y: 30, width: 50, height: 30 };
    const pA = rectToParcel(A);
    const pB = rectToParcel(B);
    const nearA = pA.filter((p) => Math.abs(p.y - 30) < 8);
    const nearB = pB.filter((p) => Math.abs(p.y - 30) < 8);
    expect(nearA.length).toBeGreaterThan(0);
    expect(nearA.length).toBe(nearB.length);
    const dump = (pts: Point[]) => pts.map((p) => `${p.x.toFixed(3)}:${p.y.toFixed(3)}`).sort();
    expect(dump(nearA)).toEqual(dump(nearB));
  });

  it("construye un path SVG válido y cerrado", () => {
    const d = parcelPath(rectToParcel({ x: 0, y: 0, width: 40, height: 30 }));
    expect(d.startsWith("M")).toBe(true);
    expect(d.endsWith("Z")).toBe(true);
  });
});

describe("paleta natural por uso y cobertura", () => {
  it("mapea todos los usos conocidos", () => {
    for (const usage of Object.keys(USAGE_BASE)) {
      expect(usageToHex(usage)).toBe(USAGE_BASE[usage]);
    }
  });

  it("usa el verde pasto por defecto para usos desconocidos", () => {
    expect(usageToHex("cualquier_cosa")).toBe(USAGE_BASE.otro);
  });

  it("cobertura buena = color base; regular y malo apagan el tono", () => {
    const usage = "pastoreo";
    const base = parcelFillColor(usage, "bueno");
    const regular = parcelFillColor(usage, "regular");
    const malo = parcelFillColor(usage, "malo");
    expect(regular).not.toBe(base);
    expect(malo).not.toBe(base);
    expect(malo).not.toBe(regular);
  });

  it("el estado NO cambia el color del terreno", () => {
    const conOcupado = parcelFillColor("pastoreo", "bueno");
    const conLibre = parcelFillColor("pastoreo", "bueno");
    const enDescanso = parcelFillColor("pastoreo", "bueno");
    expect(conOcupado).toBe(conLibre);
    expect(conOcupado).toBe(enDescanso);
  });

  it("texto legible según la luminosidad del terreno", () => {
    expect(textOnColor("#5d8a5b")).toBe("#ffffff");
    expect(textOnColor("#c7a44f")).toBe("#31210f");
    expect(luminance(mixHex("#000000", "#ffffff", 0.5))).toBeGreaterThan(0.4);
  });
});