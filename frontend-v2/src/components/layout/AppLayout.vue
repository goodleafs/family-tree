<template>
  <div class="app-layout" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <AppHeader />
    <AppSidebar v-if="userStore.isLoggedIn" @toggle="handleSidebarToggle" />
    
    <main class="app-main">
      <div class="main-content">
        <router-view v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </div>
    </main>
    
    <!-- 背景装饰 -->
    <div class="bg-decoration" v-if="showDecoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

const route = useRoute()
const userStore = useUserStore()
const sidebarCollapsed = ref(false)

const showDecoration = computed(() => {
  // 在某些页面显示背景装饰
  return ['Dashboard', 'Login', 'Register'].includes(route.name as string)
})

const handleSidebarToggle = (collapsed: boolean) => {
  sidebarCollapsed.value = collapsed
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: var(--bg-primary);
}

/* 主内容区 */
.app-main {
  padding-top: var(--header-height);
  padding-left: var(--sidebar-width);
  min-height: 100vh;
  transition: padding-left var(--transition-normal);
}

.app-layout.sidebar-collapsed .app-main {
  padding-left: var(--sidebar-collapsed-width);
}

/* 未登录状态 */
.app-layout:not(:has(.app-sidebar)) .app-main {
  padding-left: 0;
}

.main-content {
  padding: var(--space-6);
  max-width: var(--content-max-width);
  margin: 0 auto;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: -1;
  overflow: hidden;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.03;
}

.circle-1 {
  width: 600px;
  height: 600px;
  background: var(--cinnabar);
  top: -200px;
  right: -200px;
}

.circle-2 {
  width: 400px;
  height: 400px;
  background: var(--indigo);
  bottom: -100px;
  left: -100px;
}

.circle-3 {
  width: 300px;
  height: 300px;
  background: var(--bamboo);
  top: 50%;
  left: 30%;
  transform: translateY(-50%);
}

/* 页面切换动画 */
.page-enter-active,
.page-leave-active {
  transition: all 0.25s ease-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 响应式 */
@media (max-width: 1024px) {
  .app-main {
    padding-left: var(--sidebar-collapsed-width);
  }
  
  .app-layout.sidebar-collapsed .app-main {
    padding-left: var(--sidebar-collapsed-width);
  }
}

@media (max-width: 768px) {
  .app-main {
    padding-left: 0;
  }
  
  .main-content {
    padding: var(--space-4);
  }
}
</style>