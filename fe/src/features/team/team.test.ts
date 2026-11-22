/*
 * features/team/team.test.ts
 * ¿Qué?  Pruebas del cliente HTTP del equipo de la finca y de la API pública de la feature.
 * ¿Para? Que empleados, invitaciones y reactivación llamen a las rutas del módulo
 *        team del backend (incluidas las públicas bajo /auth).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({
  http: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
}));

import { http } from "@/core/http";
import {
  getInvitationInfo,
  inviteEmployee,
  listEmployees,
  registerInvited,
  removeEmployee,
  requestReactivation,
  setAccountStatus,
} from "./api";

const mocked = vi.mocked(http, true);
beforeEach(() => vi.clearAllMocks());

describe("features/team · api", () => {
  it("gestiona empleados de una finca", async () => {
    mocked.get.mockResolvedValue({ data: [] });
    mocked.post.mockResolvedValue({ data: {} });
    mocked.put.mockResolvedValue({ data: {} });
    mocked.delete.mockResolvedValue({});

    await listEmployees("f1", true);
    await inviteEmployee("f1", { email: "p@x.com", role_id: "r1" });
    await setAccountStatus("f1", "u1", { is_active: false, reason: "renunció" });
    await removeEmployee("f1", "u1");

    expect(mocked.get).toHaveBeenCalledWith("/farms/f1/employees", { params: { is_active: true } });
    expect(mocked.post).toHaveBeenCalledWith("/farms/f1/employees/invite", { email: "p@x.com", role_id: "r1" });
    expect(mocked.put).toHaveBeenCalledWith("/farms/f1/employees/u1/account", { is_active: false, reason: "renunció" });
    expect(mocked.delete).toHaveBeenCalledWith("/farms/f1/employees/u1");
  });

  it("usa las rutas públicas de invitación y reactivación", async () => {
    mocked.get.mockResolvedValue({ data: {} });
    mocked.post.mockResolvedValue({ data: {} });

    await getInvitationInfo("tok");
    await registerInvited({ token: "tok" } as Parameters<typeof registerInvited>[0]);
    await requestReactivation({ email: "p@x.com", reason: "volví" });

    expect(mocked.get).toHaveBeenCalledWith("/auth/invitation/tok");
    expect(mocked.post.mock.calls.map((c) => c[0])).toEqual(["/auth/register-invited", "/auth/request-reactivation"]);
  });
});

describe("features/team · API pública", () => {
  it("expone la lista de empleados, las dos pantallas públicas y la moderación", async () => {
    const publicApi = await import("./index");

    expect(Object.keys(publicApi).sort()).toEqual(["EmployeeList", "InvitedRegisterPage", "ReactivationRequestsPage", "RequestReactivationPage"]);
  });
});
