/*
 * features/milk_production/milk_production.test.ts
 * ¿Qué?  Contrato de la feature milk_production: rutas del backend y API pública.
 * ¿Para? La ficha del hato (herd) y el dashboard consumen listMilkProduction.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({ http: { get: vi.fn() } }));

import { http } from "@/core/http";
import { listMilkProduction } from "./api";

const mocked = vi.mocked(http, true);
beforeEach(() => {
  vi.clearAllMocks();
  mocked.get.mockResolvedValue({ data: [] });
});

describe("features/milk_production", () => {
  it("lista los ordeños de la finca", async () => {
    await listMilkProduction("f1");
    expect(mocked.get).toHaveBeenCalledWith("/farms/f1/milk-production", { params: {} });
  });

  it("su API pública expone sus pantallas y listMilkProduction", async () => {
    expect(Object.keys(await import("./index")).sort()).toEqual(["MilkProductionDashboard", "MilkProductionList", "listMilkProduction"]);
  });
});
