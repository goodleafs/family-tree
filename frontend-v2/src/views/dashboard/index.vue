<template>
  <div class="dashboard-page">
    <!-- 欢迎区域 -->
    <section class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1 class="welcome-title">
            <span class="greeting">{{ greeting }}</span>
            <span class="username">{{ userStore.username }}</span>
          </h1>
          <p class="welcome-desc">欢迎回到寻根族谱，记录家族历史，传承血脉亲情</p>
        </div>
        <div class="welcome-actions">
          <router-link to="/families" class="action-btn primary">
            <svg viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="4" r="2.5" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="4" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="12" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/>
              <path d="M6 6l-1 2M10 6l1 2" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            <span>我的家族</span>
          </router-link>
          <router-link to="/tree" class="action-btn secondary">
            <svg viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="2" r="1.5" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="4" cy="6" r="1.5" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="12" cy="6" r="1.5" stroke="currentColor" stroke-width="1.5"/>
              <path d="M8 3.5v1M4 7.5V9M12 7.5V9" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            <span>族谱树</span>
          </router-link>
        </div>
      </div>
      
      <!-- 装饰性水墨元素 -->
      <div class="ink-decoration">
        <svg viewBox="0 0 400 200" fill="none">
          <path d="M0 100 Q100 50 200 100 T400 100" stroke="var(--cinnabar)" stroke-width="1" fill="none" opacity="0.1"/>
          <path d="M0 120 Q100 70 200 120 T400 120" stroke="var(--indigo)" stroke-width="1" fill="none" opacity="0.08"/>
        </svg>
      </div>
    </section>
    
    <!-- 统计卡片 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card" v-for="stat in stats" :key="stat.label">
          <div class="stat-icon" :style="{ background: stat.color }">
            <span v-html="stat.icon"></span>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 我的家族 -->
    <section class="families-section">
      <div class="section-header">
        <h2 class="section-title">我的家族</h2>
        <router-link to="/families" class="view-all">
          查看全部
          <svg viewBox="0 0 16 16" fill="none">
            <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.5"/>
          </svg>
        </router-link>
      </div>
      
      <div class="families-grid" v-if="families.length > 0">
        <div 
          class="family-card" 
          v-for="family in families.slice(0, 4)" 
          :key="family.id"
          @click="$router.push(`/families/${family.id}`)"
        >
          <div class="family-header">
            <span class="family-name">{{ family.name }}</span>
            <span class="family-surname" v-if="family.surname">{{ family.surname }}氏</span>
          </div>
          <p class="family-desc">{{ family.description || '暂无简介' }}</p>
          <div class="family-meta">
            <span class="meta-item">
              <svg viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/>
                <path d="M2 14c0-2.5 2.5-4.5 6-4.5s6 2 6 4.5" stroke="currentColor" stroke-width="1.5"/>
              </svg>
              {{ family.person_count || 0 }} 人
            </span>
            <span class="meta-item" :class="{ public: family.is_public }">
              {{ family.is_public ? '公开' : '私密' }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="empty-state" v-else>
        <div class="empty-icon">
          <svg viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="20" r="8" stroke="currentColor" stroke-width="2"/>
            <circle cx="18" cy="40" r="6" stroke="currentColor" stroke-width="2"/>
            <circle cx="46" cy="40" r="6" stroke="currentColor" stroke-width="2"/>
            <path d="M26 24l-5 10M38 24l5 10" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <p class="empty-text">还没有创建家族</p>
        <router-link to="/families" class="create-btn">创建第一个家族</router-link>
      </div>
    </section>
    
    <!-- 功能介绍 -->
    <section class="features-section">
      <h2 class="section-title center">功能特色</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <div class="feature-icon" v-html="feature.icon"></div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.desc }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { familyApi } from '@/api/family'
import type { Family } from '@/types'

const userStore = useUserStore()
const families = ref<Family[]>([])

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了，'
  if (hour < 12) return '早上好，'
  if (hour < 18) return '下午好，'
  return '晚上好，'
})

const stats = computed(() => [
  {
    label: '家族数量',
    value: families.value.length,
    icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="4" r="2.5" stroke="currentColor" stroke-width="1.5"/><circle cx="4" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/><path d="M6 6l-1 2M10 6l1 2" stroke="currentColor" stroke-width="1.5"/></svg>',
    color: 'linear-gradient(135deg, var(--cinnabar) 0%, var(--cinnabar-light) 100%)'
  },
  {
    label: '成员总数',
    value: families.value.reduce((sum, f) => sum + (f.person_count || 0), 0),
    icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M2 14c0-2.5 2.5-4.5 6-4.5s6 2 6 4.5" stroke="currentColor" stroke-width="1.5"/></svg>',
    color: 'linear-gradient(135deg, var(--indigo) 0%, var(--indigo-light) 100%)'
  },
  {
    label: '公开家族',
    value: families.value.filter(f => f.is_public).length,
    icon: '<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/></svg>',
    color: 'linear-gradient(135deg, var(--bamboo) 0%, var(--bamboo-light) 100%)'
  }
])

const features = [
  {
    title: '家族管理',
    desc: '创建多个家族，管理家族信息、成员关系',
    icon: '<svg viewBox="0 0 32 32" fill="none"><circle cx="16" cy="8" r="5" stroke="currentColor" stroke-width="2"/><circle cx="8" cy="22" r="4" stroke="currentColor" stroke-width="2"/><circle cx="24" cy="22" r="4" stroke="currentColor" stroke-width="2"/><path d="M12 12l-3 6M20 12l3 6" stroke="currentColor" stroke-width="2"/></svg>'
  },
  {
    title: '族谱可视化',
    desc: '交互式族谱树展示，多代展开收起',
    icon: '<svg viewBox="0 0 32 32" fill="none"><circle cx="16" cy="4" r="3" stroke="currentColor" stroke-width="2"/><circle cx="8" cy="12" r="3" stroke="currentColor" stroke-width="2"/><circle cx="24" cy="12" r="3" stroke="currentColor" stroke-width="2"/><circle cx="4" cy="22" r="2" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="22" r="2" stroke="currentColor" stroke-width="2"/><circle cx="20" cy="22" r="2" stroke="currentColor" stroke-width="2"/><circle cx="28" cy="22" r="2" stroke="currentColor" stroke-width="2"/><path d="M16 7v2M8 15v5M24 15v5" stroke="currentColor" stroke-width="2"/></svg>'
  },
  {
    title: '在线祭拜',
    desc: '虚拟祭品供奉，追思留言悼念',
    icon: '<svg viewBox="0 0 32 32" fill="none"><path d="M16 4v8M12 12h8l-2 16h-4l-2-16z" stroke="currentColor" stroke-width="2"/><path d="M10 8h12" stroke="currentColor" stroke-width="2"/></svg>'
  },
  {
    title: '数据导出',
    desc: 'PDF族谱导出，Excel批量导入',
    icon: '<svg viewBox="0 0 32 32" fill="none"><path d="M8 4h12l6 6v18a2 2 0 01-2 2H8a2 2 0 01-2-2V6a2 2 0 012-2z" stroke="currentColor" stroke-width="2"/><path d="M20 4v6h6" stroke="currentColor" stroke-width="2"/></svg>'
  }
]

onMounted(async () => {
  try {
    const res = await familyApi.getFamilies({ limit: 10 })
    families.value = res.items
  } catch (error) {
    console.error(error)
  }
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
}

/* 欢迎区域 */
.welcome-section {
  position: relative;
  padding: var(--space-8);
  margin-bottom: var(--space-8);
  background: linear-gradient(135deg, var(--paper-cream) 0%, var(--paper-white) 100%);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-primary);
  overflow: hidden;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-family: var(--font-title);
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
  letter-spacing: 0.05em;
}

.greeting {
  color: var(--text-secondary);
}

.username {
  color: var(--cinnabar);
}

.welcome-desc {
  font-size: var(--text-base);
  color: var(--text-tertiary);
  margin: 0;
}

.welcome-actions {
  display: flex;
  gap: var(--space-3);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn.primary {
  background: var(--cinnabar);
  color: white;
}

.action-btn.primary:hover {
  background: var(--cinnabar-dark);
}

.action-btn.secondary {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.action-btn.secondary:hover {
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.ink-decoration {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 50%;
  height: 100%;
  pointer-events: none;
}

.ink-decoration svg {
  width: 100%;
  height: 100%;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: var(--space-8);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--border-secondary);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

/* 家族区域 */
.families-section {
  margin-bottom: var(--space-8);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.section-title {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0;
  letter-spacing: 0.05em;
}

.section-title.center {
  text-align: center;
  width: 100%;
}

.view-all {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--cinnabar);
  text-decoration: none;
}

.view-all svg {
  width: 14px;
  height: 14px;
}

.view-all:hover {
  text-decoration: underline;
}

.families-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

.family-card {
  padding: var(--space-5);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.family-card:hover {
  border-color: var(--cinnabar);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.family-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.family-name {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.family-surname {
  font-size: var(--text-xs);
  padding: 2px 6px;
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
  border-radius: var(--radius-sm);
}

.family-desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0 0 var(--space-3);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.family-meta {
  display: flex;
  gap: var(--space-4);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

.meta-item.public {
  color: var(--bamboo);
}

/* 空状态 */
.empty-state {
  padding: var(--space-12);
  text-align: center;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px dashed var(--border-primary);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-4);
  color: var(--text-tertiary);
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-text {
  font-size: var(--text-base);
  color: var(--text-tertiary);
  margin: 0 0 var(--space-4);
}

.create-btn {
  display: inline-block;
  padding: var(--space-2) var(--space-5);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: white;
  background: var(--cinnabar);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: background var(--transition-fast);
}

.create-btn:hover {
  background: var(--cinnabar-dark);
}

/* 功能特色 */
.features-section {
  padding: var(--space-6);
  background: var(--bg-secondary);
  border-radius: var(--radius-xl);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-top: var(--space-6);
}

.feature-card {
  padding: var(--space-5);
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  text-align: center;
  transition: all var(--transition-fast);
}

.feature-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--space-3);
  color: var(--cinnabar);
}

.feature-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

.feature-title {
  font-family: var(--font-title);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
}

.feature-desc {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
  line-height: var(--leading-relaxed);
}

/* 响应式 */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .welcome-content {
    flex-direction: column;
    text-align: center;
    gap: var(--space-4);
  }
  
  .welcome-actions {
    width: 100%;
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .families-grid {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>