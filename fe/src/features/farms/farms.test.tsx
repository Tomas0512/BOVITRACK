/*
 * features/farms/farms.test.tsx
 * ¿Qué?  Pruebas de la finca activa (FarmContext), del cliente HTTP de fincas y de
 *        la API pública de la feature.
 * ¿Para? La finca activa decide qué datos ve TODA la app (menú, alertas, páginas):
 *        si se elige mal, el usuario trabaja sobre la finca equivocada.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";

vi.mock("@/core/http", () => ({
  http: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
}));

import { http } from "@/core/http";
import { createFarm, deleteFarm, listCities, updateFarm } from "./api/farms";
import { FarmProvider } from "./context/FarmContext";
import { useFarm } from "./context/useFarm";

const mocked = vi.mocked(http, true);
const farm = (id: string, name: string) => ({ id, name, total_area: 10, area_unit: "hectareas", farm_identifier: id });

function Probe() {
  const { activeFarmId, activeFarm, farms, loading, setActiveFarmId } = useFarm();
  if (loading) return <p>cargando</p>;
  return (
    <div>
      <p>activa: {activeFarm?.name ?? "ninguna"} ({activeFarmId ?? "-"})</p>
      <p>total: {farms.length}</p>
      <button onClick={() => setActiveFarmId("f2")}>elegir f2</button>
    </div>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});
afterEach(() => localStorage.clear());

describe("features/farms · finca activa", () => {
  it("sin preferencia guardada, la activa es la primera finca", async () => {
    mocked.get.mockResolvedValue({ data: [farm("f1", "La Esperanza"), farm("f2", "El Retiro")] });
    render(<FarmProvider><Probe /></FarmProvider>);

    expect(await screen.findByText("activa: La Esperanza (f1)")).toBeInTheDocument();
    expect(mocked.get).toHaveBeenCalledWith("/farms");
  });

  it("recuerda la finca elegida entre visitas", async () => {
    mocked.get.mockResolvedValue({ data: [farm("f1", "La Esperanza"), farm("f2", "El Retiro")] });
    const { unmount } = render(<FarmProvider><Probe /></FarmProvider>);

    await screen.findByText("activa: La Esperanza (f1)");
    act(() => screen.getByRole("button", { name: "elegir f2" }).click());
    expect(screen.getByText("activa: El Retiro (f2)")).toBeInTheDocument();
    expect(localStorage.getItem("active_farm_id")).toBe("f2");
    unmount();

    render(<FarmProvider><Probe /></FarmProvider>);
    expect(await screen.findByText("activa: El Retiro (f2)")).toBeInTheDocument();
  });

  it("si la finca guardada ya no existe (p. ej. se desactivó), vuelve a la primera", async () => {
    localStorage.setItem("active_farm_id", "f-borrada");
    mocked.get.mockResolvedValue({ data: [farm("f1", "La Esperanza")] });
    render(<FarmProvider><Probe /></FarmProvider>);

    expect(await screen.findByText("activa: La Esperanza (f1)")).toBeInTheDocument();
  });

  it("si falla la carga, no hay finca activa (y no se rompe la app)", async () => {
    mocked.get.mockRejectedValue(new Error("sin red"));
    render(<FarmProvider><Probe /></FarmProvider>);

    await waitFor(() => expect(screen.getByText("activa: ninguna (-)")).toBeInTheDocument());
    expect(screen.getByText("total: 0")).toBeInTheDocument();
  });

  it("useFarm fuera del proveedor avisa con un error claro", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<Probe />)).toThrow("useFarm must be used within a FarmProvider");
    spy.mockRestore();
  });
});

describe("features/farms · api", () => {
  it("usa las rutas del módulo farms del backend", async () => {
    mocked.get.mockResolvedValue({ data: [] });
    mocked.post.mockResolvedValue({ data: {} });
    mocked.put.mockResolvedValue({ data: {} });
    mocked.delete.mockResolvedValue({});
    const data = { name: "La Esperanza" } as Parameters<typeof createFarm>[0];

    await createFarm(data);
    await listCities("d1");
    await updateFarm("f1", data);
    await deleteFarm("f1");

    expect(mocked.post).toHaveBeenCalledWith("/farms", data);
    expect(mocked.get).toHaveBeenCalledWith("/farms/departments/d1/cities");
    expect(mocked.put).toHaveBeenCalledWith("/farms/f1", data);
    expect(mocked.delete).toHaveBeenCalledWith("/farms/f1");
  });
});

describe("features/farms · API pública", () => {
  it("expone la finca activa, sus pantallas y solo las llamadas que usan otras features", async () => {
    const publicApi = await import("./index");

    expect(Object.keys(publicApi).sort()).toEqual([
      "CreateFarmPage", "FarmProvider", "LandPlotList", "MapaInteractivoFinca", "PaddockList",
      "deleteFarm", "getFarm", "listDepartments", "listFarms", "listLandPlots", "listPaddocks",
      "listPurposes", "updateFarm", "useFarm",
    ]);
  });
});
