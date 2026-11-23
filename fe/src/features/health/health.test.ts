/*
 * features/health/health.test.ts
 * ¿Qué?  Contrato de la feature health: rutas del backend y API pública.
 * ¿Para? La ficha del hato (herd) consume listTreatments: si cambia, esto avisa.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({ http: { get: vi.fn() } }));

import { http } from "@/core/http";
import { listTreatments } from "./api/treatments";

const mocked = vi.mocked(http, true);
beforeEach(() => {
  vi.clearAllMocks();
  mocked.get.mockResolvedValue({ data: [] });
});

describe("features/health", () => {
  it("lista tratamientos de la finca o de un bovino", async () => {
    await listTreatments("f1");
    await listTreatments("f1", "b1");
    expect(mocked.get.mock.calls).toEqual([
      ["/farms/f1/treatments", { params: {} }],
      ["/farms/f1/treatments", { params: { bovine_id: "b1" } }],
    ]);
  });

  it("su API pública expone sus pantallas y listTreatments", async () => {
    expect(Object.keys(await import("./index")).sort()).toEqual(["FarmTreatments", "SanitaryPlanList", "TreatmentList", "listTreatments"]);
  });
});
