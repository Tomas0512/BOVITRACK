/*
 * features/reproduction/reproduction.test.tsx
 * ¿Qué?  Pruebas de la línea de tiempo reproductiva y de la API pública de la feature.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("@/core/http", () => ({ http: { get: vi.fn(), post: vi.fn(), delete: vi.fn() } }));

import { http } from "@/core/http";
import ReproductiveTimeline from "./components/ReproductiveTimeline";
import { listReproductiveEvents } from "./api";

const mocked = vi.mocked(http, true);
beforeEach(() => vi.clearAllMocks());

describe("features/reproduction · ReproductiveTimeline", () => {
  it("pide los eventos del bovino y muestra el estado vacío", async () => {
    mocked.get.mockResolvedValue({ data: [] });
    render(<ReproductiveTimeline farmId="f1" bovineId="b1" />);

    expect(await screen.findByText("Sin eventos reproductivos registrados.")).toBeInTheDocument();
    expect(mocked.get).toHaveBeenCalledWith("/farms/f1/reproductive-events", { params: { bovine_id: "b1" } });
  });

  it("muestra el error si la carga falla", async () => {
    mocked.get.mockRejectedValue(new Error("sin red"));
    render(<ReproductiveTimeline farmId="f1" bovineId="b1" />);

    expect(await screen.findByText("No se pudieron cargar los eventos reproductivos.")).toBeInTheDocument();
  });

  it("sin bovino, lista los eventos de toda la finca", async () => {
    mocked.get.mockResolvedValue({ data: [] });
    await listReproductiveEvents("f1");
    expect(mocked.get).toHaveBeenCalledWith("/farms/f1/reproductive-events", { params: {} });
  });
});

describe("features/reproduction · API pública", () => {
  it("expone la línea de tiempo y la lista de eventos", async () => {
    expect(Object.keys(await import("./index")).sort()).toEqual(["ReproductiveTimeline", "listReproductiveEvents"]);
  });
});
