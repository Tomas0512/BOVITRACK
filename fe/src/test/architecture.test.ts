/*
 * test/architecture.test.ts
 * ¿Qué?  Contrato de ESTRUCTURA del frontend (complementa las reglas de ESLint).
 * ¿Para? Que nadie vuelva a crear carpetas "por tipo de archivo" (api/, components/,
 *        pages/…) fuera de las capas, y que toda feature tenga su API pública y su
 *        documentación de arquitectura.
 * ¿Cómo? import.meta.glob de Vite lista los archivos sin importarlos.
 */

import { describe, expect, it } from "vitest";

const files = Object.keys(import.meta.glob("/src/**/*.{ts,tsx,css,md}"));
const rel = (p: string) => p.replace(/^\/src\//, "");

const TOP_LEVEL = ["app", "core", "features", "shared", "test", "README.md", "index.css", "main.tsx", "vite-env.d.ts"];

describe("estructura del frontend", () => {
  it("src/ solo tiene las capas acordadas (nada de api/, components/, pages/ sueltos)", () => {
    const top = [...new Set(files.map((f) => rel(f).split("/")[0]))].sort();
    expect(top.filter((t) => !TOP_LEVEL.includes(t))).toEqual([]);
  });

  it("cada feature tiene index.ts (su API pública) y README.md (sus conceptos)", () => {
    const features = [...new Set(files.map(rel).filter((f) => f.startsWith("features/")).map((f) => f.split("/")[1]))];
    expect(features.length).toBeGreaterThan(10);
    for (const feature of features) {
      expect(files, `features/${feature}/index.ts`).toContain(`/src/features/${feature}/index.ts`);
      expect(files, `features/${feature}/README.md`).toContain(`/src/features/${feature}/README.md`);
    }
  });

  it("no hay archivos sueltos en features/ y cada feature tiene a lo sumo un nivel de subcarpetas", () => {
    const inFeatures = files.map(rel).filter((f) => f.startsWith("features/"));
    expect(inFeatures.filter((f) => f.split("/").length === 2)).toEqual([]); // features/x.ts
    expect(inFeatures.filter((f) => f.split("/").length > 4)).toEqual([]); // features/f/a/b/x.ts
  });

  it("shared y core exponen una API pública por carpeta", () => {
    for (const unit of ["core/http", "shared/ui", "shared/hooks", "shared/theme", "shared/layout"]) {
      expect(files, unit).toContain(`/src/${unit}/index.ts`);
    }
  });
});
