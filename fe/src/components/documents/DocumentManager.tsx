/**
 * ╔════════════════════════════════════════════════════════════════════════╗
 * ║ COMPONENTE: DocumentManager.tsx                                        ║
 * ║ PROPÓSITO: Gestor de documentos (upload, lista, descarga, eliminar)   ║
 * ║ HU012: Document Management                                            ║
 * ║                                                                        ║
 * ║ ¿QUÉ?                                                                  ║
 * ║   Interfaz para subir, listar, descargar y eliminar documentos        ║
 * ║   - Modal de upload con validación                                    ║
 * ║   - Tabla con listado paginado                                        ║
 * ║   - Filtros por tipo de asociación                                    ║
 * ║   - Búsqueda de documentos                                            ║
 * ║                                                                        ║
 * ║ ¿PARA QUÉ?                                                             ║
 * ║   HU012 Task 12.4: Interfaz de repositorio documental                ║
 * ║                                                                        ║
 * ║ ¿IMPACTO?                                                              ║
 * ║   Permite a usuarios adjuntar archivos a fincas/bovinos/eventos      ║
 * ╚════════════════════════════════════════════════════════════════════════╝
 */

import { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface Document {
  id: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  document_type: string;
  association_type: string;
  associated_entity_id: string;
  description?: string;
  uploaded_by: string;
  uploaded_at: string;
  is_active: boolean;
}

interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
}

// ═══════════════════════════════════════════════════════════════════════════
// 🎨 TIPOS Y CONSTANTES
// ═══════════════════════════════════════════════════════════════════════════

type DocumentType = 'pdf' | 'image' | 'word' | 'excel' | 'text';
type AssociationType = 'farm' | 'bovine' | 'reproductive_event' | 'treatment' | 'sanitary_plan';

const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  pdf: '📄 PDF',
  image: '🖼️ Imagen',
  word: '📝 Word',
  excel: '📊 Excel',
  text: '📋 Texto',
};

const ASSOCIATION_LABELS: Record<AssociationType, string> = {
  farm: 'Finca',
  bovine: 'Bovino',
  reproductive_event: 'Evento Reproductivo',
  treatment: 'Tratamiento',
  sanitary_plan: 'Plan Sanitario',
};

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

// ═══════════════════════════════════════════════════════════════════════════
// 🧩 COMPONENTE
// ═══════════════════════════════════════════════════════════════════════════

export function DocumentManager() {
  const { farm_id } = useParams<{ farm_id: string }>();

  // 📌 Estado
  const [documents, setDocuments] = useState<Document[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [pageSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<AssociationType | ''>('');

  // Upload modal
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadDocType, setUploadDocType] = useState<DocumentType>('pdf');
  const [uploadAssocType, setUploadAssocType] = useState<AssociationType>('farm');
  const [uploadEntityId, setUploadEntityId] = useState('');
  const [uploadDesc, setUploadDesc] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // 🔄 Cargar documentos
  const loadDocuments = useCallback(async () => {
    if (!farm_id) return;

    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: String(page * pageSize),
        limit: String(pageSize),
      });

      if (search) params.append('search', search);
      if (filterType) params.append('association_type', filterType);

      const response = await axios.get<DocumentListResponse>(
        `/api/v1/farms/${farm_id}/documents?${params}`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );

      setDocuments(response.data.documents);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error cargando documentos:', error);
    } finally {
      setLoading(false);
    }
  }, [farm_id, page, pageSize, search, filterType]);

  // Cargar al montar o cambiar filtros
  // useEffect(() => { loadDocuments(); }, [loadDocuments]);

  // ⬆️ Subir documento
  const handleUpload = async () => {
    if (!uploadFile || !uploadEntityId) {
      setUploadError('Selecciona archivo y entidad');
      return;
    }

    if (uploadFile.size > MAX_FILE_SIZE) {
      setUploadError('Archivo demasiado grande (máx 50MB)');
      return;
    }

    try {
      setUploading(true);
      setUploadError('');

      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('document_type', uploadDocType);
      formData.append('association_type', uploadAssocType);
      formData.append('associated_entity_id', uploadEntityId);
      if (uploadDesc) formData.append('description', uploadDesc);

      await axios.post(
        `/api/v1/farms/${farm_id}/documents`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Limpiar modal y recargar
      setUploadFile(null);
      setUploadDocType('pdf');
      setUploadAssocType('farm');
      setUploadEntityId('');
      setUploadDesc('');
      setShowUploadModal(false);
      await loadDocuments();
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : 'Error al subir');
    } finally {
      setUploading(false);
    }
  };

  // 📥 Descargar documento
  const handleDownload = async (docId: string, filename: string) => {
    try {
      const response = await axios.get(
        `/api/v1/farms/${farm_id}/documents/${docId}/download`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          responseType: 'blob',
        }
      );

      const blob = new Blob([response.data]);
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(link.href);
    } catch (error) {
      console.error('Error descargando:', error);
    }
  };

  // 🗑️ Eliminar documento
  const handleDelete = async (docId: string) => {
    if (!confirm('¿Eliminar documento?')) return;

    try {
      await axios.delete(
        `/api/v1/farms/${farm_id}/documents/${docId}`,
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      await loadDocuments();
    } catch (error) {
      console.error('Error eliminando:', error);
    }
  };

  // 📊 Tamaño legible
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
  };

  // 📅 Fecha legible
  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6 p-6 bg-white rounded-lg shadow">
      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* 🎯 ENCABEZADO Y CONTROLES */}
      {/* ═══════════════════════════════════════════════════════════════════ */}

      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">📁 Documentos</h2>
        <button
          onClick={() => setShowUploadModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          ⬆️ Subir Documento
        </button>
      </div>

      {/* Búsqueda y filtros */}
      <div className="flex gap-4 flex-wrap">
        <input
          type="text"
          placeholder="Buscar documentos..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="flex-1 min-w-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <select
          value={filterType}
          onChange={(e) => {
            setFilterType(e.target.value as AssociationType | '');
            setPage(0);
          }}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todos los tipos</option>
          {(Object.keys(ASSOCIATION_LABELS) as AssociationType[]).map((type) => (
            <option key={type} value={type}>
              {ASSOCIATION_LABELS[type]}
            </option>
          ))}
        </select>
      </div>

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* 📋 TABLA DE DOCUMENTOS */}
      {/* ═══════════════════════════════════════════════════════════════════ */}

      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Nombre</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Tipo</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Tamaño</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Fecha</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Asociado a</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  ⏳ Cargando...
                </td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No hay documentos
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-900 truncate max-w-xs">
                    {doc.original_filename}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                      {DOCUMENT_TYPE_LABELS[doc.document_type as DocumentType]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatFileSize(doc.file_size)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatDate(doc.uploaded_at)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                      {ASSOCIATION_LABELS[doc.association_type as AssociationType]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm space-x-2">
                    <button
                      onClick={() => handleDownload(doc.id, doc.original_filename)}
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      📥
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-600 hover:text-red-800 underline"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      {total > pageSize && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">
            Mostrando {page * pageSize + 1} a {Math.min((page + 1) * pageSize, total)} de {total}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
            >
              ⬅️
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * pageSize >= total}
              className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
            >
              ➡️
            </button>
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════════════════════ */}
      {/* 📤 MODAL DE UPLOAD */}
      {/* ═══════════════════════════════════════════════════════════════════ */}

      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full space-y-6 p-6">
            <h3 className="text-xl font-bold text-gray-900">Subir Documento</h3>

            {/* Archivo */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Archivo (máx 50MB)
              </label>
              <input
                type="file"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) setUploadFile(file);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              {uploadFile && (
                <p className="text-sm text-gray-600 mt-2">
                  ✅ {uploadFile.name} ({formatFileSize(uploadFile.size)})
                </p>
              )}
            </div>

            {/* Tipo de documento */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Documento
              </label>
              <select
                value={uploadDocType}
                onChange={(e) => setUploadDocType(e.target.value as DocumentType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              >
                {(Object.entries(DOCUMENT_TYPE_LABELS) as [DocumentType, string][]).map(
                  ([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  )
                )}
              </select>
            </div>

            {/* Asociación */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Asociado a
                </label>
                <select
                  value={uploadAssocType}
                  onChange={(e) => setUploadAssocType(e.target.value as AssociationType)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  {(Object.entries(ASSOCIATION_LABELS) as [AssociationType, string][]).map(
                    ([key, label]) => (
                      <option key={key} value={key}>
                        {label}
                      </option>
                    )
                  )}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ID de la Entidad
                </label>
                <input
                  type="text"
                  value={uploadEntityId}
                  onChange={(e) => setUploadEntityId(e.target.value)}
                  placeholder="UUID de finca/bovino/etc"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
            </div>

            {/* Descripción */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción (opcional)
              </label>
              <textarea
                value={uploadDesc}
                onChange={(e) => setUploadDesc(e.target.value)}
                placeholder="Descripción del documento..."
                maxLength={500}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </div>

            {/* Error */}
            {uploadError && (
              <div className="px-4 py-3 bg-red-100 text-red-800 rounded-lg text-sm">
                ❌ {uploadError}
              </div>
            )}

            {/* Botones */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowUploadModal(false)}
                disabled={uploading}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleUpload}
                disabled={uploading || !uploadFile}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {uploading ? '⏳ Subiendo...' : '⬆️ Subir'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
