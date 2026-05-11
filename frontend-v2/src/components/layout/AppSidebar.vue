<template>
  <aside class="app-sidebar" :class="{ collapsed: isCollapsed }">
    <!-- 折叠按钮 -->
    <button class="collapse-btn" @click="toggleCollapse">
      <svg viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    
    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <div class="nav-section" v-for="section in menuSections" :key="section.title">
        <div class="section-title" v-if="!isCollapsed">{{ section.title }}</div>
        <router-link
          v-for="item in section.items"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: isActive(item.path) }"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-text" v-if="!isCollapsed">{{ item.name }}</span>
          <span class="nav-badge" v-if="item.badge && !isCollapsed">{{ item.badge }}</span>
        </router-link>
      </div>
    </nav>
    
    <!-- 底部装饰 -->
    <div class="sidebar-footer" v-if="!isCollapsed">
      <div class="decoration">
        <svg viewBox="0 0 100 20" fill="none">
          <path d="M0 10 Q25 0 50 10 T100 10" stroke="var(--cinnabar)" stroke-width="1" fill="none" opacity="0.3"/>
        </svg>
      </div>
      <p class="copyright">寻根族谱 v2.0</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

interface MenuItem {
  name: string
  path: string
  icon: string
  badge?: string | number
}

interface MenuSection {
  title: string
  items: MenuItem[]
}

const route = useRoute()
const userStore = useUserStore()
const isCollapsed = ref(false)

const emit = defineEmits(['toggle'])

const menuSections = computed<MenuSection[]>(() => {
  const sections: MenuSection[] = [
    {
      title: '导航',
      items: [
        { 
          name: '首页', 
          path: '/',
          icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M2 6l6-4 6 4v8a1 1 0 01-1 1H3a1 1 0 01-1-1V6z" stroke="currentColor" stroke-width="1.5"/><path d="M6 14V9h4v5" stroke="currentColor" stroke-width="1.5"/></svg>'
        },
        { 
          name: '家族管理', 
          path: '/families',
          icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="4" r="2.5" stroke="currentColor" stroke-width="1.5"/><circle cx="4" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/><path d="M6 6l-1 2M10 6l1 2" stroke="currentColor" stroke-width="1.5"/></svg>'
        },
        { 
          name: '族谱树', 
          path: '/tree',
          icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="2" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="4" cy="6" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="6" r="1.5" stroke="currentColor" stroke-width="1.5"/><circle cx="2" cy="11" r="1" stroke="currentColor" stroke-width="1.5"/><circle cx="6" cy="11" r="1" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="11" r="1" stroke="currentColor" stroke-width="1.5"/><circle cx="14" cy="11" r="1" stroke="currentColor" stroke-width="1.5"/><path d="M8 3.5v1M4 7.5V9M12 7.5V9" stroke="currentColor" stroke-width="1.5"/></svg>'
        },
        { 
          name: '祭拜', 
          path: '/memorial',
          icon: '<svg viewBox="0 0 16 16" fill="none"><path d="M8 2v4M6 6h4l-1 8H7L6 6z" stroke="currentColor" stroke-width="1.5"/><path d="M5 4h6" stroke="currentColor" stroke-width="1.5"/></svg>'
        }
      ]
    }
  ]
  
  // 管理员菜单
  if (userStore.isSuperuser) {
    sections.push({
      title: '系统管理',
      items: [
        { 
          name: '用户管理', 
          path: '/users',
          icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="5" cy="6" r="2.5" stroke="currentColor" stroke-width="1.5"/><circle cx="11" cy="6" r="2.5" stroke="currentColor" stroke-width="1.5"/><path d="M1 14c0-2 1.5-3.5 4-3.5M15 14c0-2-1.5-3.5-4-3.5" stroke="currentColor" stroke-width="1.5"/></svg>'
        },
        { 
          name: '系统设置', 
          path: '/admin',
          icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.5 1.5M11.5 11.5L13 13M3 13l1.5-1.5M11.5 4.5L13 3" stroke="currentColor" stroke-width="1.5"/></svg>'
        }
      ]
    })
  }
  
  return sections
})

const isActive = (path: string) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  emit('toggle', isCollapsed.value)
}
</script>

<style scoped>
.app-sidebar {
  position: fixed;
  top: var(--header-height);
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--bg-primary);
  border-right: 1px solid var(--border-primary);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  z-index: var(--z-sticky);
}

.app-sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

/* 折叠按钮 */
.collapse-btn {
  position: absolute;
  top: var(--space-4);
  right: -12px;
  width: 24px;
  height: 24px;
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  z-index: 1;
}

.collapse-btn:hover {
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.collapse-btn svg {
  width: 12px;
  height: 12px;
  transition: transform var(--transition-fast);
}

.collapsed .collapse-btn svg {
  transform: rotate(180deg);
}

/* 导航 */
.sidebar-nav {
  flex: 1;
  padding: var(--space-6) var(--space-3);
  overflow-y: auto;
}

.nav-section {
  margin-bottom: var(--space-6);
}

.section-title {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-2);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-1);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.nav-link:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.nav-link.active {
  background: var(--color-primary-pale);
  color: var(--cinnabar);
  font-weight: var(--font-medium);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-badge {
  padding: 2px 6px;
  font-size: var(--text-xs);
  background: var(--cinnabar);
  color: white;
  border-radius: var(--radius-full);
}

/* 折叠状态 */
.collapsed .nav-link {
  justify-content: center;
  padding: var(--space-3);
}

.collapsed .section-title {
  display: none;
}

/* 底部 */
.sidebar-footer {
  padding: var(--space-4);
  border-top: 1px solid var(--border-primary);
}

.decoration {
  margin-bottom: var(--space-2);
}

.decoration svg {
  width: 100%;
  height: 20px;
}

.copyright {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  text-align: center;
}

/* 响应式 */
@media (max-width: 1024px) {
  .app-sidebar {
    width: var(--sidebar-collapsed-width);
  }
  
  .app-sidebar .nav-text,
  .app-sidebar .section-title,
  .app-sidebar .nav-badge,
  .app-sidebar .sidebar-footer {
    display: none;
  }
  
  .app-sidebar .nav-link {
    justify-content: center;
  }
  
  .collapse-btn {
    display: none;
  }
}
</style>