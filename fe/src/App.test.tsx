/*
 * App.test.tsx
 * ¿Qué? Tests básicos del componente raíz App.
 * ¿Para qué? Verificar que la app renderiza correctamente.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

describe("App", () => {
  it("renderiza el texto de construcción", () => {
    render(<App />);
    expect(screen.getByText(/Bovitrack — En construcción/i)).toBeDefined();
  });

  it("renderiza el emoji de vaca", () => {
    render(<App />);
    expect(screen.getByText(/🐄/i)).toBeDefined();
  });
});
