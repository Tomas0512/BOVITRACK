/*
 * app/layout/Breadcrumbs.test.tsx
 * ¿Qué?  Pruebas de las migas de pan del layout autenticado.
 * ¿Para? Que cada ruta muestre dónde está el usuario, incluida la ficha del bovino
 *        (antes la expresión de 3 segmentos la dejaba sin migas).
 */

import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Breadcrumbs from "./Breadcrumbs";

function trailAt(path: string): string | null {
  const { container, unmount } = render(
    <MemoryRouter initialEntries={[path]}>
      <Breadcrumbs />
    </MemoryRouter>,
  );
  const nav = container.querySelector("nav");
  const text = nav ? nav.textContent : null;
  unmount();
  return text;
}

describe("Breadcrumbs", () => {
  it("no se muestra en el dashboard ni en rutas sin miga propia", () => {
    expect(trailAt("/dashboard")).toBeNull();
    expect(trailAt("/otra")).toBeNull();
  });

  it("muestra el camino de cada sección", () => {
    expect(trailAt("/farms/new")).toBe("Inicio/Nueva Finca");
    expect(trailAt("/audit")).toBe("Inicio/Auditoría");
    expect(trailAt("/admin/reactivations")).toBe("Inicio/Reactivaciones");
    expect(trailAt("/farms/f1")).toBe("Inicio/Detalle de Finca");
    expect(trailAt("/farms/f1/economics")).toBe("Inicio/Detalle de Finca/Economía");
    expect(trailAt("/farms/f1/reports")).toBe("Inicio/Detalle de Finca/Reportes");
    expect(trailAt("/farms/f1/alerts")).toBe("Inicio/Detalle de Finca/Alertas");
  });

  it("la ficha del bovino (4 segmentos) tiene migas y enlaza a su finca", () => {
    expect(trailAt("/farms/f1/bovines/b1")).toBe("Inicio/Detalle de Finca/Bovino");

    render(
      <MemoryRouter initialEntries={["/farms/f1/bovines/b1"]}>
        <Breadcrumbs />
      </MemoryRouter>,
    );
    expect(screen.getByRole("link", { name: "Detalle de Finca" })).toHaveAttribute("href", "/farms/f1");
    expect(screen.getByRole("link", { name: "Inicio" })).toHaveAttribute("href", "/dashboard");
  });
});
