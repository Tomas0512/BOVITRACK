import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import NotificationBell from "../../components/layout/NotificationBell";
import {
  getUnreadNotificationCount,
  listNotificationHistory,
  markNotificationRead,
  type NotificationLog,
} from "../../api/alerts";

vi.mock("../../api/alerts", () => ({
  getUnreadNotificationCount: vi.fn(),
  listNotificationHistory: vi.fn(),
  markNotificationRead: vi.fn(),
}));

vi.mock("../../context/FarmContext", () => ({
  useFarm: () => ({ activeFarmId: "farm-123" }),
}));

const mockedGetCount = vi.mocked(getUnreadNotificationCount);
const mockedListHistory = vi.mocked(listNotificationHistory);
const mockedMarkRead = vi.mocked(markNotificationRead);

function buildLog(partial: Partial<NotificationLog> = {}): NotificationLog {
  return {
    id: "n1",
    farm_id: "farm-123",
    user_id: "user-1",
    type: "sanitary",
    title: "Plan sanitario vencido: Aftosa",
    message: "Aftosa para Bovino #123 venció el 2026-09-10.",
    channel: "email",
    status: "sent",
    reference_id: null,
    sent_at: "2026-09-10T12:00:00",
    read_at: null,
    created_at: "2026-09-10T12:00:00",
    ...partial,
  };
}

function renderBell() {
  return render(
    <MemoryRouter>
      <NotificationBell />
    </MemoryRouter>,
  );
}

describe("NotificationBell", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedGetCount.mockResolvedValue({ farm_id: "farm-123", unread_count: 0 });
  });

  it("muestra el badge con el conteo de no leídas", async () => {
    mockedGetCount.mockResolvedValue({ farm_id: "farm-123", unread_count: 3 });

    renderBell();

    expect(await screen.findByText("3")).toBeInTheDocument();
  });

  it("no muestra badge cuando el conteo es 0", async () => {
    mockedGetCount.mockResolvedValue({ farm_id: "farm-123", unread_count: 0 });

    renderBell();

    await waitFor(() => expect(getUnreadNotificationCount).toHaveBeenCalled());
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("abre el panel con las notificaciones sin leer", async () => {
    mockedGetCount.mockResolvedValue({ farm_id: "farm-123", unread_count: 1 });
    mockedListHistory.mockResolvedValue({
      items: [buildLog()],
      total: 1,
      limit: 5,
      offset: 0,
    });

    renderBell();

    fireEvent.click(screen.getByRole("button", { name: "Notificaciones" }));

    expect(
      await screen.findByText("Plan sanitario vencido: Aftosa"),
    ).toBeInTheDocument();
    expect(screen.getByText("Ver todas")).toBeInTheDocument();
  });

  it("muestra estado vacío cuando no hay notificaciones sin leer", async () => {
    mockedListHistory.mockResolvedValue({ items: [], total: 0, limit: 5, offset: 0 });

    renderBell();

    fireEvent.click(screen.getByRole("button", { name: "Notificaciones" }));

    expect(
      await screen.findByText("No tienes notificaciones sin leer"),
    ).toBeInTheDocument();
  });

  it("marca como leída y decrementa el badge", async () => {
    mockedGetCount.mockResolvedValue({ farm_id: "farm-123", unread_count: 2 });
    mockedListHistory.mockResolvedValue({
      items: [buildLog()],
      total: 1,
      limit: 5,
      offset: 0,
    });
    mockedMarkRead.mockResolvedValue(undefined);

    renderBell();

    await screen.findByText("2");
    fireEvent.click(screen.getByRole("button", { name: "Notificaciones" }));
    fireEvent.click(await screen.findByRole("button", { name: "Marcar como leída" }));

    await waitFor(() => expect(markNotificationRead).toHaveBeenCalledWith("farm-123", "n1"));
    await waitFor(() =>
      expect(
        screen.queryByText("Plan sanitario vencido: Aftosa"),
      ).not.toBeInTheDocument(),
    );
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  it("cierra el panel al pulsar Escape", async () => {
    mockedListHistory.mockResolvedValue({ items: [], total: 0, limit: 5, offset: 0 });

    renderBell();

    fireEvent.click(screen.getByRole("button", { name: "Notificaciones" }));
    expect(
      await screen.findByText("No tienes notificaciones sin leer"),
    ).toBeInTheDocument();

    fireEvent.keyDown(document, { key: "Escape" });

    await waitFor(() =>
      expect(
        screen.queryByText("No tienes notificaciones sin leer"),
      ).not.toBeInTheDocument(),
    );
  });
});