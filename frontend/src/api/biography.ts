import request from './request'
import type { Biography, BiographyListItem, ListResponse } from '@/types'

export const biographyApi = {
  // 获取家族传记列表
  getBiographies: (familyId: number, params?: { skip?: number; limit?: number; search?: string }): Promise<ListResponse<BiographyListItem>> => {
    return request.get(`/biographies/family/${familyId}`, { params })
  },

  // 获取传记详情
  getBiography: (biographyId: number): Promise<Biography> => {
    return request.get(`/biographies/${biographyId}`)
  },

  // 根据人员ID获取传记
  getBiographyByPerson: (personId: number): Promise<Biography> => {
    return request.get(`/biographies/by-person/${personId}`)
  },

  // 创建传记
  createBiography: (data: {
    person_id: number
    family_id: number
    title?: string
    subtitle?: string
    summary?: string
    content: string
    achievements?: string
    portrait_url?: string
    is_published?: boolean
  }): Promise<Biography> => {
    return request.post('/biographies', data)
  },

  // 更新传记
  updateBiography: (biographyId: number, data: Partial<Biography>): Promise<Biography> => {
    return request.put(`/biographies/${biographyId}`, data)
  },

  // 删除传记
  deleteBiography: (biographyId: number): Promise<void> => {
    return request.delete(`/biographies/${biographyId}`)
  },

  // 获取可创建传记的人员列表
  getEligiblePersons: (familyId: number): Promise<any[]> => {
    return request.get(`/biographies/eligible-persons/${familyId}`)
  }
}
