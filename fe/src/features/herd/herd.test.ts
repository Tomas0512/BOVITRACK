/*
 * features/herd/herd.test.ts
 * ¿Qué?  Pruebas de los cálculos de la ficha del hato y de la API pública de la feature.
 * ¿Para? La edad y su formato aparecen en columnas y filtros de TODO el hato.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { calcAgeMonths, formatAge } from "./components/bovineColumns";

describe("features/herd · edad del animal", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-11-22T12:00:00"));
  });
  afterEach(() => vi.useRealTimers());

  it("cuenta meses cumplidos (no redondea hacia arriba)", () => {
    expect(calcAgeMonths("2026-10-22")).toBe(1);
    expect(calcAgeMonths("2026-10-23")).toBe(0); // aún no cumple el mes
    expect(calcAgeMonths("2024-05-01")).toBe(30);
    expect(calcAgeMonths(null)).toBeNull();
    expect(calcAgeMonths("no-es-fecha")).toBeNull();
    expect(calcAgeMonths("2027-01-01")).toBe(0); // fecha futura: nunca negativo
  });

  it("formatea la edad para la tabla", () => {
    expect(formatAge(1)).toBe("1 mes");
    expect(formatAge(5)).toBe("5 meses");
    expect(formatAge(12)).toBe("1 año");
    expect(formatAge(24)).toBe("2 años");
    expect(formatAge(30)).toBe("2a 6m");
    expect(formatAge(null)).toBe("—");
  });
});

describe("features/herd · API pública", () => {
  it("solo expone la ficha del hato", async () => {
    expect(Object.keys(await import("./index"))).toEqual(["BovineList"]);
  });
});
