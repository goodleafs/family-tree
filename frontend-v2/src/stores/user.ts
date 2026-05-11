import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value)
  const isSuperuser = computed(() => user.value?.is_superuser || false)
  const username = computed(() => user.value?.username || '')

  const fetchUser = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      user.value = null
      return
    }

    loading.value = true
    try {
      user.value = await authApi.getCurrentUser()
    } catch (error) {
      user.value = null
      localStorage.removeItem('token')
    } finally {
      loading.value = false
    }
  }

  const setUser = (userData: User | null) => {
    user.value = userData
  }

  const clearUser = () => {
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    loading,
    isLoggedIn,
    isSuperuser,
    username,
    fetchUser,
    setUser,
    clearUser
  }
})