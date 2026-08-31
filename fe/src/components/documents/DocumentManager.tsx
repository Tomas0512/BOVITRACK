import { useEffect, useState, useCallback } from "react";
import { Plus, Trash2, Download, Search, AlertTriangle } from "lucide-react";
import {
  listDocuments,
  uploadDocument,
  downloadDocument,
  deleteDocument,
  type IDocument,
  type DocumentType,
  type AssociationType,
} from "../../api/documents";

const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  pdf: "PDF",
  image: "Imagen",
  word: "Word",
  excel: "Excel",
  text: "Texto",
};

// Misma escala que los badges de la lista de empleados (50/700): chips claros
// que se leen bien tanto sobre el fondo claro como sobre el oscuro.
const TYPE_BADGE: Record<string, string> = {
  pdf: "bg-red-50 text-red-700",
  image: "bg-purple-50 text-purple-700",
  word: "bg-blue-50 text-blue-700",
  excel: "bg-green-50 text-green-700",
  text: "bg-surface-alt text-text-secondary",
};

const ASSOCIATION_LABELS: Record<AssociationType, string> = {
  farm: "Finca",
  bovine: "Bovino",
  reproductive_event: "Evento Reproductivo",
  treatment: "Tratamiento",
  sanitary_plan: "Plan Sanitario",
};

interface Props {
  farmId: string;
}

export default function DocumentManager({ farmId }: Props) {
  const [documents, setDocuments] = useState<IDocument[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState<AssociationType | "">("");

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadDocType, setUploadDocType] = useState<DocumentType>("pdf");
  const [uploadAssocType, setUploadAssocType] = useState<AssociationType>("farm");
  const [uploadEntityId, setUploadEntityId] = useState("");
  const [uploadDesc, setUploadDesc] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const loadDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const data = await listDocuments(farmId, {
        skip: page * pageSize,
        limit: pageSize,
        search: search || undefined,
        association_type: filterType || undefined,
      });
      setDocuments(data.documents);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar documentos");
    } finally {
      setLoading(false);
    }
  }, [farmId, page, pageSize, search, filterType]);

  useEffect(() => { loadDocuments(); }, [loadDocuments]);

  const handleUpload = async () => {
    if (!uploadFile || !uploadEntityId) {
      setUploadError("Selecciona archivo y entidad");
      return;
    }
    if (uploadFile.size > 52428800) {
      setUploadError("Archivo demasiado grande (max 50MB)");
      return;
    }
    try {
      setUploading(true);
      setUploadError("");
      await uploadDocument(
        farmId,
        uploadFile,
        uploadDocType,
        uploadAssocType,
        uploadEntityId,
        uploadDesc || undefined
      );
      setUploadFile(null);
      setUploadDocType("pdf");
      setUploadAssocType("farm");
      setUploadEntityId("");
      setUploadDesc("");
      setShowUploadModal(false);
      loadDocuments();
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Error al subir");
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (doc: IDocument) => {
    try {
      const blob = await downloadDocument(farmId, doc.id);
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = doc.original_filename;
      link.click();
      window.URL.revokeObjectURL(link.href);
    } catch {
      setError("Error al descargar");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Eliminar documento?")) return;
    try {
      await deleteDocument(farmId, id);
      loadDocuments();
    } catch {
      setError("No se pudo eliminar el documento");
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / 1048576).toFixed(1)}MB`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("es-CO", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="mt-6 rounded-2xl bg-surface p-6 shadow-sm">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-text-primary">Documentos</h2>
          <p className="text-xs text-text-muted">
            {total} documento{total !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              type="text"
              placeholder="Buscar documentos..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              className="rounded-lg border border-border bg-surface-alt py-2 pl-8 pr-3 text-sm text-text-primary placeholder:text-text-muted focus:border-primary focus:outline-none"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => { setFilterType(e.target.value as AssociationType | ""); setPage(0); }}
            className="rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
          >
            <option value="">Todos</option>
            {(Object.keys(ASSOCIATION_LABELS) as AssociationType[]).map((type) => (
              <option key={type} value={type}>{ASSOCIATION_LABELS[type]}</option>
            ))}
          </select>
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light"
          >
            <Plus size={16} />
            Subir
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-3 flex items-center gap-2 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-700">
          <AlertTriangle size={16} /> {error}
          <button onClick={() => setError("")} className="ml-auto font-bold">X</button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : documents.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border py-10 text-center">
          <p className="text-sm text-text-muted">No hay documentos en esta categoría</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs font-semibold uppercase tracking-wide text-text-muted">
                <th className="pb-2 pr-4">Nombre</th>
                <th className="pb-2 pr-4">Tipo</th>
                <th className="pb-2 pr-4">Tamaño</th>
                <th className="pb-2 pr-4">Fecha</th>
                <th className="pb-2 pr-4">Asociado a</th>
                <th className="pb-2">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-surface-alt">
                  <td className="max-w-xs truncate py-3 pr-4 font-medium text-text-primary">
                    {doc.original_filename}
                  </td>
                  <td className="py-3 pr-4">
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                        TYPE_BADGE[doc.document_type] || TYPE_BADGE.text
                      }`}
                    >
                      {DOCUMENT_TYPE_LABELS[doc.document_type as DocumentType] || doc.document_type}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-text-secondary">{formatFileSize(doc.file_size)}</td>
                  <td className="py-3 pr-4 text-text-secondary">{formatDate(doc.uploaded_at)}</td>
                  <td className="py-3 pr-4">
                    <span className="inline-block rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700">
                      {ASSOCIATION_LABELS[doc.association_type as AssociationType] || doc.association_type}
                    </span>
                  </td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleDownload(doc)}
                        className="rounded px-2 py-1 text-xs font-medium text-text-secondary hover:bg-surface-alt"
                        title="Descargar"
                      >
                        <Download size={15} />
                      </button>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="rounded px-2 py-1 text-xs font-medium text-red-500 hover:bg-red-50"
                        title="Eliminar"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {total > pageSize && (
        <div className="mt-3 flex items-center justify-between text-sm text-text-secondary">
          <span>
            {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} de {total}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="rounded-lg border border-border px-3 py-1 hover:bg-surface-alt disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * pageSize >= total}
              className="rounded-lg border border-border px-3 py-1 hover:bg-surface-alt disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg space-y-4 rounded-xl bg-surface p-6 shadow-lg">
            <h3 className="text-lg font-bold text-text-primary">Subir Documento</h3>

            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Archivo (max 50MB)</label>
              <input
                type="file"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) setUploadFile(f); }}
                className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary"
              />
              {uploadFile && (
                <p className="mt-1 text-xs text-text-muted">{uploadFile.name} ({formatFileSize(uploadFile.size)})</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Tipo</label>
                <select
                  value={uploadDocType}
                  onChange={(e) => setUploadDocType(e.target.value as DocumentType)}
                  className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
                >
                  {(Object.entries(DOCUMENT_TYPE_LABELS) as [DocumentType, string][]).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-text-secondary">Asociado a</label>
                <select
                  value={uploadAssocType}
                  onChange={(e) => setUploadAssocType(e.target.value as AssociationType)}
                  className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
                >
                  {(Object.entries(ASSOCIATION_LABELS) as [AssociationType, string][]).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">ID de la Entidad</label>
              <input
                type="text"
                value={uploadEntityId}
                onChange={(e) => setUploadEntityId(e.target.value)}
                placeholder="UUID de la entidad"
                className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">Descripcion (opcional)</label>
              <textarea
                value={uploadDesc}
                onChange={(e) => setUploadDesc(e.target.value)}
                maxLength={500}
                rows={2}
                className="w-full rounded-lg border border-border bg-surface-alt px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
              />
            </div>

            {uploadError && (
              <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                <AlertTriangle size={16} /> {uploadError}
              </div>
            )}

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowUploadModal(false)}
                disabled={uploading}
                className="rounded-lg border border-border px-4 py-2 text-sm text-text-secondary hover:bg-surface-alt disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleUpload}
                disabled={uploading || !uploadFile}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-bold text-white hover:bg-primary-light disabled:opacity-50"
              >
                {uploading ? "Subiendo..." : "Subir"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
