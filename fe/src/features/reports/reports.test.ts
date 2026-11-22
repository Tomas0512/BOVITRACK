/*
 * features/reports/reports.test.ts
 * ¿Qué?  Contrato de la feature reports: JSON para pantalla, blob para PDF/Excel,
 *        nombre del archivo descargado y API pública.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({ http: { get: vi.fn() } }));

import { http } from "@/core/http";
import { downloadReport, generateReport } from "./api";

const mocked = vi.mocked(http, true);
let clicked: HTMLAnchorElement[] = [];

beforeEach(() => {
  vi.clearAllMocks();
  clicked = [];
  mocked.get.mockResolvedValue({ data: {} });
  window.URL.createObjectURL = vi.fn(() => "blob:fake");
  window.URL.revokeObjectURL = vi.fn();
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (this: HTMLAnchorElement) {
    clicked.push(this);
  });
});
afterEach(() => vi.restoreAllMocks());

describe("features/reports · api", () => {
  it("pide JSON para la pantalla y blob para PDF o Excel", async () => {
    await generateReport("f1", { category: "productivo" });
    await generateReport("f1", { category: "sanitario", export: "pdf" });

    expect(mocked.get.mock.calls).toEqual([
      ["/farms/f1/reports", { params: { category: "productivo" } }],
      ["/farms/f1/reports", { params: { category: "sanitario", export: "pdf" }, responseType: "blob" }],
    ]);
  });

  it("descarga el archivo con la extensión correcta", async () => {
    await downloadReport("f1", "excel", { category: "economico" });
    await downloadReport("f1", "pdf");

    expect(mocked.get.mock.calls[0]).toEqual([
      "/farms/f1/reports",
      { params: { category: "economico", export: "excel" }, responseType: "blob" },
    ]);
    expect(clicked.map((a) => a.download)).toEqual(["reporte_f1.xlsx", "reporte_f1.pdf"]);
  });
});

describe("features/reports · API pública", () => {
  it("solo expone la página de reportes", async () => {
    expect(Object.keys(await import("./index"))).toEqual(["ReportsPage"]);
  });
});
