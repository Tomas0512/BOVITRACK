/*
 * features/livestock/livestock.test.tsx
 * ¿Qué?  Pruebas del gráfico de pesos (carga por bovino), del manejo de errores de
 *        terneros y de la API pública de la feature.
 * ¿Para? Al cambiar de bovino, la respuesta tardía del anterior NO debe pisar los
 *        datos del nuevo (antes el efecto no lo controlaba).
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { AxiosError, type AxiosResponse } from "axios";

vi.mock("./api/weights", () => ({ listWeights: vi.fn() }));

import { listWeights } from "./api/weights";
import { handleCalfError } from "./api/calves";
import WeightChart from "./components/WeightChart";

const mockedListWeights = vi.mocked(listWeights);
beforeEach(() => vi.clearAllMocks());

function deferred<T>() {
  let resolve!: (v: T) => void;
  const promise = new Promise<T>((r) => (resolve = r));
  return { promise, resolve };
}

describe("features/livestock · WeightChart", () => {
  it("muestra el error si no se pueden cargar los pesos", async () => {
    mockedListWeights.mockRejectedValue(new Error("sin red"));
    render(<WeightChart farmId="f1" bovineId="b1" />);

    expect(await screen.findByText("No se pudo cargar el gráfico de pesos.")).toBeInTheDocument();
  });

  it("al cambiar de bovino, ignora la respuesta tardía del anterior", async () => {
    const slowB1 = deferred<Awaited<ReturnType<typeof listWeights>>>();
    mockedListWeights.mockImplementation((_farm, bovine) =>
      bovine === "b1" ? slowB1.promise : Promise.reject(new Error("b2 falla")),
    );

    const { rerender } = render(<WeightChart farmId="f1" bovineId="b1" />);
    rerender(<WeightChart farmId="f1" bovineId="b2" />);
    expect(await screen.findByText("No se pudo cargar el gráfico de pesos.")).toBeInTheDocument();

    slowB1.resolve([{ measured_at: "2026-01-01", weight_kg: "300", daily_gain: null } as never]);
    await new Promise((r) => setTimeout(r, 0));
    // sigue mostrando el estado de b2: los datos viejos de b1 se descartaron
    expect(screen.getByText("No se pudo cargar el gráfico de pesos.")).toBeInTheDocument();
    await waitFor(() => expect(mockedListWeights).toHaveBeenCalledTimes(2));
  });
});

describe("features/livestock · errores de terneros", () => {
  const axiosError = (status: number, detail?: string) =>
    new AxiosError("x", "ERR", undefined, undefined, { status, data: detail ? { detail } : {} } as AxiosResponse);

  it("usa el mensaje del backend o uno claro según el código", () => {
    expect(handleCalfError(axiosError(400, "El bovino no es un ternero"))).toBe("El bovino no es un ternero");
    expect(handleCalfError(axiosError(404))).toBe("Ternero no encontrado");
    expect(handleCalfError(axiosError(403))).toBe("No tienes acceso a esta finca");
    expect(handleCalfError(new Error("otra cosa"))).toBe("Error al procesar terneros. Intenta de nuevo.");
  });
});

describe("features/livestock · API pública", () => {
  it("expone sus componentes y solo las llamadas que usan otras features", async () => {
    const publicApi = await import("./index");

    expect(Object.keys(publicApi).sort()).toEqual([
      "BovineFormModal", "CalfList", "GrowthChart", "MovementList", "WeightChart", "WeightHistory",
      "deleteBovine", "getBovine", "importBovinesCsv", "listBovines", "listMovements",
    ]);
  });
});
