import request from './request'
import type { Token, User, UserRegister, UserLogin } from '@/types'

export const authApi = {
  // 登录
  login: (data: UserLogin): Promise<Token> => {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    return request.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 注册
  register: (data: UserRegister): Promise<User> => {
    return request.post('/auth/register', data)
  },

  // 获取当前用户信息
  getCurrentUser: (): Promise<User> => {
    return request.get('/auth/me')
  },

  // 更新用户信息
  updateUser: (data: { email?: string; phone?: string }): Promise<User> => {
    return request.put('/auth/me', data)
  },

  // 修改密码
  changePassword: (data: { current_password: string; new_password: string }): Promise<{ message: string }> => {
    return request.put('/auth/password', data)
  },

  // 上传头像
  uploadAvatar: (file: File): Promise<{ avatar_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/auth/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}