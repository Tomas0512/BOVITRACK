/*
 * treemapLayout.test.ts
 * What? Pruebas del algoritmo squarified treemap.
 * Why?  Verificar que los rectángulos sean proporcionales al valor, no se
 *       solapen y llenen por completo el área disponible.
 */

import { describe, it, expect } from "vitest";
import { squarifiedTreemap } from "../../components/paddocks/treemapLayout";

describe("squarifiedTreemap", () => {
  it("devuelve lista vacía cuando no hay elementos", () => {
    expect(squarifiedTreemap([], 100, 100)).toEqual([]);
  });

  it("devuelve lista vacía con dimensiones inválidas", () => {
    const items = [{ key: "a", value: 1 }];
    expect(squarifiedTreemap(items, 0, 100)).toEqual([]);
    expect(squarifiedTreemap(items, 100, -5)).toEqual([]);
  });

  it("un solo elemento ocupa toda el área", () => {
    const rects = squarifiedTreemap([{ key: "a", value: 5 }], 400, 300);
    expect(rects).toHaveLength(1);
    expect(rects[0]).toMatchObject({ key: "a", x: 0, y: 0, width: 400, height: 300 });
  });

  it("reparte las áreas proporcionalmente al valor", () => {
    // Dos potreros con 1 y 3 hectáreas: el segundo debe ocupar 3x la superficie del primero.
    const rects = squarifiedTreemap(
      [
        { key: "a", value: 1 },
        { key: "b", value: 3 },
      ],
      400,
      300
    );
    const area = (r: { width: number; height: number }) => r.width * r.height;
    const a = rects.find((r) => r.key === "a")!;
    const b = rects.find((r) => r.key === "b")!;
    expect(area(b) / area(a)).toBeCloseTo(3, 4);
  });

  it("los rectángulos no se solapan y cubren el área total", () => {
    const items = [
      { key: "a", value: 2 },
      { key: "b", value: 5 },
      { key: "c", value: 1 },
      { key: "d", value: 4 },
    ];
    const width = 500;
    const height = 320;
    const rects = squarifiedTreemap(items, width, height);

    // Cada rectángulo dentro de los límites.
    for (const r of rects) {
      expect(r.x).toBeGreaterThanOrEqual(0);
      expect(r.y).toBeGreaterThanOrEqual(0);
      expect(r.x + r.width).toBeLessThanOrEqual(width + 1e-6);
      expect(r.y + r.height).toBeLessThanOrEqual(height + 1e-6);
    }

    // Sin solapamientos: los intervalos solo pueden tocarse en los bordes.
    for (let i = 0; i < rects.length; i++) {
      for (let j = i + 1; j < rects.length; j++) {
        const a = rects[i];
        const b = rects[j];
        const overlapX = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
        const overlapY = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
        expect(overlapX * overlapY).toBeLessThan(1e-6);
      }
    }

    // La suma de superficies es (aprox.) el área total del lienzo.
    const totalArea = rects.reduce((acc, r) => acc + r.width * r.height, 0);
    expect(totalArea).toBeCloseTo(width * height, 4);
  });

  it("funciona con valores cero manteniendo al menos una partición", () => {
    const rects = squarifiedTreemap(
      [
        { key: "a", value: 0 },
        { key: "b", value: 0 },
      ],
      200,
      100
    );
    expect(rects).toHaveLength(2);
    const totalArea = rects.reduce((acc, r) => acc + r.width * r.height, 0);
    expect(totalArea).toBeCloseTo(20000, 4);
  });
});