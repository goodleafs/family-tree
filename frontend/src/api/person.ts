import request from './request'
import type { Person, Relationship, FamilyTree, ListResponse } from '@/types'

// 成员相关API
export const personApi = {
  // 获取家族成员列表
  getFamilyPersons: (familyId: number, params?: { skip?: number; limit?: number; search?: string; generation?: number }): Promise<ListResponse<Person>> => {
    return request.get(`/persons/family/${familyId}`, { params })
  },

  // 获取成员详情
  getPerson: (id: number): Promise<Person> => {
    return request.get(`/persons/${id}`)
  },

  // 创建成员
  createPerson: (data: Partial<Person>): Promise<Person> => {
    return request.post('/persons', data)
  },

  // 更新成员
  updatePerson: (id: number, data: Partial<Person>): Promise<Person> => {
    return request.put(`/persons/${id}`, data)
  },

  // 删除成员
  deletePerson: (id: number): Promise<void> => {
    return request.delete(`/persons/${id}`)
  },

  // 上传照片
  uploadPhoto: (personId: number, file: File): Promise<{ photo_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post(`/persons/${personId}/photo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取家谱树
  getFamilyTree: (personId: number, maxGenerations?: number): Promise<FamilyTree> => {
    return request.get(`/persons/${personId}/tree`, {
      params: { max_generations: maxGenerations }
    })
  },

  // 创建关系
  createRelationship: (data: Partial<Relationship>): Promise<Relationship> => {
    return request.post('/persons/relationships', data)
  },

  getRelationships: (personId: number): Promise<Relationship[]> => {
    return request.get(`/persons/${personId}/relationships`)
  },

  updateRelationship: (relationshipId: number, data: Partial<Relationship>): Promise<Relationship> => {
    return request.put(`/persons/relationships/${relationshipId}`, data)
  },

  deleteRelationship: (relationshipId: number): Promise<void> => {
    return request.delete(`/persons/relationships/${relationshipId}`)
  }
}
