/*
 * features/audit/audit.test.ts
 * ¿Qué?  Contrato de la feature audit (HU015): rutas del backend, descarga de la
 *        auditoría como archivo y API pública.
 * ¿Para? Si la exportación no pide un blob, el Excel llega corrupto; si cambia una
 *        ruta, la auditoría global queda vacía sin error visible.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({ http: { get: vi.fn() } }));

import { http } from "@/core/http";
import { downloadAuditLogs, getAuditCatalog, listAuditLogs, searchAuditLogs } from "./api";

const mocked = vi.mocked(http, true);
let clicked: HTMLAnchorElement[] = [];

beforeEach(() => {
  vi.clearAllMocks();
  clicked = [];
  mocked.get.mockResolvedValue({ data: [] });
  window.URL.createObjectURL = vi.fn(() => "blob:fake");
  window.URL.revokeObjectURL = vi.fn();
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(function (this: HTMLAnchorElement) {
    clicked.push(this);
  });
});
afterEach(() => vi.restoreAllMocks());

describe("features/audit · api", () => {
  it("usa las rutas de auditoría por finca y del sistema", async () => {
    await listAuditLogs("f1");
    await searchAuditLogs({ action: "create", limit: 50 } as Parameters<typeof searchAuditLogs>[0]);
    await getAuditCatalog();

    expect(mocked.get.mock.calls).toEqual([
      ["/farms/f1/audit-logs"],
      ["/admin/audit-logs", { params: { action: "create", limit: 50 } }],
      ["/admin/audit-logs/actions"],
    ]);
  });

  it("descarga la auditoría filtrada como archivo (blob) con fecha en el nombre", async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-11-22T10:00:00Z"));
    await downloadAuditLogs("excel", { action: "delete" } as Parameters<typeof downloadAuditLogs>[1]);
    vi.useRealTimers();

    expect(mocked.get).toHaveBeenCalledWith("/admin/audit-logs/export", {
      params: { action: "delete", export: "excel" },
      responseType: "blob",
    });
    expect(clicked.map((a) => a.download)).toEqual(["auditoria_2026-11-22.xlsx"]);
    expect(window.URL.revokeObjectURL).toHaveBeenCalledWith("blob:fake"); // no deja memoria retenida
  });
});

describe("features/audit · API pública", () => {
  it("expone la auditoría global y la pestaña de la finca", async () => {
    expect(Object.keys(await import("./index")).sort()).toEqual(["AuditLogList", "AuditPage"]);
  });
});
