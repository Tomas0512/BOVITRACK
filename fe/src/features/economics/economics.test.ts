/*
 * features/economics/economics.test.ts
 * ¿Qué?  Contrato de la feature economics (HU010): rutas del backend y API pública.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({ http: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() } }));

import { http } from "@/core/http";
import { createRecord, deleteRecord, getIndicators, listRecords, updateRecord } from "./api";

const mocked = vi.mocked(http, true);
beforeEach(() => {
  vi.clearAllMocks();
  for (const fn of [mocked.get, mocked.post, mocked.put, mocked.delete]) fn.mockResolvedValue({ data: {} });
});

describe("features/economics · api", () => {
  it("usa las rutas del módulo economics del backend", async () => {
    const record = { record_type: "ingreso" } as Parameters<typeof createRecord>[1];

    await listRecords("f1", { record_type: "gasto" });
    await getIndicators("f1", { date_from: "2026-01-01", date_to: "2026-01-31" });
    await createRecord("f1", record);
    await updateRecord("f1", "r1", { amount: 10 } as Parameters<typeof updateRecord>[2]);
    await deleteRecord("f1", "r1");

    expect(mocked.get.mock.calls).toEqual([
      ["/farms/f1/economics", { params: { record_type: "gasto" } }],
      ["/farms/f1/economics/indicators", { params: { date_from: "2026-01-01", date_to: "2026-01-31" } }],
    ]);
    expect(mocked.post).toHaveBeenCalledWith("/farms/f1/economics", record);
    expect(mocked.put).toHaveBeenCalledWith("/farms/f1/economics/r1", { amount: 10 });
    expect(mocked.delete).toHaveBeenCalledWith("/farms/f1/economics/r1");
  });
});

describe("features/economics · API pública", () => {
  it("solo expone el tablero económico", async () => {
    expect(Object.keys(await import("./index"))).toEqual(["EconomicDashboard"]);
  });
});
