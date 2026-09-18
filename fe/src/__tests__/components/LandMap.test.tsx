/*
 * LandMap.test.tsx
 * What? Pruebas del componente del mapa de la finca.
 * Why?  Verificar que dibuja una parcela por lote y potrero con colores
 *       naturales (uso + cobertura, sin estado), permite seleccionar un
 *       potrero para ver su detalle y maneja estados vacío / de error.
 *       La API se simula con mocks.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import LandMap from "../../components/paddocks/LandMap";
import { parcelFillColor } from "../../components/paddocks/parcelGeometry";
import { listPaddocks } from "../../api/paddocks";
import { listLandPlots } from "../../api/land_plots";

vi.mock("../../api/paddocks", () => ({
  listPaddocks: vi.fn(),
}));

vi.mock("../../api/land_plots", () => ({
  listLandPlots: vi.fn(),
}));

const plots = [
  {
    id: "lot-1",
    farm_id: "farm",
    name: "Lote Norte",
    area: 10,
    area_unit: "hectareas",
    usage_type: "pastoreo",
    max_capacity: 50,
    location: null,
    is_active: true,
    created_at: "",
    updated_at: "",
  },
  {
    id: "lot-2",
    farm_id: "farm",
    name: "Lote Sur",
    area: 6,
    area_unit: "hectareas",
    usage_type: "cultivo",
    max_capacity: 20,
    location: null,
    is_active: true,
    created_at: "",
    updated_at: "",
  },
];

const paddocks = [
  {
    id: "p1",
    farm_id: "farm",
    land_plot_id: "lot-1",
    land_plot_name: "Lote Norte",
    name: "Potrero A",
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
    animal_count: 5,
    animals: [{ id: "a1", identification_number: "001", name: "Blanca" }],
  },
  {
    id: "p2",
    farm_id: "farm",
    land_plot_id: "lot-1",
    land_plot_name: "Lote Norte",
    name: "Potrero B",
    area_hectares: 6,
    max_capacity: 30,
    coverage_status: "regular",
    pasture_type: null,
    status: "libre",
    rest_start_date: null,
    rest_end_date: null,
    is_active: true,
    created_at: "",
    updated_at: "",
    animal_count: 0,
    animals: [],
  },
  {
    id: "p3",
    farm_id: "farm",
    land_plot_id: "lot-2",
    land_plot_name: "Lote Sur",
    name: "Potrero C",
    area_hectares: 6,
    max_capacity: 20,
    coverage_status: "malo",
    pasture_type: null,
    status: "en_descanso",
    rest_start_date: "2026-09-01",
    rest_end_date: "2026-10-01",
    is_active: true,
    created_at: "",
    updated_at: "",
    animal_count: 0,
    animals: [],
  },
  {
    id: "p4",
    farm_id: "farm",
    land_plot_id: "lot-1",
    land_plot_name: "Lote Norte",
    name: "Potrero D",
    area_hectares: 2,
    max_capacity: 10,
    coverage_status: "bueno",
    pasture_type: null,
    status: "libre",
    rest_start_date: null,
    rest_end_date: null,
    is_active: true,
    created_at: "",
    updated_at: "",
    animal_count: 0,
    animals: [],
  },
];

beforeEach(() => {
  vi.mocked(listPaddocks).mockResolvedValue(paddocks);
  vi.mocked(listLandPlots).mockResolvedValue(plots);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

const waitForMap = async () => screen.findByRole("img", { name: /mapa de la finca/i });

describe("LandMap", () => {
  it("dibuja una zona por lote y sus potreros", async () => {
    render(<LandMap farmId="farm" />);
    await waitForMap();

    expect(screen.getByText("Lote Norte")).toBeDefined();
    expect(screen.getByText("Lote Sur")).toBeDefined();
    expect(screen.getAllByText(/Potrero [ABC]/u).length).toBeGreaterThan(0);
  });

  it("colorea el terreno con tono natural del uso (pastoreo bueno)", async () => {
    render(<LandMap farmId="farm" />);
    await waitForMap();

    const potrero = screen.getByRole("button", { name: /Potrero A/ });
    const path = potrero.querySelector("path");
    expect(path?.getAttribute("fill")).toBe(parcelFillColor("pastoreo", "bueno"));
  });

  it("el estado del potrero NO cambia el color del terreno", async () => {
    render(<LandMap farmId="farm" />);
    await waitForMap();

    const ocupado = screen.getByRole("button", { name: /Potrero A/ }).querySelector("path");
    const libre = screen.getByRole("button", { name: /Potrero D/ }).querySelector("path");
    expect(ocupado?.getAttribute("fill")).toBe(libre?.getAttribute("fill"));
  });

  it("marca con tramado las parcelas de cobertura mala", async () => {
    render(<LandMap farmId="farm" />);
    await waitForMap();

    const potrero = screen.getByRole("button", { name: /Potrero C/ });
    const hatch = [...potrero.querySelectorAll("path")].find((p) => p.getAttribute("fill") === "url(#coverage-hatch)");
    expect(hatch).toBeDefined();
  });

  it("dibuja la decoración (camino de entrada) debajo de las parcelas", async () => {
    render(<LandMap farmId="farm" />);
    const svg = await waitForMap();

    const paths = Array.from(svg.querySelectorAll<SVGPathElement>("path"));
    const entrance = paths.find((p) => p.getAttribute("stroke-width") === "10");
    const parcel = paths.find((p) => p.getAttribute("stroke-width") === "8" && p.getAttribute("fill")?.startsWith("#"));

    expect(entrance).toBeDefined();
    expect(parcel).toBeDefined();
    if (!entrance || !parcel) return;

    const rel = entrance.compareDocumentPosition(parcel);
    expect(rel & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("dibuja una mancha de bosque en los lotes de cultivo/reserva", async () => {
    render(<LandMap farmId="farm" />);
    const svg = await waitForMap();

    const canopies = svg.querySelectorAll('circle[fill="#3f6b3f"]');
    expect(canopies.length).toBeGreaterThanOrEqual(1);
  });

  it("muestra el detalle del potrero al seleccionarlo", async () => {
    render(<LandMap farmId="farm" />);
    await waitForMap();

    fireEvent.click(screen.getByRole("button", { name: /Potrero A/ }));

    expect(await screen.findByText(/001/)).toBeDefined();
    expect(screen.getByText(/Blanca/)).toBeDefined();
    expect(screen.getByText(/kikuyo/)).toBeDefined();
  });

  it("muestra el estado vacío cuando la finca no tiene lotes", async () => {
    vi.mocked(listLandPlots).mockResolvedValue([]);
    render(<LandMap farmId="farm" />);

    expect(await screen.findByText(/No hay lotes registrados/)).toBeDefined();
  });

  it("muestra un error legible cuando falla la carga", async () => {
    vi.mocked(listPaddocks).mockRejectedValue(new Error("Token inválido"));
    render(<LandMap farmId="farm" />);

    expect(await screen.findByText(/Token inválido/)).toBeDefined();
  });
});