<template>
  <div class="memorial-list-page">
    <div class="page-header">
      <h1 class="page-title">祭拜管理</h1>
      <button class="create-btn" @click="handleCreate">
        <svg viewBox="0 0 16 16" fill="none">
          <path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        布置灵堂
      </button>
    </div>
    
    <!-- 家族筛选 -->
    <div class="filter-section">
      <label class="filter-label">选择家族：</label>
      <select v-model="selectedFamily" class="filter-select" @change="fetchHalls">
        <option :value="0">请选择家族</option>
        <option v-for="family in families" :key="family.id" :value="family.id">
          {{ family.name }}
        </option>
      </select>
    </div>
    
    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-else-if="halls.length === 0">
      <div class="empty-icon">🕯️</div>
      <h3>暂无灵堂</h3>
      <p>请先选择家族，然后点击"布置灵堂"为逝者创建灵堂</p>
    </div>
    
    <!-- 灵堂列表 -->
    <div class="halls-grid" v-else>
      <div 
        class="hall-card" 
        v-for="hall in halls" 
        :key="hall.id"
        :class="{ inactive: !hall.is_active }"
        @click="viewHall(hall.id)"
      >
        <!-- 头像区域 -->
        <div class="hall-avatar">
          <img v-if="hall.person.photo_url" :src="hall.person.photo_url" alt="" />
          <div v-else class="avatar-placeholder">
            {{ hall.person.name?.charAt(0) || '故' }}
          </div>
        </div>
        
        <!-- 信息区域 -->
        <div class="hall-info">
          <h3 class="hall-name">{{ hall.person.name }}</h3>
          <p class="hall-date" v-if="hall.person.death_date">
            逝世：{{ hall.person.death_date }}
          </p>
          <span v-if="!hall.is_active" class="inactive-tag">已停用</span>
        </div>
        
        <!-- 统计区域 -->
        <div class="hall-stats">
          <div class="stat-item">
            <span class="stat-icon">🙏</span>
            <span class="stat-value">{{ hall.worship_count }}</span>
            <span class="stat-label">祭拜人次</span>
          </div>
        </div>
        
        <!-- 底部区域 -->
        <div class="hall-footer">
          <span class="creator">布置人：{{ hall.creator.username }}</span>
          <button 
            v-if="hall.is_active"
            class="delete-btn" 
            @click.stop="handleDelete(hall)"
          >删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { memorialApi, type MemorialHallListItem } from '@/api/memorial'
import { familyApi } from '@/api/family'

const router = useRouter()
const halls = ref<MemorialHallListItem[]>([])
const families = ref<{id: number, name: string}[]>([])
const selectedFamily = ref(0)
const loading = ref(false)

// 获取家族列表
const fetchFamilies = async () => {
  try {
    const res = await familyApi.getFamilies()
    families.value = res.items
    if (families.value.length > 0) {
      selectedFamily.value = families.value[0].id
      fetchHalls()
    }
  } catch (error) {
    console.error(error)
  }
}

// 获取灵堂列表
const fetchHalls = async () => {
  if (!selectedFamily.value) {
    halls.value = []
    return
  }
  
  loading.value = true
  try {
    const res = await memorialApi.getMemorialHalls({ 
      family_id: selectedFamily.value 
    })
    halls.value = res.items
  } catch (error) {
    console.error(error)
    alert('获取灵堂列表失败')
  } finally {
    loading.value = false
  }
}

// 创建灵堂
const handleCreate = () => {
  if (!selectedFamily.value) {
    alert('请先选择家族')
    return
  }
  router.push(`/memorial/create?family_id=${selectedFamily.value}`)
}

// 删除灵堂
const handleDelete = async (hall: MemorialHallListItem) => {
  if (!confirm(`确定要删除 ${hall.person.name} 的灵堂吗？`)) return
  
  try {
    await memorialApi.deleteMemorialHall(hall.id)
    alert('删除成功')
    fetchHalls()
  } catch (error: any) {
    alert(error?.response?.data?.detail || '删除失败')
  }
}

// 查看灵堂
const viewHall = (hallId: number) => {
  router.push(`/memorial/${hallId}`)
}

onMounted(() => {
  fetchFamilies()
})
</script>

<style scoped>
.memorial-list-page {
  max-width: 1100px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.page-title {
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.create-btn svg {
  width: 16px;
  height: 16px;
}

.create-btn:hover {
  background: var(--cinnabar-dark);
}

/* 筛选区域 */
.filter-section {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
  padding: var(--space-4);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
}

.filter-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.filter-select {
  flex: 1;
  max-width: 300px;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--text-tertiary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-primary);
  border-top-color: var(--cinnabar);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-16);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.empty-state h3 {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
}

.empty-state p {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

/* 灵堂网格 */
.halls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}

/* 灵堂卡片 */
.hall-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.hall-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.hall-card.inactive {
  opacity: 0.6;
}

/* 头像 */
.hall-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-4);
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid var(--border-primary);
}

.hall-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: white;
  background: var(--ink-black);
}

/* 信息区域 */
.hall-info {
  text-align: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.hall-name {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
}

.hall-date {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

.inactive-tag {
  display: inline-block;
  margin-top: var(--space-2);
  padding: 2px 8px;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

/* 统计 */
.hall-stats {
  text-align: center;
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--border-light);
}

.stat-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
}

.stat-icon {
  font-size: 24px;
  margin-bottom: var(--space-1);
}

.stat-value {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--cinnabar);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* 底部 */
.hall-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-3);
}

.creator {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.delete-btn {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  color: var(--cinnabar);
  background: var(--cinnabar-pale);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.delete-btn:hover {
  background: var(--cinnabar);
  color: white;
}

/* 响应式 */
@media (max-width: 768px) {
  .halls-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filter-select {
    max-width: 100%;
  }
}
</style>