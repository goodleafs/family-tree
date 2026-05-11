import request from './request'
import type { Biography, BiographyListItem, ListResponse } from '@/types'

export const biographyApi = {
  getBiographies: (familyId: number, params?: { skip?: number; limit?: number; search?: string }): Promise<ListResponse<BiographyListItem>> => {
    return request.get(`/biographies/family/${familyId}`, { params })
  },

  getBiography: (biographyId: number): Promise<Biography> => {
    return request.get(`/biographies/${biographyId}`)
  },

  getBiographyByPerson: (personId: number): Promise<Biography> => {
    return request.get(`/biographies/by-person/${personId}`)
  },

  createBiography: (data: {
    person_id: number; family_id: number; title?: string; subtitle?: string
    summary?: string; content: string; achievements?: string; portrait_url?: string; is_published?: boolean
  }): Promise<Biography> => {
    return request.post('/biographies', data)
  },

  updateBiography: (biographyId: number, data: Partial<Biography>): Promise<Biography> => {
    return request.put(`/biographies/${biographyId}`, data)
  },

  deleteBiography: (biographyId: number): Promise<void> => {
    return request.delete(`/biographies/${biographyId}`)
  },

  getEligiblePersons: (familyId: number): Promise<any[]> => {
    return request.get(`/biographies/eligible-persons/${familyId}`)
  }
}
