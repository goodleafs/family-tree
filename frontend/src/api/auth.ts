import request from './request'
import type { User, UserLogin, UserRegister, Token } from '@/types'

export const authApi = {
  register: (data: UserRegister): Promise<User> => {
    return request.post('/auth/register', data)
  },

  login: (data: UserLogin): Promise<Token> => {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)
    
    return request.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  getCurrentUser: (): Promise<User> => {
    return request.get('/auth/me')
  },

  updateUser: (data: Partial<User>): Promise<User> => {
    return request.put('/auth/me', data)
  },

  changePassword: (data: { current_password: string; new_password: string }): Promise<{ message: string }> => {
    return request.put('/auth/password', data)
  },

  uploadAvatar: (file: File): Promise<{ avatar_url: string }> => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/auth/avatar', formData)
  }



  // // 获取当前用户信息
  // getMe: (): Promise<User> => {
  //   return request.get('/auth/me')
  // },

  // // 更新用户信息
  // updateMe: (data: Partial<User>): Promise<User> => {
  //   return request.put('/auth/me', data)
  // },

  // // 上传头像
  // uploadAvatar: (file: File): Promise<{ avatar_url: string }> => {
  //   const formData = new FormData()
  //   formData.append('file', file)
  //   return request.post('/auth/me/avatar', formData, {
  //     headers: {
  //       'Content-Type': 'multipart/form-data'
  //     }
  //   })
  // }
}
