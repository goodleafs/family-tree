<template>
  <div class="memorial-hall-page" v-if="hall">
    <!-- 页面头部 -->
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/memorial')">
        <svg viewBox="0 0 16 16" fill="none">
          <path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        返回
      </button>
      <h1 class="page-title">{{ hall.person.name }}的灵堂</h1>
    </div>
    
    <!-- 灵堂主体 -->
    <div class="hall-content">
      <!-- 祭坛区域 -->
      <div class="altar-section">
        <div class="altar-card">
          <div class="altar">
            <!-- 牌位 -->
            <div class="memorial-tablet">
              <div class="tablet-frame">
                <div class="tablet-content">
                  <p class="tablet-title">故显考</p>
                  <h2 class="tablet-name">{{ hall.person.name }}</h2>
                  <p class="tablet-dates" v-if="hall.person.birth_date || hall.person.death_date">
                    {{ hall.person.birth_date || '?' }} ~ {{ hall.person.death_date || '?' }}
                  </p>
                  <p class="tablet-lunar" v-if="hall.person.birth_date || hall.person.death_date">
                    农历: {{ hall.person.birth_date ? toLunarYearWithDate(hall.person.birth_date) : '?' }} ~ {{ hall.person.death_date ? toLunarYearWithDate(hall.person.death_date) : '?' }}
                  </p>
                  <p class="tablet-honor">英灵永存</p>
                </div>
              </div>
            </div>
            
            <!-- 贡品台 -->
            <div class="offering-table" v-if="hall.offerings.length > 0">
              <div 
                v-for="(offering, index) in hall.offerings" 
                :key="index"
                class="offering-item"
              >
                <span class="offering-icon">{{ offering.icon }}</span>
                <span class="offering-name">{{ offering.name }}</span>
              </div>
            </div>
            
            <!-- 香火 -->
            <div class="incense-burner">
              <div class="burner">
                <div class="incense-sticks">
                  <div class="stick" v-for="n in Math.min(hall.incense_count, 5)" :key="n"></div>
                </div>
                <span class="incense-count">香火：{{ hall.incense_count }}</span>
              </div>
            </div>
            
            <!-- 统计 -->
            <div class="worship-stats">
              <span class="stats-value">{{ hall.worship_count }}</span>
              <span class="stats-label">人祭拜</span>
            </div>
            
            <!-- 布置人 -->
            <div class="creator-info">
              <span>灵堂布置：{{ hall.creator.username }}</span>
              <span v-if="!hall.is_active" class="inactive-badge">已停用</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 祭拜操作区 -->
      <div class="worship-section">
        <div class="worship-card">
          <h3 class="section-title">祭拜祈福</h3>
          
          <div class="action-buttons">
            <button 
              class="worship-btn kowtow"
              :disabled="!hall.is_active || worshipLoading"
              @click="handleWorship('kowtow')"
            >
              <span class="btn-icon">🙏</span>
              <span>叩拜</span>
            </button>
            
            <button 
              class="worship-btn incense"
              :disabled="!hall.is_active || worshipLoading"
              @click="handleWorship('incense')"
            >
              <span class="btn-icon">🕯️</span>
              <span>上香</span>
            </button>
          </div>
          
          <!-- 贡品选择 -->
          <div class="offering-section">
            <p class="section-subtitle">选择贡品</p>
            <div class="offering-options">
              <button
                v-for="opt in offeringOptions"
                :key="opt.name"
                class="offering-btn"
                :class="{ selected: selectedOfferings.includes(opt.name) }"
                @click="toggleOffering(opt.name)"
              >
                {{ opt.icon }} {{ opt.name }}
              </button>
            </div>
            
            <button 
              class="offering-submit"
              :disabled="!hall.is_active || worshipLoading || selectedOfferings.length === 0"
              @click="handleWorship('offering')"
            >
              <span class="btn-icon">🎁</span>
              献贡
            </button>
          </div>
        </div>
      </div>
      
      <!-- 祭拜记录 -->
      <div class="records-section">
        <div class="records-card">
          <h3 class="section-title">祭拜记录</h3>
          
          <div class="records-empty" v-if="records.length === 0">
            <p>暂无祭拜记录</p>
          </div>
          
          <div class="records-list" v-else>
            <div class="record-item" v-for="record in records" :key="record.id">
              <div class="record-time">{{ formatDate(record.created_at) }}</div>
              <div class="record-content">
                <span class="record-type" :class="record.worship_type">
                  {{ getWorshipTypeText(record.worship_type) }}
                </span>
                <span v-if="record.username" class="record-user">{{ record.username }}</span>
              </div>
              <p v-if="record.message" class="record-message">{{ record.message }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 加载状态 -->
  <div class="loading-state" v-else-if="loading">
    <div class="loading-spinner"></div>
    <p>加载中...</p>
  </div>
  
  <!-- 错误状态 -->
  <div class="error-state" v-else>
    <div class="error-icon">⚠️</div>
    <h2>灵堂不存在</h2>
    <button class="back-btn" @click="$router.push('/memorial')">返回列表</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { memorialApi, type MemorialHall, type WorshipRecord } from '@/api/memorial'
import { toLunarYearWithDate } from '@/utils/lunar'

const route = useRoute()
const router = useRouter()
const hallId = parseInt(route.params.id as string)

const hall = ref<MemorialHall | null>(null)
const records = ref<WorshipRecord[]>([])
const loading = ref(true)
const worshipLoading = ref(false)
const selectedOfferings = ref<string[]>([])

// 贡品选项
const offeringOptions = [
  { name: '鲜花', icon: '🌸' },
  { name: '水果', icon: '🍎' },
  { name: '糕点', icon: '🥮' },
  { name: '酒水', icon: '🍶' },
  { name: '香烛', icon: '🕯️' },
  { name: '纸钱', icon: '💴' }
]

// 获取灵堂详情
const fetchHall = async () => {
  loading.value = true
  try {
    hall.value = await memorialApi.getMemorialHall(hallId)
    fetchRecords()
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 获取祭拜记录
const fetchRecords = async () => {
  try {
    records.value = await memorialApi.getWorshipRecords(hallId, { limit: 10 })
  } catch (error) {
    console.error(error)
  }
}

// 祭拜操作
const handleWorship = async (type: 'kowtow' | 'incense' | 'offering') => {
  if (!hall.value?.is_active) {
    alert('该灵堂已停用')
    return
  }
  
  worshipLoading.value = true
  try {
    const res = await memorialApi.worship(hallId, {
      worship_type: type,
      message: type === 'offering' ? selectedOfferings.value.join('、') : undefined
    })
    
    if (hall.value) {
      hall.value.worship_count = res.worship_count
      if (type === 'incense') {
        hall.value.incense_count += 1
      }
    }
    
    alert('祭拜成功')
    if (type === 'offering') {
      selectedOfferings.value = []
    }
    fetchRecords()
  } catch (error: any) {
    alert(error?.response?.data?.detail || '祭拜失败')
  } finally {
    worshipLoading.value = false
  }
}

// 切换贡品选择
const toggleOffering = (name: string) => {
  const index = selectedOfferings.value.indexOf(name)
  if (index > -1) {
    selectedOfferings.value.splice(index, 1)
  } else {
    selectedOfferings.value.push(name)
  }
}

// 获取祭拜类型文本
const getWorshipTypeText = (type: string) => {
  const map: Record<string, string> = {
    kowtow: '叩拜',
    incense: '上香',
    offering: '献贡'
  }
  return map[type] || type
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  if (isNaN(hallId)) {
    router.push('/memorial')
    return
  }
  fetchHall()
})
</script>

<style scoped>
.memorial-hall-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: none;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.back-btn svg {
  width: 14px;
  height: 14px;
}

.back-btn:hover {
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.page-title {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

/* 灵堂内容 */
.hall-content {
  display: grid;
  gap: var(--space-6);
}

/* 祭坛区域 */
.altar-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.altar {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-10) var(--space-6);
  color: white;
}

/* 牌位 */
.memorial-tablet {
  margin-bottom: var(--space-6);
}

.tablet-frame {
  background: linear-gradient(145deg, #8b4513, #a0522d);
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.tablet-content {
  background: #f5f5dc;
  color: #333;
  padding: var(--space-6) var(--space-10);
  text-align: center;
  border-radius: 4px;
  min-width: 200px;
}

.tablet-title {
  margin: 0 0 var(--space-2);
  font-size: var(--text-base);
  color: #666;
}

.tablet-name {
  margin: 0 0 var(--space-3);
  font-family: var(--font-title);
  font-size: 32px;
  color: #333;
  letter-spacing: 8px;
}

.tablet-dates {
  margin: 0 0 var(--space-2);
  font-size: var(--text-sm);
  color: #666;
}

.tablet-lunar {
  margin: 0 0 var(--space-2);
  font-size: var(--text-xs);
  color: #999;
}

.tablet-honor {
  margin: 0;
  font-size: var(--text-sm);
  color: #999;
}

/* 贡品台 */
.offering-table {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
  justify-content: center;
}

.offering-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  min-width: 60px;
}

.offering-icon {
  font-size: 28px;
  margin-bottom: 4px;
}

.offering-name {
  font-size: var(--text-xs);
  color: #ccc;
}

/* 香火 */
.incense-burner {
  margin-bottom: var(--space-6);
}

.burner {
  background: #2c2c2c;
  padding: var(--space-5) var(--space-8);
  border-radius: 50%;
  text-align: center;
  border: 3px solid #8b4513;
}

.incense-sticks {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-bottom: var(--space-2);
}

.stick {
  width: 4px;
  height: 40px;
  background: linear-gradient(to top, #8b4513, #ff6b6b);
  border-radius: 2px;
  position: relative;
}

.stick::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 12px;
  background: #ff6b6b;
  border-radius: 50%;
  box-shadow: 0 0 10px #ff6b6b;
}

.incense-count {
  font-size: var(--text-sm);
  color: #ccc;
}

/* 统计 */
.worship-stats {
  margin-bottom: var(--space-4);
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
}

.stats-value {
  font-size: 28px;
  font-weight: var(--font-bold);
  color: #f0d78c;
}

.stats-label {
  font-size: var(--text-sm);
  color: #ccc;
}

/* 布置人 */
.creator-info {
  font-size: var(--text-sm);
  color: #999;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.inactive-badge {
  padding: 2px 8px;
  font-size: var(--text-xs);
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-sm);
}

/* 祭拜操作区 */
.worship-card, .records-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.section-title {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-primary);
}

.action-buttons {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
  margin-bottom: var(--space-5);
}

.worship-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-6);
  font-size: var(--text-base);
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.worship-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.worship-btn.kowtow {
  background: linear-gradient(135deg, #4a7c59, #5a8a4a);
  color: white;
}

.worship-btn.incense {
  background: linear-gradient(135deg, #c9a227, #d4af37);
  color: white;
}

.btn-icon {
  font-size: 28px;
}

/* 贡品选择 */
.offering-section {
  border-top: 1px solid var(--border-primary);
  padding-top: var(--space-4);
}

.section-subtitle {
  margin: 0 0 var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.offering-options {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
}

.offering-btn {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.offering-btn:hover {
  border-color: var(--cinnabar);
}

.offering-btn.selected {
  background: var(--cinnabar-pale);
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.offering-submit {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3);
  font-size: var(--text-base);
  color: white;
  background: var(--indigo);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.offering-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 祭拜记录 */
.records-empty {
  text-align: center;
  padding: var(--space-8);
  color: var(--text-tertiary);
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.record-item {
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.record-time {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-bottom: var(--space-1);
}

.record-content {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.record-type {
  padding: 2px 8px;
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
}

.record-type.kowtow {
  background: #d4edda;
  color: #155724;
}

.record-type.incense {
  background: #fff3cd;
  color: #856404;
}

.record-type.offering {
  background: #e2e3e5;
  color: #383d41;
}

.record-user {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.record-message {
  margin: var(--space-2) 0 0;
  padding: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
}

/* 加载和错误状态 */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
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

.error-icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
}

.error-state h2 {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin: 0 0 var(--space-4);
}

/* 响应式 */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }
  
  .worship-btn {
    flex-direction: row;
  }
}
</style>