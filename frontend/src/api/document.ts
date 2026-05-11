import request from './request'
import type { Document, DocumentOverview, ListResponse } from '@/types'

export const documentApi = {
  // 获取家族文献列表
  getDocuments: (familyId: number, params?: { skip?: number; limit?: number; category?: string; search?: string }): Promise<ListResponse<Document>> => {
    return request.get(`/documents/family/${familyId}`, { params })
  },

  // 获取文献库概览
  getOverview: (familyId: number): Promise<DocumentOverview> => {
    return request.get(`/documents/family/${familyId}/overview`)
  },

  // 获取文献详情
  getDocument: (documentId: number): Promise<Document> => {
    return request.get(`/documents/${documentId}`)
  },

  // 上传文献
  uploadDocument: (
    familyId: number,
    file: File,
    data?: {
      title?: string
      description?: string
      author?: string
      document_date?: string
      tags?: string
      category?: string
    }
  ): Promise<Document> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('family_id', String(familyId))
    if (data?.title) formData.append('title', data.title)
    if (data?.description) formData.append('description', data.description)
    if (data?.author) formData.append('author', data.author)
    if (data?.document_date) formData.append('document_date', data.document_date)
    if (data?.tags) formData.append('tags', data.tags)
    if (data?.category) formData.append('category', data.category)
    return request.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { family_id: familyId, ...data }
    })
  },

  // 更新文献信息
  updateDocument: (documentId: number, data: Partial<Document>): Promise<Document> => {
    return request.put(`/documents/${documentId}`, data)
  },

  // 删除文献
  deleteDocument: (documentId: number): Promise<void> => {
    return request.delete(`/documents/${documentId}`)
  }
}
