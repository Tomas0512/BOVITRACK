/*
 * features/inventory/inventory.test.ts
 * ¿Qué?  Contrato de la feature inventory: rutas del backend y API pública.
 * ¿Para? La ficha del hato (herd) consume listConsumptions: si cambia, esto avisa.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({ http: { get: vi.fn() } }));

import { http } from "@/core/http";
import { listConsumptions } from "./api";

const mocked = vi.mocked(http, true);
beforeEach(() => {
  vi.clearAllMocks();
  mocked.get.mockResolvedValue({ data: [] });
});

describe("features/inventory", () => {
  it("lista los consumos de la finca con sus filtros", async () => {
    await listConsumptions("f1", { bovine_id: "b1" });
    const [url, config] = mocked.get.mock.calls[0];
    expect(url).toMatch(/^\/farms\/f1\/.*consumptions$/);
    expect(config).toEqual({ params: { bovine_id: "b1" } });
  });

  it("su API pública expone sus pantallas y listConsumptions", async () => {
    expect(Object.keys(await import("./index")).sort()).toEqual(["BovineFoodList", "FoodList", "listConsumptions"]);
  });
});
