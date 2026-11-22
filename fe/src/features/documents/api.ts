import apiClient from "./axios";

export type DocumentType = "pdf" | "image" | "word" | "excel" | "text";
export type AssociationType = "farm" | "bovine" | "reproductive_event" | "treatment" | "sanitary_plan";

export interface IDocument {
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

export interface IDocumentListResponse {
  documents: IDocument[];
  total: number;
  page: number;
  page_size: number;
}

export async function listDocuments(
  farmId: string,
  params?: {
    association_type?: AssociationType;
    associated_entity_id?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }
): Promise<IDocumentListResponse> {
  const response = await apiClient.get(`/farms/${farmId}/documents`, { params });
  return response.data;
}

export async function uploadDocument(
  farmId: string,
  file: File,
  documentType: DocumentType,
  associationType: AssociationType,
  associatedEntityId: string,
  description?: string
): Promise<IDocument> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", documentType);
  formData.append("association_type", associationType);
  formData.append("associated_entity_id", associatedEntityId);
  if (description) formData.append("description", description);

  const response = await apiClient.post(`/farms/${farmId}/documents`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function downloadDocument(
  farmId: string,
  documentId: string
): Promise<Blob> {
  const response = await apiClient.get(`/farms/${farmId}/documents/${documentId}/download`, {
    responseType: "blob",
  });
  return response.data;
}

export async function deleteDocument(
  farmId: string,
  documentId: string
): Promise<void> {
  await apiClient.delete(`/farms/${farmId}/documents/${documentId}`);
}
