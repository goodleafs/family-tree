import request from './request'
import type { Family, FamilyMember, FamilyMemberInfo, ListResponse } from '@/types'

export const familyApi = {
  getFamilies: (params?: { skip?: number; limit?: number; search?: string }): Promise<ListResponse<Family>> => {
    return request.get('/families', { params })
  },

  getFamily: (id: number): Promise<Family> => {
    return request.get(`/families/${id}`)
  },

  createFamily: (data: Partial<Family>): Promise<Family> => {
    return request.post('/families', data)
  },

  updateFamily: (id: number, data: Partial<Family>): Promise<Family> => {
    return request.put(`/families/${id}`, data)
  },

  deleteFamily: (id: number): Promise<void> => {
    return request.delete(`/families/${id}`)
  },

  getFamilyMembers: (familyId: number): Promise<FamilyMemberInfo[]> => {
    return request.get(`/families/${familyId}/members`)
  },

  updateMemberRole: (familyId: number, userId: number, role: string): Promise<{ message: string; role: string }> => {
    return request.put(`/families/${familyId}/members/${userId}/role`, null, {
      params: { role }
    })
  },

  addFamilyMember: (familyId: number, data: { user_id: number; role: string }): Promise<FamilyMember> => {
    return request.post(`/families/${familyId}/members`, data)
  },

  removeFamilyMember: (familyId: number, userId: number): Promise<{ message: string }> => {
    return request.delete(`/families/${familyId}/members/${userId}`)
  }
}
