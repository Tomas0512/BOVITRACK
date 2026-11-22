/*
 * features/notifications/notifications.test.ts
 * ¿Qué?  Contrato de la feature notifications (HU014): rutas de alertas, historial,
 *        no leídas y marcar como leída, y API pública. El comportamiento de la
 *        campana se prueba en components/NotificationBell.test.tsx.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({ http: { get: vi.fn(), put: vi.fn() } }));

import { http } from "@/core/http";
import { getUnreadNotificationCount, listAlerts, listNotificationHistory, markNotificationRead } from "./api";

const mocked = vi.mocked(http, true);
beforeEach(() => {
  vi.clearAllMocks();
  mocked.get.mockResolvedValue({ data: {} });
  mocked.put.mockResolvedValue({});
});

describe("features/notifications · api", () => {
  it("usa las rutas del módulo notifications del backend", async () => {
    await listAlerts("f1");
    await listNotificationHistory("f1", { unread_only: true, limit: 5 });
    await getUnreadNotificationCount("f1");
    await markNotificationRead("f1", "n1");

    expect(mocked.get.mock.calls).toEqual([
      ["/farms/f1/alerts", { params: { days: 7 } }], // por defecto, la próxima semana
      ["/farms/f1/alerts/history", { params: { unread_only: true, limit: 5 } }],
      ["/farms/f1/alerts/history/unread-count"],
    ]);
    expect(mocked.put).toHaveBeenCalledWith("/farms/f1/alerts/history/n1/read");
  });
});

describe("features/notifications · API pública", () => {
  it("expone la campana del encabezado y la página de alertas", async () => {
    expect(Object.keys(await import("./index")).sort()).toEqual(["AlertasPage", "NotificationBell"]);
  });
});
