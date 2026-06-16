/*
 * App.test.tsx
 * What? Tests básicos del componente raíz App.
 * Why? Verificar que la app renderiza correctamente.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renderiza el texto de construcción", () => {
    render(<App />);
    expect(screen.getByText(/Bovitrack — En construcción/i)).toBeDefined();
  });

  it("renderiza el título de la plataforma", () => {
    render(<App />);
    expect(screen.getByText(/BoviTrack/i)).toBeDefined();
  });
});
