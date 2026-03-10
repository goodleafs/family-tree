import request from './request'
import type { ListResponse } from '@/types'

export interface OfferingItem {
  name: string
  icon: string
}

export interface MemorialHallCreate {
  person_id: number
  offerings?: OfferingItem[]
}

export interface MemorialHallUpdate {
  offerings?: OfferingItem[]
  is_active?: boolean
}

export interface PersonBrief {
  id: number
  name: string
  gender?: string
  birth_date?: string
  death_date?: string
  photo_url?: string
}

export interface CreatorBrief {
  id: number
  username: string
}

export interface MemorialHall {
  id: number
  person: PersonBrief
  offerings: OfferingItem[]
  incense_count: number
  worship_count: number
  is_active: boolean
  creator: CreatorBrief
  created_at: string
}

export interface MemorialHallListItem {
  id: number
  person: PersonBrief
  worship_count: number
  is_active: boolean
  creator: CreatorBrief
  created_at: string
}

export interface WorshipRequest {
  worship_type: 'kowtow' | 'incense' | 'offering'
  message?: string
}

export interface WorshipRecord {
  id: number
  user_id?: number
  username?: string
  worship_type: string
  message?: string
  created_at: string
}

export const memorialApi = {
  // 获取灵堂列表
  getMemorialHalls: (params?: { skip?: number; limit?: number; family_id?: number }): Promise<ListResponse<MemorialHallListItem>> => {
    return request.get('/memorial/halls', { params })
  },

  // 获取灵堂详情
  getMemorialHall: (hallId: number): Promise<MemorialHall> => {
    return request.get(`/memorial/halls/${hallId}`)
  },

  // 创建灵堂
  createMemorialHall: (data: MemorialHallCreate): Promise<MemorialHall> => {
    return request.post('/memorial/halls', data)
  },

  // 更新灵堂
  updateMemorialHall: (hallId: number, data: MemorialHallUpdate): Promise<MemorialHall> => {
    return request.put(`/memorial/halls/${hallId}`, data)
  },

  // 删除灵堂
  deleteMemorialHall: (hallId: number): Promise<void> => {
    return request.delete(`/memorial/halls/${hallId}`)
  },

  // 祭拜
  worship: async (hallId: number, data: WorshipRequest): Promise<{ message: string; worship_count: number }> => {
    try {
      console.log('API worship called with hallId:', hallId, 'data:', data)
      const response = await request.post(`/memorial/halls/${hallId}/worship`, data)
      console.log('API worship response:', response)
      return response
    } catch (error) {
      console.error('API worship error:', error)
      throw error
    }
  },

  // 获取祭拜记录
  getWorshipRecords: (hallId: number, params?: { skip?: number; limit?: number }): Promise<WorshipRecord[]> => {
    return request.get(`/memorial/halls/${hallId}/records`, { params })
  },

  // 获取可布置灵堂的逝者列表
  getEligiblePersons: (familyId: number): Promise<PersonBrief[]> => {
    return request.get(`/memorial/eligible-persons/${familyId}`)
  }
}
