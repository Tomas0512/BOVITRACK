/*
 * MapaInteractivoFinca.test.tsx
 * What? Pruebas del componente del mapa aéreo interactivo (foto + zonas).
 * Why?  Verificar que pinta una zona por lote real de la API (máx. 8), que el
 *       hover muestra un tooltip con datos vivos, que el click abre el panel de
 *       detalle inline y que maneja estados vacío / de error. APIs simuladas.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import MapaInteractivoFinca from "../../components/paddocks/MapaInteractivoFinca";
import { listPaddocks } from "../../api/paddocks";
import { listLandPlots } from "../../api/land_plots";

vi.mock("../../api/paddocks", () => ({
  listPaddocks: vi.fn(),
}));

vi.mock("../../api/land_plots", () => ({
  listLandPlots: vi.fn(),
}));

const makePlot = (id: string, name: string, createdAt: string, area = 10): Record<string, unknown> => ({
  id,
  farm_id: "farm",
  name,
  area,
  area_unit: "hectareas",
  usage_type: "pastoreo",
  max_capacity: 50,
  location: null,
  is_active: true,
  created_at: createdAt,
  updated_at: createdAt,
});

const plots = [
  makePlot("lot-a", "Lote A", "2026-01-01T00:00:00Z"),
  makePlot("lot-b", "Lote B", "2026-01-02T00:00:00Z"),
  makePlot("lot-c", "Lote C", "2026-01-03T00:00:00Z", 12),
];

const paddocks = [
  {
    id: "p-a1",
    farm_id: "farm",
    land_plot_id: "lot-a",
    land_plot_name: "Lote A",
    name: "Potrero A1",
    area_hectares: 4,
    max_capacity: 20,
    coverage_status: "bueno",
    pasture_type: "kikuyo",
    status: "ocupado",
    rest_start_date: null,
    rest_end_date: null,
    is_active: true,
    created_at: "",
    updated_at: "",
    animal_count: 6,
    animals: [],
  },
  {
    id: "p-c1",
    farm_id: "farm",
    land_plot_id: "lot-c",
    land_plot_name: "Lote C",
    name: "Potrero C1",
    area_hectares: 12,
    max_capacity: 30,
    coverage_status: "regular",
    pasture_type: null,
    status: "en_descanso",
    rest_start_date: null,
    rest_end_date: null,
    is_active: true,
    created_at: "",
    updated_at: "",
    animal_count: 0,
    animals: [],
  },
];

const renderMap = () =>
  render(
    <MemoryRouter>
      <MapaInteractivoFinca farmId="farm" />
    </MemoryRouter>
  );

beforeEach(() => {
  vi.mocked(listPaddocks).mockResolvedValue(paddocks as never);
  vi.mocked(listLandPlots).mockResolvedValue(plots as never);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

const waitForMap = async () => screen.findByAltText(/mapa aéreo interactivo de la finca ganadera/i);

describe("MapaInteractivoFinca", () => {
  it("renderiza la imagen y una zona por lote real de la API", async () => {
    renderMap();
    await waitForMap();

    const img = screen.getByAltText(/mapa aéreo interactivo de la finca ganadera/i);
    expect(img.getAttribute("src")).toContain("/imagenes/finca_ganadera.svg");

    const zones = screen.getAllByRole("button", { name: /ver información de lote/i });
    expect(zones).toHaveLength(3);
    expect(zones[0]?.getAttribute("aria-label")).toBe("Ver información de Lote A");
    expect(zones[1]?.getAttribute("aria-label")).toBe("Ver información de Lote B");
    expect(zones[2]?.getAttribute("aria-label")).toBe("Ver información de Lote C");
  });

  it("limita a 6 zonas aunque haya más lotes", async () => {
    const many = Array.from({ length: 12 }, (_, i) => makePlot(`l${i}`, `Lote ${i + 1}`, `2026-01-${String(i + 1).padStart(2, "0")}T00:00:00Z`));
    vi.mocked(listLandPlots).mockResolvedValue(many as never);
    renderMap();
    await waitForMap();

    expect(screen.getAllByRole("button", { name: /ver información de lote/i })).toHaveLength(6);
    expect(screen.getByText(/mostrando los primeros 6 lotes sobre el mapa/i)).toBeDefined();
  });

  it("al hacer clic en una zona abre el detalle del lote (panel inline)", async () => {
    renderMap();
    await waitForMap();

    fireEvent.click(screen.getByRole("button", { name: /ver información de lote a/i }));

    expect(screen.getByText("Lote A")).toBeDefined();
    expect(screen.getByText(/10 hectareas/)).toBeDefined();
    expect(screen.getByText("Potrero A1")).toBeDefined();
    expect(screen.getByText(/ocupado/i)).toBeDefined();
  });

  it("muestra un tooltip al pasar el mouse con datos vivos del lote", async () => {
    renderMap();
    await waitForMap();

    const zone = screen.getByRole("button", { name: /ver información de lote c/i });
    fireEvent.mouseMove(zone, { clientX: 300, clientY: 200 });
    fireEvent.mouseEnter(zone);

    expect(screen.getByRole("tooltip").textContent).toContain("Lote C");
    expect(screen.getByRole("tooltip").textContent).toContain("12 hectareas");
    expect(screen.getByRole("tooltip").textContent).toContain("1 potrero");

    fireEvent.mouseLeave(zone);
    expect(screen.queryByRole("tooltip")).toBeNull();
  });

  it("muestra el estado vacío cuando la finca no tiene lotes", async () => {
    vi.mocked(listLandPlots).mockResolvedValue([] as never);
    renderMap();

    expect(await screen.findByText(/no hay lotes registrados/i)).toBeDefined();
  });

  it("muestra un error legible cuando falla la carga", async () => {
    vi.mocked(listLandPlots).mockRejectedValue(new Error("Token inválido"));
    renderMap();

    expect(await screen.findByText(/token inválido/i)).toBeDefined();
  });
});