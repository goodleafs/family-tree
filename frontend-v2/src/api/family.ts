import request from './request'
import type { Family, FamilyMemberInfo, ListResponse } from '@/types'

export interface FamilyCreate {
  name: string
  surname?: string
  description?: string
  history?: string
  family_motto?: string
  generation_names?: string[]
  is_public?: boolean
}

export interface FamilyUpdate {
  name?: string
  surname?: string
  description?: string
  history?: string
  family_motto?: string
  generation_names?: string[]
  is_public?: boolean
}

export interface AddMemberRequest {
  user_id: number
  role: string
}

export const familyApi = {
  getFamilies: (params?: { search?: string; skip?: number; limit?: number }): Promise<ListResponse<Family>> => {
    return request.get('/families', { params })
  },

  getFamily: (id: number): Promise<Family> => {
    return request.get(`/families/${id}`)
  },

  createFamily: (data: FamilyCreate): Promise<Family> => {
    return request.post('/families', data)
  },

  updateFamily: (id: number, data: FamilyUpdate): Promise<Family> => {
    return request.put(`/families/${id}`, data)
  },

  deleteFamily: (id: number): Promise<void> => {
    return request.delete(`/families/${id}`)
  },

  getFamilyMembers: (familyId: number): Promise<FamilyMemberInfo[]> => {
    return request.get(`/families/${familyId}/members`)
  },

  addFamilyMember: (familyId: number, data: AddMemberRequest): Promise<FamilyMemberInfo> => {
    return request.post(`/families/${familyId}/members`, data)
  },

  removeFamilyMember: (familyId: number, userId: number): Promise<void> => {
    return request.delete(`/families/${familyId}/members/${userId}`)
  },

  updateMemberRole: (familyId: number, userId: number, role: string): Promise<FamilyMemberInfo> => {
    return request.put(`/families/${familyId}/members/${userId}`, { role })
  }
}