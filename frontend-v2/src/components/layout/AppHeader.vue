<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Logo区域 -->
      <div class="header-logo" @click="$router.push('/')">
        <div class="logo-icon">
          <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="2"/>
            <path d="M20 8 L20 32 M12 16 L28 16 M12 24 L28 24" stroke="currentColor" stroke-width="1.5"/>
          </svg>
        </div>
        <div class="logo-text">
          <span class="logo-title">寻根族谱</span>
          <span class="logo-subtitle">传承家族记忆</span>
        </div>
      </div>
      
      <!-- 导航菜单 -->
      <nav class="header-nav" v-if="userStore.isLoggedIn">
        <router-link 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-text">{{ item.name }}</span>
        </router-link>
      </nav>
      
      <!-- 用户区域 -->
      <div class="header-user" v-if="userStore.isLoggedIn">
        <div class="user-info" @click="showUserMenu = !showUserMenu">
          <div class="user-avatar">
            <span>{{ userStore.username.charAt(0).toUpperCase() }}</span>
          </div>
          <span class="user-name">{{ userStore.username }}</span>
          <svg class="arrow-icon" :class="{ rotated: showUserMenu }" viewBox="0 0 12 12" fill="none">
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        
        <Transition name="dropdown">
          <div class="user-menu" v-if="showUserMenu" @click.stop>
            <router-link to="/profile" class="menu-item" @click="showUserMenu = false">
              <svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="6" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M2 14c0-3 2.5-5 6-5s6 2 6 5" stroke="currentColor" stroke-width="1.5"/></svg>
              <span>个人资料</span>
            </router-link>
            <router-link to="/users" class="menu-item" v-if="userStore.isSuperuser" @click="showUserMenu = false">
              <svg viewBox="0 0 16 16" fill="none"><circle cx="5" cy="6" r="2.5" stroke="currentColor" stroke-width="1.5"/><circle cx="11" cy="6" r="2.5" stroke="currentColor" stroke-width="1.5"/><path d="M1 13c0-2 1.5-3.5 4-3.5M15 13c0-2-1.5-3.5-4-3.5" stroke="currentColor" stroke-width="1.5"/></svg>
              <span>用户管理</span>
            </router-link>
            <div class="menu-divider"></div>
            <button class="menu-item logout" @click="handleLogout">
              <svg viewBox="0 0 16 16" fill="none"><path d="M6 14H3a1 1 0 01-1-1V3a1 1 0 011-1h3M11 11l3-3-3-3M14 8H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <span>退出登录</span>
            </button>
          </div>
        </Transition>
      </div>
      
      <!-- 未登录状态 -->
      <div class="header-auth" v-else>
        <router-link to="/auth/login" class="auth-btn login">登录</router-link>
        <router-link to="/auth/register" class="auth-btn register">注册</router-link>
      </div>
    </div>
    
    <!-- 装饰性底边 -->
    <div class="header-border">
      <svg viewBox="0 0 1200 4" preserveAspectRatio="none">
        <path d="M0 2 Q300 0 600 2 T1200 2" stroke="var(--cinnabar)" stroke-width="1" fill="none" opacity="0.3"/>
      </svg>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const showUserMenu = ref(false)

const navItems = [
  { 
    name: '首页', 
    path: '/',
    icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M2 6l6-4 6 4v8a1 1 0 01-1 1H3a1 1 0 01-1-1V6z" stroke="currentColor" stroke-width="1.5"/></svg>'
  },
  { 
    name: '家族', 
    path: '/families',
    icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="4" r="2.5" stroke="currentColor" stroke-width="1.5"/><circle cx="4" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/><path d="M6 6l-1 2M10 6l1 2" stroke="currentColor" stroke-width="1.5"/></svg>'
  },
  { 
    name: '族谱树', 
    path: '/tree',
    icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="2" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="4" cy="7" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="7" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="2" cy="12" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="6" cy="12" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="12" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="14" cy="12" r="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M8 3.5v2M4 8.5v2M12 8.5v2" stroke="currentColor" stroke-width="1.5"/></svg>'
  },
  { 
    name: '祭拜', 
    path: '/memorial',
    icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M8 2v4M6 6h4l-1 8H7L6 6z" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="4" r="2" stroke="currentColor" stroke-width="1.5"/></svg>'
  }
]

const isActive = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const handleLogout = () => {
  showUserMenu.value = false
  userStore.clearUser()
  router.push('/auth/login')
}

// 点击外部关闭菜单
const handleClickOutside = (event: MouseEvent) => {
  if (showUserMenu.value) {
    // 检查点击是否在用户菜单区域内
    const target = event.target as HTMLElement
    const userMenu = document.querySelector('.user-menu')
    const userInfo = document.querySelector('.user-info')
    if (userMenu && !userMenu.contains(target) && userInfo && !userInfo.contains(target)) {
      showUserMenu.value = false
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: var(--bg-primary);
  z-index: var(--z-fixed);
  box-shadow: var(--shadow-sm);
}

.header-inner {
  max-width: var(--content-max-width);
  height: 100%;
  margin: 0 auto;
  padding: 0 var(--space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo */
.header-logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.header-logo:hover {
  opacity: 0.8;
}

.logo-icon {
  width: 36px;
  height: 36px;
  color: var(--cinnabar);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--ink-black);
  letter-spacing: 0.1em;
}

.logo-subtitle {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  letter-spacing: 0.05em;
}

/* 导航 */
.header-nav {
  display: flex;
  gap: var(--space-1);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  position: relative;
}

.nav-item:hover {
  color: var(--color-primary);
  background: var(--color-primary-pale);
}

.nav-item.active {
  color: var(--color-primary);
  background: var(--color-primary-pale);
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: var(--cinnabar);
  border-radius: var(--radius-full);
}

.nav-icon {
  width: 16px;
  height: 16px;
}

.nav-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

/* 用户区域 */
.header-user {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: var(--bg-secondary);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--cinnabar) 0%, var(--cinnabar-light) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
}

.user-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-medium);
}

.arrow-icon {
  width: 12px;
  height: 12px;
  color: var(--text-tertiary);
  transition: transform var(--transition-fast);
}

.arrow-icon.rotated {
  transform: rotate(180deg);
}

/* 用户菜单 */
.user-menu {
  position: absolute;
  top: calc(100% + var(--space-2));
  right: 0;
  min-width: 180px;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: var(--space-2);
  z-index: var(--z-dropdown);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-3);
  color: var(--text-primary);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  cursor: pointer;
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  text-decoration: none;
}

.menu-item:hover {
  background: var(--bg-secondary);
  color: var(--color-primary);
}

.menu-item svg {
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
}

.menu-item:hover svg {
  color: var(--color-primary);
}

.menu-item.logout {
  color: var(--cinnabar);
}

.menu-item.logout svg {
  color: var(--cinnabar);
}

.menu-divider {
  height: 1px;
  background: var(--border-primary);
  margin: var(--space-2) 0;
}

/* 未登录 */
.header-auth {
  display: flex;
  gap: var(--space-3);
}

.auth-btn {
  padding: var(--space-2) var(--space-5);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.auth-btn.login {
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.auth-btn.login:hover {
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.auth-btn.register {
  background: var(--cinnabar);
  color: white;
}

.auth-btn.register:hover {
  background: var(--cinnabar-dark);
}

/* 底边装饰 */
.header-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  overflow: hidden;
}

.header-border svg {
  width: 100%;
  height: 100%;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all var(--transition-fast);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 响应式 */
@media (max-width: 768px) {
  .header-nav {
    display: none;
  }
  
  .logo-subtitle {
    display: none;
  }
  
  .user-name {
    display: none;
  }
}
</style>