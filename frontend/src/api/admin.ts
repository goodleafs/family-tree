import request from './request'
import type { User, ListResponse } from '@/types'

export const adminApi = {
  getUsers: async (params?: { skip?: number; limit?: number; search?: string }): Promise<ListResponse<User>> => {
    const response = await request.get('/admin/users', { params })
    return response
  },

  toggleSuperuser: async (userId: number, isSuperuser: boolean): Promise<User> => {
    const response = await request.put(`/admin/users/${userId}/superuser`, null, {
      params: { is_superuser: isSuperuser }
    })
    return response
  },

  getUser: async (userId: number): Promise<User> => {
    const response = await request.get(`/admin/users/${userId}`)
    return response
  },

  updateUser: async (userId: number, data: Partial<User>): Promise<User> => {
    const response = await request.put(`/admin/users/${userId}`, data)
    return response
  },

  resetUserPassword: async (userId: number, newPassword: string): Promise<void> => {
    await request.post(`/admin/users/${userId}/reset-password`, {
      new_password: newPassword
    })
  }
}