<template>
  <div class="families-page">
    <div class="page-header">
      <h1 class="page-title">家族管理</h1>
      <button class="create-btn" @click="showCreateDialog = true">
        <svg viewBox="0 0 16 16" fill="none">
          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        创建家族
      </button>
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-input">
        <svg viewBox="0 0 16 16" fill="none">
          <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.5"/>
          <path d="M11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <input 
          v-model="searchQuery" 
          placeholder="搜索家族..." 
          @input="handleSearch"
        />
      </div>
    </div>
    
    <!-- 家族列表 -->
    <div class="families-list" v-if="families.length > 0">
      <div 
        class="family-item" 
        v-for="family in families" 
        :key="family.id"
        @click="$router.push(`/families/${family.id}`)"
      >
        <div class="family-main">
          <div class="family-icon">
            {{ family.surname?.charAt(0) || '族' }}
          </div>
          <div class="family-info">
            <h3 class="family-name">{{ family.name }}</h3>
            <p class="family-desc">{{ family.description || '暂无简介' }}</p>
          </div>
        </div>
        <div class="family-meta">
          <span class="meta-badge">
            <svg viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/>
              <path d="M2 14c0-2.5 2.5-4.5 6-4.5s6 2 6 4.5" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            {{ family.person_count || 0 }} 人
          </span>
          <span class="meta-status" :class="{ public: family.is_public }">
            {{ family.is_public ? '公开' : '私密' }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-else-if="!loading">
      <div class="empty-icon">📜</div>
      <h3>还没有家族</h3>
      <p>点击上方按钮创建您的第一个家族</p>
    </div>
    
    <!-- 创建对话框 -->
    <div class="dialog-overlay" v-if="showCreateDialog" @click="showCreateDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>创建家族</h2>
          <button class="close-btn" @click="showCreateDialog = false">×</button>
        </div>
        <form class="dialog-form" @submit.prevent="handleCreate">
          <div class="form-group">
            <label>家族名称 *</label>
            <input v-model="createForm.name" placeholder="请输入家族名称" required />
          </div>
          <div class="form-group">
            <label>姓氏</label>
            <input v-model="createForm.surname" placeholder="如：张、李、王" />
          </div>
          <div class="form-group">
            <label>家族简介</label>
            <textarea v-model="createForm.description" placeholder="请输入家族简介" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="createForm.is_public" />
              <span>公开家族（其他用户可见）</span>
            </label>
          </div>
          <div class="dialog-actions">
            <button type="button" class="btn-cancel" @click="showCreateDialog = false">取消</button>
            <button type="submit" class="btn-submit" :disabled="createLoading">
              {{ createLoading ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { familyApi } from '@/api/family'
import type { Family } from '@/types'

const router = useRouter()
const families = ref<Family[]>([])
const loading = ref(false)
const searchQuery = ref('')
const showCreateDialog = ref(false)
const createLoading = ref(false)

const createForm = reactive({
  name: '',
  surname: '',
  description: '',
  is_public: false
})

const fetchFamilies = async () => {
  loading.value = true
  try {
    const res = await familyApi.getFamilies({ search: searchQuery.value || undefined })
    families.value = res.items
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchFamilies()
}

const handleCreate = async () => {
  if (!createForm.name) return
  
  createLoading.value = true
  try {
    const family = await familyApi.createFamily(createForm)
    showCreateDialog.value = false
    router.push(`/families/${family.id}`)
  } catch (error: any) {
    console.error(error)
    alert(error?.response?.data?.detail || '创建失败')
  } finally {
    createLoading.value = false
  }
}

onMounted(() => {
  fetchFamilies()
})
</script>

<style scoped>
.families-page {
  max-width: 900px;
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
  font-weight: var(--font-medium);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.create-btn:hover {
  background: var(--cinnabar-dark);
}

.create-btn svg {
  width: 16px;
  height: 16px;
}

/* 搜索栏 */
.search-bar {
  margin-bottom: var(--space-6);
}

.search-input {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
}

.search-input svg {
  width: 18px;
  height: 18px;
  color: var(--text-tertiary);
}

.search-input input {
  flex: 1;
  border: none;
  background: none;
  font-size: var(--text-base);
  color: var(--text-primary);
}

.search-input input::placeholder {
  color: var(--text-tertiary);
}

.search-input input:focus {
  outline: none;
}

/* 家族列表 */
.families-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.family-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.family-item:hover {
  border-color: var(--cinnabar);
  box-shadow: var(--shadow-md);
}

.family-main {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.family-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--cinnabar) 0%, var(--cinnabar-light) 100%);
  color: white;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-title);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
}

.family-info {
  display: flex;
  flex-direction: column;
}

.family-name {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
}

.family-desc {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

.family-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.meta-badge {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.meta-badge svg {
  width: 14px;
  height: 14px;
}

.meta-status {
  font-size: var(--text-xs);
  padding: 2px 8px;
  background: var(--bg-secondary);
  color: var(--text-tertiary);
  border-radius: var(--radius-full);
}

.meta-status.public {
  background: var(--bamboo-pale);
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
  font-size: 48px;
  margin-bottom: var(--space-4);
}

.empty-state h3 {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
}

.empty-state p {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--space-4);
}

@media (max-width: 768px) {
  .families-grid { grid-template-columns: 1fr; }
  .search-section { flex-direction: column; }
  .search-section input { width: 100%; }
}

.dialog {
  width: 100%;
  max-width: 480px;
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5);
  border-bottom: 1px solid var(--border-primary);
}

.dialog-header h2 {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--text-tertiary);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: var(--radius-md);
}

.close-btn:hover {
  background: var(--bg-secondary);
}

.dialog-form {
  padding: var(--space-5);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: var(--space-3);
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--cinnabar);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  margin-top: var(--space-4);
}

.btn-cancel {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.btn-submit {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: var(--cinnabar-dark);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>