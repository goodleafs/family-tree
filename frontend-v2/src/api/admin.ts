import request from './request'
import type { User, ListResponse } from '@/types'

export const adminApi = {
  // 获取用户列表
  getUsers: (params?: { skip?: number; limit?: number; search?: string }): Promise<ListResponse<User>> => {
    return request.get('/admin/users', { params })
  },

  // 获取单个用户
  getUser: (userId: number): Promise<User> => {
    return request.get(`/admin/users/${userId}`)
  },

  // 更新用户信息
  updateUser: (userId: number, data: { email?: string; phone?: string; is_active?: boolean; is_superuser?: boolean }): Promise<User> => {
    return request.put(`/admin/users/${userId}`, data)
  },

  // 切换超级管理员权限
  toggleSuperuser: (userId: number, isSuperuser: boolean): Promise<User> => {
    return request.put(`/admin/users/${userId}/superuser`, null, {
      params: { is_superuser: isSuperuser }
    })
  },

  // 重置用户密码
  resetUserPassword: (userId: number, newPassword: string): Promise<void> => {
    return request.post(`/admin/users/${userId}/reset-password`, {
      new_password: newPassword
    })
  },

  // 删除用户
  deleteUser: (userId: number): Promise<void> => {
    return request.delete(`/admin/users/${userId}`)
  }
}