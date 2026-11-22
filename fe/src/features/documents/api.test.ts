/*
 * features/documents/api.test.ts
 * ¿Qué?  Pruebas del cliente HTTP de documentos (HU012) y del contrato de la feature.
 * ¿Para? Que las rutas y el formato de envío coincidan con el backend
 *        (/api/v1/farms/{farm_id}/documents), sin levantar el servidor.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/core/http", () => ({
  http: { get: vi.fn(), post: vi.fn(), delete: vi.fn() },
}));

import { http } from "@/core/http";
import { deleteDocument, downloadDocument, listDocuments, uploadDocument } from "./api";

const mocked = vi.mocked(http, true);

beforeEach(() => vi.clearAllMocks());

describe("features/documents · api", () => {
  it("lista los documentos de la finca con sus filtros", async () => {
    mocked.get.mockResolvedValue({ data: { documents: [], total: 0, page: 1, page_size: 20 } });

    const result = await listDocuments("f1", { association_type: "bovine", search: "vacuna" });

    expect(mocked.get).toHaveBeenCalledWith("/farms/f1/documents", {
      params: { association_type: "bovine", search: "vacuna" },
    });
    expect(result.total).toBe(0);
  });

  it("sube el archivo como multipart con su asociación", async () => {
    mocked.post.mockResolvedValue({ data: { id: "d1" } });
    const file = new File(["%PDF"], "acta.pdf", { type: "application/pdf" });

    await uploadDocument("f1", file, "pdf", "farm", "f1", "Acta de compra");

    const [url, body, config] = mocked.post.mock.calls[0];
    expect(url).toBe("/farms/f1/documents");
    expect(config).toEqual({ headers: { "Content-Type": "multipart/form-data" } });
    const form = body as FormData;
    expect(form.get("file")).toBe(file);
    expect([form.get("document_type"), form.get("association_type"), form.get("associated_entity_id")]).toEqual(["pdf", "farm", "f1"]);
    expect(form.get("description")).toBe("Acta de compra");
  });

  it("no envía descripción vacía", async () => {
    mocked.post.mockResolvedValue({ data: {} });

    await uploadDocument("f1", new File(["x"], "a.txt"), "text", "bovine", "b1");

    expect((mocked.post.mock.calls[0][1] as FormData).has("description")).toBe(false);
  });

  it("descarga como blob y elimina por id", async () => {
    const blob = new Blob(["x"]);
    mocked.get.mockResolvedValue({ data: blob });
    mocked.delete.mockResolvedValue({});

    expect(await downloadDocument("f1", "d1")).toBe(blob);
    expect(mocked.get).toHaveBeenCalledWith("/farms/f1/documents/d1/download", { responseType: "blob" });
    await deleteDocument("f1", "d1");
    expect(mocked.delete).toHaveBeenCalledWith("/farms/f1/documents/d1");
  });
});

describe("features/documents · API pública", () => {
  it("solo expone el componente DocumentManager", async () => {
    const publicApi = await import("./index");

    expect(Object.keys(publicApi)).toEqual(["DocumentManager"]);
  });
});
