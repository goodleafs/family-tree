import request from './request'
import type { Document, DocumentOverview, ListResponse } from '@/types'

export const documentApi = {
  getDocuments: (familyId: number, params?: { skip?: number; limit?: number; category?: string; search?: string }): Promise<ListResponse<Document>> => {
    return request.get(`/documents/family/${familyId}`, { params })
  },

  getOverview: (familyId: number): Promise<DocumentOverview> => {
    return request.get(`/documents/family/${familyId}/overview`)
  },

  getDocument: (documentId: number): Promise<Document> => {
    return request.get(`/documents/${documentId}`)
  },

  uploadDocument: (familyId: number, file: File, data?: {
    title?: string; description?: string; author?: string
    document_date?: string; tags?: string; category?: string
  }): Promise<Document> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('family_id', String(familyId))
    return request.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { family_id: familyId, ...data }
    })
  },

  updateDocument: (documentId: number, data: Partial<Document>): Promise<Document> => {
    return request.put(`/documents/${documentId}`, data)
  },

  deleteDocument: (documentId: number): Promise<void> => {
    return request.delete(`/documents/${documentId}`)
  }
}
