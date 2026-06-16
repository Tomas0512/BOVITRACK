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

const TYPE_BADGE: Record<string, string> = {
  pdf: "bg-red-100 text-red-800",
  image: "bg-purple-100 text-purple-800",
  word: "bg-blue-100 text-blue-800",
  excel: "bg-green-100 text-green-800",
  text: "bg-gray-100 text-gray-600",
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
    <div className="mt-6">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-bold text-gray-900">Documentos</h2>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar documentos..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              className="rounded-lg border border-gray-200 py-1.5 pl-8 pr-3 text-sm focus:border-primary focus:outline-none"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => { setFilterType(e.target.value as AssociationType | ""); setPage(0); }}
            className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-primary focus:outline-none"
          >
            <option value="">Todos</option>
            {(Object.keys(ASSOCIATION_LABELS) as AssociationType[]).map((type) => (
              <option key={type} value={type}>{ASSOCIATION_LABELS[type]}</option>
            ))}
          </select>
          <button
            onClick={() => setShowUploadModal(true)}
            className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-1.5 text-sm font-bold text-white hover:bg-primary-light"
          >
            <Plus size={16} />
            Subir
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertTriangle size={16} /> {error}
          <button onClick={() => setError("")} className="ml-auto font-bold">X</button>
        </div>
      )}

      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-xs font-semibold uppercase text-gray-500">
            <tr>
              <th className="px-4 py-3">Nombre</th>
              <th className="px-4 py-3">Tipo</th>
              <th className="px-4 py-3">Tamanio</th>
              <th className="px-4 py-3">Fecha</th>
              <th className="px-4 py-3">Asociado a</th>
              <th className="px-4 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                  <div className="flex justify-center py-8">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  </div>
                </td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-sm text-gray-400">
                  No hay documentos
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="max-w-xs truncate px-4 py-3 text-gray-900">{doc.original_filename}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold ${TYPE_BADGE[doc.document_type] || "bg-gray-100 text-gray-600"}`}>
                      {DOCUMENT_TYPE_LABELS[doc.document_type as DocumentType] || doc.document_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{formatFileSize(doc.file_size)}</td>
                  <td className="px-4 py-3 text-gray-700">{formatDate(doc.uploaded_at)}</td>
                  <td className="px-4 py-3">
                    <span className="inline-block rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-800">
                      {ASSOCIATION_LABELS[doc.association_type as AssociationType] || doc.association_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDownload(doc)}
                      className="mr-1 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                      title="Descargar"
                    >
                      <Download size={15} />
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
                      title="Eliminar"
                    >
                      <Trash2 size={15} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {total > pageSize && (
        <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
          <span>
            {page * pageSize + 1}-{Math.min((page + 1) * pageSize, total)} de {total}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="rounded-lg border border-gray-200 px-3 py-1 disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * pageSize >= total}
              className="rounded-lg border border-gray-200 px-3 py-1 disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-lg space-y-4 rounded-xl bg-white p-6 shadow-lg">
            <h3 className="text-lg font-bold text-gray-900">Subir Documento</h3>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Archivo (max 50MB)</label>
              <input
                type="file"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) setUploadFile(f); }}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
              />
              {uploadFile && (
                <p className="mt-1 text-xs text-gray-500">{uploadFile.name} ({formatFileSize(uploadFile.size)})</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Tipo</label>
                <select
                  value={uploadDocType}
                  onChange={(e) => setUploadDocType(e.target.value as DocumentType)}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                >
                  {(Object.entries(DOCUMENT_TYPE_LABELS) as [DocumentType, string][]).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Asociado a</label>
                <select
                  value={uploadAssocType}
                  onChange={(e) => setUploadAssocType(e.target.value as AssociationType)}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
                >
                  {(Object.entries(ASSOCIATION_LABELS) as [AssociationType, string][]).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">ID de la Entidad</label>
              <input
                type="text"
                value={uploadEntityId}
                onChange={(e) => setUploadEntityId(e.target.value)}
                placeholder="UUID de la entidad"
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Descripcion (opcional)</label>
              <textarea
                value={uploadDesc}
                onChange={(e) => setUploadDesc(e.target.value)}
                maxLength={500}
                rows={2}
                className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
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
                className="rounded-lg border border-gray-200 px-4 py-2 text-sm hover:bg-gray-50 disabled:opacity-50"
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
