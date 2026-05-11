<template>
  <div class="create-memorial-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/memorial')">
        <svg viewBox="0 0 16 16" fill="none">
          <path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        返回
      </button>
      <h1 class="page-title">布置灵堂</h1>
    </div>
    
    <!-- 表单卡片 -->
    <div class="form-card">
      <div class="form-section">
        <!-- 选择逝者 -->
        <div class="form-group">
          <label class="form-label">选择逝者 <span class="required">*</span></label>
          <select v-model="selectedPerson" class="form-select">
            <option :value="0">请选择要布置灵堂的逝者</option>
            <option 
              v-for="person in eligiblePersons" 
              :key="person.id" 
              :value="person.id"
            >
              {{ person.name }}{{ person.death_date ? ` (逝世：${person.death_date})` : '' }}
            </option>
          </select>
          
          <div class="alert-warning" v-if="eligiblePersons.length === 0 && !loading">
            该家族暂无可布置灵堂的逝者（需要有逝世日期且尚未布置灵堂）
          </div>
        </div>
        
        <!-- 选择贡品 -->
        <div class="form-group">
          <label class="form-label">选择贡品 <span class="required">*</span></label>
          <p class="form-hint">点击选择要供奉的贡品</p>
          
          <div class="offerings-grid">
            <button
              v-for="offering in availableOfferings"
              :key="offering.name"
              class="offering-card"
              :class="{ selected: selectedOfferings.some(o => o.name === offering.name) }"
              @click="toggleOffering(offering)"
            >
              <span class="offering-icon">{{ offering.icon }}</span>
              <span class="offering-name">{{ offering.name }}</span>
              <span v-if="selectedOfferings.some(o => o.name === offering.name)" class="check-icon">✓</span>
            </button>
          </div>
          
          <div class="selected-preview">
            <span class="preview-label">已选择：</span>
            <span v-if="selectedOfferings.length === 0" class="preview-empty">未选择贡品</span>
            <span v-else class="preview-items">
              {{ selectedOfferings.map(o => `${o.icon} ${o.name}`).join('、') }}
            </span>
          </div>
        </div>
        
        <!-- 预览 -->
        <div class="form-group">
          <label class="form-label">灵堂预览</label>
          <div class="preview-hall">
            <div class="preview-altar">
              <div class="preview-tablet">
                <span class="preview-title">故显考</span>
                <span class="preview-name">{{ selectedPersonName || '逝者姓名' }}</span>
              </div>
              
              <div class="preview-offerings" v-if="selectedOfferings.length > 0">
                <span 
                  v-for="item in selectedOfferings" 
                  :key="item.name"
                  class="preview-offering"
                >
                  {{ item.icon }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 提交按钮 -->
        <button 
          class="submit-btn"
          :disabled="!selectedPerson || selectedOfferings.length === 0 || submitting"
          @click="handleSubmit"
        >
          {{ submitting ? '布置中...' : '布置灵堂' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { memorialApi, type OfferingItem, type PersonBrief } from '@/api/memorial'

const route = useRoute()
const router = useRouter()
const familyId = parseInt(route.query.family_id as string)

const eligiblePersons = ref<PersonBrief[]>([])
const selectedPerson = ref(0)
const loading = ref(false)
const submitting = ref(false)

// 可选贡品
const availableOfferings: OfferingItem[] = [
  { name: '鲜花', icon: '🌸' },
  { name: '水果', icon: '🍎' },
  { name: '糕点', icon: '🥮' },
  { name: '酒水', icon: '🍶' },
  { name: '香烛', icon: '🕯️' },
  { name: '纸钱', icon: '💴' },
  { name: '菜肴', icon: '🍲' },
  { name: '茶点', icon: '🍵' }
]

// 默认选择三种贡品
const selectedOfferings = ref<OfferingItem[]>([
  { name: '鲜花', icon: '🌸' },
  { name: '水果', icon: '🍎' },
  { name: '糕点', icon: '🥮' }
])

// 选中逝者姓名
const selectedPersonName = computed(() => {
  const person = eligiblePersons.value.find(p => p.id === selectedPerson.value)
  return person?.name || ''
})

// 获取可布置灵堂的逝者列表
const fetchEligiblePersons = async () => {
  if (!familyId) return
  
  loading.value = true
  try {
    eligiblePersons.value = await memorialApi.getEligiblePersons(familyId)
  } catch (error) {
    console.error(error)
    alert('获取可布置灵堂的逝者列表失败')
  } finally {
    loading.value = false
  }
}

// 切换贡品选择
const toggleOffering = (offering: OfferingItem) => {
  const index = selectedOfferings.value.findIndex(o => o.name === offering.name)
  if (index > -1) {
    selectedOfferings.value.splice(index, 1)
  } else {
    selectedOfferings.value.push(offering)
  }
}

// 提交布置灵堂
const handleSubmit = async () => {
  if (!selectedPerson.value) {
    alert('请选择逝者')
    return
  }
  
  if (selectedOfferings.value.length === 0) {
    alert('请至少选择一种贡品')
    return
  }
  
  submitting.value = true
  try {
    await memorialApi.createMemorialHall({
      person_id: selectedPerson.value,
      offerings: selectedOfferings.value
    })
    
    alert('灵堂布置成功')
    router.push('/memorial')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '布置失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!familyId) {
    alert('请先选择家族')
    router.push('/memorial')
    return
  }
  fetchEligiblePersons()
})
</script>

<style scoped>
.create-memorial-page {
  max-width: 600px;
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

/* 表单卡片 */
.form-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.required {
  color: var(--cinnabar);
}

.form-hint {
  margin: 0;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.form-select {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.form-select:focus {
  outline: none;
  border-color: var(--cinnabar);
}

.alert-warning {
  padding: var(--space-3);
  font-size: var(--text-sm);
  color: #856404;
  background: #fff3cd;
  border-radius: var(--radius-md);
  margin-top: var(--space-2);
}

/* 贡品网格 */
.offerings-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-2);
}

.offering-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-3);
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  background: var(--bg-primary);
}

.offering-card:hover {
  border-color: var(--cinnabar);
}

.offering-card.selected {
  border-color: var(--cinnabar);
  background: var(--cinnabar-pale);
}

.offering-icon {
  font-size: 28px;
  margin-bottom: var(--space-1);
}

.offering-name {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.check-icon {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  background: var(--cinnabar);
  border-radius: 50%;
}

/* 已选预览 */
.selected-preview {
  margin-top: var(--space-3);
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
}

.preview-label {
  color: var(--text-tertiary);
  margin-right: var(--space-2);
}

.preview-empty {
  color: var(--text-tertiary);
}

.preview-items {
  color: var(--text-primary);
}

/* 灵堂预览 */
.preview-hall {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: var(--space-6);
  border-radius: var(--radius-lg);
}

.preview-altar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.preview-tablet {
  background: linear-gradient(145deg, #8b4513, #a0522d);
  padding: 6px;
  border-radius: 6px;
  text-align: center;
  min-width: 150px;
}

.preview-tablet::before {
  content: '';
  display: block;
  background: #f5f5dc;
  padding: var(--space-4) var(--space-6);
  border-radius: 3px;
}

.preview-title {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.preview-name {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.preview-offerings {
  display: flex;
  gap: var(--space-2);
}

.preview-offering {
  font-size: 24px;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: var(--space-3);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.submit-btn:hover:not(:disabled) {
  background: var(--cinnabar-dark);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 768px) {
  .offerings-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>