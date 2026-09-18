/*
 * App.test.tsx
 * What? Tests básicos del componente raíz App.
 * Why? Verificar que la app renderiza correctamente.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renderiza el hero de la plataforma", () => {
    render(<App />);
    expect(screen.getByText(/Tu ganado bajo control con/i)).toBeInTheDocument();
  });

  it("muestra el acceso a registro desde el home", () => {
    render(<App />);
    expect(screen.getByRole("link", { name: "Registrarse" })).toBeInTheDocument();
  });
});