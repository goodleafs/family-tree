<template>
  <AppLayout>
    <router-view />
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import AppLayout from '@/components/layout/AppLayout.vue'

const userStore = useUserStore()

onMounted(() => {
  // 应用启动时尝试获取用户信息
  const token = localStorage.getItem('token')
  if (token) {
    userStore.fetchUser()
  }
})
</script>

<style>
@import '@/styles/main.css';
</style>