import request from './request'
import type { ListResponse } from '@/types'

// 贡品项
export interface OfferingItem {
  name: string
  icon: string
}

// 创建灵堂请求
export interface MemorialHallCreate {
  person_id: number
  offerings?: OfferingItem[]
}

// 更新灵堂请求
export interface MemorialHallUpdate {
  offerings?: OfferingItem[]
  is_active?: boolean
}

// 人物简要信息
export interface PersonBrief {
  id: number
  name: string
  gender?: string
  birth_date?: string
  death_date?: string
  photo_url?: string
}

// 创建者简要信息
export interface CreatorBrief {
  id: number
  username: string
}

// 灵堂详情
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

// 灵堂列表项
export interface MemorialHallListItem {
  id: number
  person: PersonBrief
  worship_count: number
  is_active: boolean
  creator: CreatorBrief
  created_at: string
}

// 祭拜请求
export interface WorshipRequest {
  worship_type: 'kowtow' | 'incense' | 'offering'
  message?: string
}

// 祭拜记录
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
  worship: (hallId: number, data: WorshipRequest): Promise<{ message: string; worship_count: number }> => {
    return request.post(`/memorial/halls/${hallId}/worship`, data)
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