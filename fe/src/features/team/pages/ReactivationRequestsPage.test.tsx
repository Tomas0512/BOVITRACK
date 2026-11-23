/*
 * features/team/pages/ReactivationRequestsPage.test.tsx
 * ¿Qué?  Pruebas de la pantalla de moderación de reactivaciones.
 * ¿Para? Que el administrador vea las solicitudes pendientes, pueda aprobarlas o
 *        rechazarlas (con confirmación) y entienda cuándo no tiene permiso.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";

vi.mock("../api", () => ({
  listReactivationRequests: vi.fn(),
  approveReactivation: vi.fn(),
  rejectReactivation: vi.fn(),
}));

import { approveReactivation, listReactivationRequests, rejectReactivation } from "../api";
import { ReactivationRequestsPage } from "./ReactivationRequestsPage";

const rosa = {
  id: "r1", user_id: "u1", reason: "Volví a la finca", status: "pending",
  created_at: "2026-11-20T10:00:00Z", reviewed_at: null, user_email: "rosa@x.com", user_name: "Rosa Ruiz",
};
const pedro = { ...rosa, id: "r2", user_id: "u2", reason: null, user_email: "pedro@x.com", user_name: "Pedro Mora" };

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(listReactivationRequests).mockResolvedValue([rosa, pedro]);
});

describe("ReactivationRequestsPage", () => {
  it("lista las solicitudes pendientes con su motivo", async () => {
    render(<ReactivationRequestsPage />);

    expect(await screen.findByText("Rosa Ruiz")).toBeInTheDocument();
    expect(screen.getByText("rosa@x.com")).toBeInTheDocument();
    expect(screen.getByText("Volví a la finca")).toBeInTheDocument();
    expect(screen.getByText("Sin motivo")).toBeInTheDocument(); // Pedro no escribió motivo
    expect(screen.getByText("2 solicitud(es)")).toBeInTheDocument();
  });

  it("aprueba con confirmación y quita la solicitud de la lista", async () => {
    vi.mocked(approveReactivation).mockResolvedValue({ ...rosa, status: "approved" });
    render(<ReactivationRequestsPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Aprobar a Rosa Ruiz" }));
    expect(approveReactivation).not.toHaveBeenCalled(); // primero confirma
    expect(screen.getByText("Rosa Ruiz podrá volver a iniciar sesión.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Aprobar" }));

    await waitFor(() => expect(approveReactivation).toHaveBeenCalledWith("r1"));
    expect(await screen.findByRole("status")).toHaveTextContent("Cuenta de Rosa Ruiz reactivada");
    expect(screen.queryByText("rosa@x.com")).not.toBeInTheDocument();
    expect(screen.getByText("1 solicitud(es)")).toBeInTheDocument();
  });

  it("rechaza, y cancelar no hace nada", async () => {
    vi.mocked(rejectReactivation).mockResolvedValue({ ...pedro, status: "rejected" });
    render(<ReactivationRequestsPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Rechazar a Pedro Mora" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(rejectReactivation).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Rechazar a Pedro Mora" }));
    fireEvent.click(screen.getByRole("button", { name: "Rechazar" }));
    await waitFor(() => expect(rejectReactivation).toHaveBeenCalledWith("r2"));
    expect(await screen.findByRole("status")).toHaveTextContent("la cuenta sigue desactivada");
  });

  it("muestra el motivo del backend si falla (p. ej. sin permiso) y el estado vacío", async () => {
    vi.mocked(listReactivationRequests).mockRejectedValueOnce(
      new Error("Solo un administrador puede gestionar solicitudes de reactivación"),
    );
    const { unmount } = render(<ReactivationRequestsPage />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Solo un administrador puede gestionar");
    unmount();

    vi.mocked(listReactivationRequests).mockResolvedValueOnce([]);
    render(<ReactivationRequestsPage />);
    expect(await screen.findByText("No hay solicitudes pendientes de personas de tus fincas.")).toBeInTheDocument();
  });

  it("si aprobar falla, la solicitud sigue en la lista con el error a la vista", async () => {
    vi.mocked(approveReactivation).mockRejectedValue(new Error("Solicitud no encontrada o ya procesada"));
    render(<ReactivationRequestsPage />);

    fireEvent.click(await screen.findByRole("button", { name: "Aprobar a Rosa Ruiz" }));
    fireEvent.click(screen.getByRole("button", { name: "Aprobar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Solicitud no encontrada o ya procesada");
    expect(within(screen.getByRole("table")).getByText("Rosa Ruiz")).toBeInTheDocument();
  });
});
