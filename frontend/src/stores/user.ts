import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, UserLogin, UserRegister } from '@/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isLoggedIn = computed(() => !!token.value)
  const isSuperuser = computed(() => user.value?.is_superuser || false)

  const login = async (credentials: UserLogin) => {
    const res = await authApi.login(credentials)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await fetchUser()
  }

  const register = async (data: UserRegister) => {
    await authApi.register(data)
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const fetchUser = async () => {
    if (!token.value) return
    try {
      user.value = await authApi.getCurrentUser()
    } catch {
      logout()
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isSuperuser,
    login,
    register,
    logout,
    fetchUser
  }
})