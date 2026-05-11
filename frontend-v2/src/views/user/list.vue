<template>
  <div class="user-list-page">
    <div class="page-header">
      <h1 class="page-title">用户管理</h1>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="filter-card">
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索用户名或邮箱" 
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>
    </div>
    
    <!-- 用户表格 -->
    <div class="table-card">
      <div class="table-header">
        <div class="col-id">ID</div>
        <div class="col-username">用户名</div>
        <div class="col-email">邮箱</div>
        <div class="col-phone">手机号</div>
        <div class="col-status">状态</div>
        <div class="col-super">超级管理员</div>
        <div class="col-time">注册时间</div>
        <div class="col-actions">操作</div>
      </div>
      
      <div class="table-body" v-if="users.length > 0">
        <div class="table-row" v-for="user in users" :key="user.id">
          <div class="col-id">{{ user.id }}</div>
          <div class="col-username">
            <div class="user-cell">
              <div class="user-avatar">
                <img v-if="user.avatar_url" :src="user.avatar_url" alt="" />
                <span v-else>{{ user.username?.charAt(0)?.toUpperCase() }}</span>
              </div>
              <span class="username">{{ user.username }}</span>
            </div>
          </div>
          <div class="col-email">{{ user.email || '-' }}</div>
          <div class="col-phone">{{ user.phone || '-' }}</div>
          <div class="col-status">
            <span class="status-tag" :class="{ active: user.is_active }">
              {{ user.is_active ? '正常' : '禁用' }}
            </span>
          </div>
          <div class="col-super">
            <span class="super-tag" :class="{ yes: user.is_superuser }">
              {{ user.is_superuser ? '是' : '否' }}
            </span>
          </div>
          <div class="col-time">{{ formatDate(user.created_at) }}</div>
          <div class="col-actions">
            <button class="action-btn view" @click="viewUser(user.id)">详情</button>
            <button 
              v-if="user.id !== userStore.user?.id"
              class="action-btn toggle"
              :class="{ revoke: user.is_superuser }"
              @click="toggleSuperuser(user)"
            >
              {{ user.is_superuser ? '取消超管' : '设为超管' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div class="empty-state" v-else-if="!loading">
        <div class="empty-icon">👤</div>
        <p>暂无用户数据</p>
      </div>
      
      <!-- 加载状态 -->
      <div class="loading-state" v-if="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 分页 -->
      <div class="pagination" v-if="total > pageSize">
        <button class="page-btn" :disabled="currentPage === 1" @click="handlePageChange(currentPage - 1)">上一页</button>
        <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="handlePageChange(currentPage + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { adminApi } from '@/api/admin'
import { useUserStore } from '@/stores/user'
import type { User } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const users = ref<User[]>([])
const total = ref(0)
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await adminApi.getUsers({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined
    })
    users.value = res.items
    total.value = res.total
  } catch (error) {
    console.error(error)
    alert('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

// 分页
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchUsers()
}

// 查看用户详情
const viewUser = (userId: number) => {
  router.push(`/profile?id=${userId}`)
}

// 切换超级管理员
const toggleSuperuser = async (user: User) => {
  const action = user.is_superuser ? '取消' : '设为'
  if (!confirm(`确定要${action}用户 "${user.username}" 的超级管理员权限吗？`)) return
  
  try {
    await adminApi.toggleSuperuser(user.id, !user.is_superuser)
    alert(`${action}超级管理员成功`)
    fetchUsers()
  } catch (error) {
    alert('操作失败')
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-list-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-title {
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

/* 筛选卡片 */
.filter-card {
  padding: var(--space-4);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
}

.search-box {
  display: flex;
  gap: var(--space-2);
}

.search-input {
  flex: 1;
  max-width: 300px;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--cinnabar);
}

.search-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.search-btn:hover {
  background: var(--cinnabar-dark);
}

/* 表格卡片 */
.table-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-header {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-tertiary);
}

.table-header > div {
  padding: var(--space-3);
}

.table-body {
  max-height: 600px;
  overflow-y: auto;
}

.table-row {
  display: flex;
  border-bottom: 1px solid var(--border-light);
  transition: background var(--transition-fast);
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: var(--bg-secondary);
}

.table-row > div {
  padding: var(--space-3);
  display: flex;
  align-items: center;
}

/* 列宽 */
.col-id { width: 60px; }
.col-username { width: 150px; }
.col-email { width: 180px; }
.col-phone { width: 120px; }
.col-status { width: 80px; }
.col-super { width: 100px; }
.col-time { width: 160px; }
.col-actions { flex: 1; justify-content: flex-end; gap: var(--space-2); }

/* 用户单元格 */
.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--indigo);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.username {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

/* 状态标签 */
.status-tag {
  padding: 2px 8px;
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
}

.status-tag.active {
  background: var(--bamboo-pale);
  color: var(--bamboo);
}

.super-tag {
  padding: 2px 8px;
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
  background: var(--bg-secondary);
  color: var(--text-tertiary);
}

.super-tag.yes {
  background: #fff3cd;
  color: #856404;
}

/* 操作按钮 */
.action-btn {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: none;
}

.action-btn.view {
  background: var(--indigo-pale);
  color: var(--indigo);
}

.action-btn.toggle {
  background: #fff3cd;
  color: #856404;
}

.action-btn.toggle.revoke {
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: var(--space-12);
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-3);
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-8);
  color: var(--text-tertiary);
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-primary);
  border-top-color: var(--cinnabar);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  padding: var(--space-4);
  border-top: 1px solid var(--border-primary);
}

.page-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

/* 响应式 */
@media (max-width: 1024px) {
  .table-header,
  .table-row {
    display: block;
  }
  
  .table-header {
    display: none;
  }
  
  .table-row {
    padding: var(--space-3);
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .table-row > div {
    padding: 0;
    width: 100% !important;
    justify-content: space-between;
  }
  
  .col-actions {
    justify-content: flex-start;
    margin-top: var(--space-2);
  }
}
</style>