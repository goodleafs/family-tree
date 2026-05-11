<template>
  <div class="profile-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <button class="back-btn" @click="$router.back()">
        <svg viewBox="0 0 16 16" fill="none">
          <path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        返回
      </button>
      <h1 class="page-title">{{ isOwnProfile ? '个人中心' : '用户详情' }}</h1>
    </div>
    
    <!-- 加载状态 -->
    <div class="loading-state" v-if="userLoading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 内容区域 -->
    <div class="profile-content" v-else-if="userInfo">
      <div class="profile-grid">
        <!-- 左侧：用户卡片 -->
        <div class="user-card">
          <div class="avatar-section">
            <div class="user-avatar">
              <img v-if="userInfo.avatar_url" :src="userInfo.avatar_url" alt="" />
              <span v-else>{{ userInfo.username?.charAt(0)?.toUpperCase() }}</span>
            </div>
            <h3 class="user-name">{{ userInfo.username }}</h3>
            <p class="user-id">ID: {{ userInfo.id }}</p>
            
            <div class="user-badges">
              <span v-if="userInfo.is_superuser" class="badge super">超级管理员</span>
              <span v-else class="badge" :class="{ active: userInfo.is_active }">
                {{ userInfo.is_active ? '正常' : '禁用' }}
              </span>
            </div>
          </div>
          
          <div class="avatar-upload" v-if="isOwnProfile">
            <input type="file" ref="avatarInput" accept="image/*" @change="handleAvatarUpload" style="display: none" />
            <button class="upload-btn" @click="() => avatarInput?.click()" :disabled="avatarLoading">
              {{ avatarLoading ? '上传中...' : '更换头像' }}
            </button>
          </div>
        </div>
        
        <!-- 右侧：信息卡片 -->
        <div class="info-card">
          <div class="card-header">
            <h3>基本信息</h3>
            <div class="header-actions">
              <button v-if="!editMode && (isOwnProfile || userStore.isSuperuser)" class="edit-btn" @click="startEdit">编辑</button>
              <template v-else-if="editMode">
                <button class="cancel-btn" @click="cancelEdit">取消</button>
                <button class="save-btn" @click="saveEdit" :disabled="loading">{{ loading ? '保存中...' : '保存' }}</button>
              </template>
            </div>
          </div>
          
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">用户名</span>
              <span class="info-value">{{ userInfo.username }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">邮箱</span>
              <input v-if="editMode" v-model="editForm.email" class="info-input" placeholder="请输入邮箱" />
              <span v-else class="info-value">{{ userInfo.email || '未设置' }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">手机号</span>
              <input v-if="editMode" v-model="editForm.phone" class="info-input" placeholder="请输入手机号" />
              <span v-else class="info-value">{{ userInfo.phone || '未设置' }}</span>
            </div>
            
            <div class="info-item">
              <span class="info-label">注册时间</span>
              <span class="info-value">{{ formatDate(userInfo.created_at) }}</span>
            </div>
          </div>
          
          <div class="actions-section">
            <button v-if="isOwnProfile" class="password-btn" @click="showPasswordDialog = true">
              修改密码
            </button>
            <button v-else-if="userStore.isSuperuser" class="reset-btn" @click="showResetPasswordDialog = true">
              重置密码
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 修改密码对话框 -->
    <div class="dialog-overlay" v-if="showPasswordDialog" @click="showPasswordDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>修改密码</h2>
          <button class="close-btn" @click="showPasswordDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>当前密码</label>
            <input v-model="passwordForm.currentPassword" type="password" placeholder="请输入当前密码" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码（至少6位）" />
          </div>
          <div class="form-group">
            <label>确认密码</label>
            <input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showPasswordDialog = false">取消</button>
          <button class="btn-submit" @click="changePassword" :disabled="passwordLoading">
            {{ passwordLoading ? '修改中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 重置密码对话框 -->
    <div class="dialog-overlay" v-if="showResetPasswordDialog" @click="showResetPasswordDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>重置用户密码</h2>
          <button class="close-btn" @click="showResetPasswordDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="alert-warning">
            正在为 <strong>{{ userInfo?.username }}</strong> 重置密码
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="resetPasswordForm.newPassword" type="password" placeholder="请输入新密码（至少6位）" />
          </div>
          <div class="form-group">
            <label>确认密码</label>
            <input v-model="resetPasswordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showResetPasswordDialog = false">取消</button>
          <button class="btn-submit" @click="resetPassword" :disabled="resetPasswordLoading">
            {{ resetPasswordLoading ? '重置中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { adminApi } from '@/api/admin'
import type { User } from '@/types'

const route = useRoute()
const userStore = useUserStore()

const editMode = ref(false)
const loading = ref(false)
const passwordLoading = ref(false)
const avatarLoading = ref(false)
const userLoading = ref(false)

// 目标用户ID（管理员查看其他用户）
const targetUserId = computed(() => {
  const id = route.query.id
  return id ? parseInt(id as string) : null
})

// 是否是查看自己的资料
const isOwnProfile = computed(() => !targetUserId.value || targetUserId.value === userStore.user?.id)

// 目标用户信息
const targetUser = ref<User | null>(null)

// 显示的用户信息
const userInfo = computed(() => {
  if (isOwnProfile.value) {
    return userStore.user
  }
  return targetUser.value
})

// 编辑表单
const editForm = ref({
  email: '',
  phone: ''
})

// 密码表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const resetPasswordForm = ref({
  newPassword: '',
  confirmPassword: ''
})

const showPasswordDialog = ref(false)
const showResetPasswordDialog = ref(false)
const resetPasswordLoading = ref(false)
const avatarInput = ref<HTMLInputElement | null>(null)

// 加载目标用户信息
const loadTargetUser = async () => {
  if (!targetUserId.value || isOwnProfile.value) {
    targetUser.value = null
    return
  }
  
  userLoading.value = true
  try {
    targetUser.value = await adminApi.getUser(targetUserId.value)
  } catch (error) {
    console.error(error)
    alert('获取用户信息失败')
  } finally {
    userLoading.value = false
  }
}

// 开始编辑
const startEdit = () => {
  editForm.value = {
    email: userInfo.value?.email || '',
    phone: userInfo.value?.phone || ''
  }
  editMode.value = true
}

// 取消编辑
const cancelEdit = () => {
  editMode.value = false
}

// 保存编辑
const saveEdit = async () => {
  loading.value = true
  try {
    if (targetUserId.value && !isOwnProfile.value) {
      await adminApi.updateUser(targetUserId.value, {
        email: editForm.value.email || undefined,
        phone: editForm.value.phone || undefined
      })
      await loadTargetUser()
    } else {
      await authApi.updateUser({
        email: editForm.value.email || undefined,
        phone: editForm.value.phone || undefined
      })
      await userStore.fetchUser()
    }
    editMode.value = false
    alert('信息更新成功')
  } catch (error) {
    console.error(error)
    alert('更新失败')
  } finally {
    loading.value = false
  }
}

// 修改密码
const changePassword = async () => {
  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword) {
    alert('请填写完整信息')
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    alert('两次输入的新密码不一致')
    return
  }
  
  if (passwordForm.value.newPassword.length < 6) {
    alert('密码长度至少6位')
    return
  }
  
  passwordLoading.value = true
  try {
    await authApi.changePassword({
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })
    alert('密码修改成功')
    showPasswordDialog.value = false
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    alert('密码修改失败，请检查当前密码是否正确')
  } finally {
    passwordLoading.value = false
  }
}

// 重置密码
const resetPassword = async () => {
  if (!resetPasswordForm.value.newPassword) {
    alert('请输入新密码')
    return
  }
  
  if (resetPasswordForm.value.newPassword !== resetPasswordForm.value.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  
  if (resetPasswordForm.value.newPassword.length < 6) {
    alert('密码长度至少6位')
    return
  }
  
  if (!targetUserId.value) {
    alert('未选择目标用户')
    return
  }
  
  resetPasswordLoading.value = true
  try {
    await adminApi.resetUserPassword(targetUserId.value, resetPasswordForm.value.newPassword)
    alert('密码重置成功')
    showResetPasswordDialog.value = false
    resetPasswordForm.value = {
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    alert('密码重置失败')
  } finally {
    resetPasswordLoading.value = false
  }
}

// 上传头像
const handleAvatarUpload = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  
  avatarLoading.value = true
  try {
    const res = await authApi.uploadAvatar(file)
    if (userStore.user) {
      userStore.user.avatar_url = res.avatar_url
    }
    alert('头像上传成功')
  } catch (error) {
    alert('头像上传失败')
  } finally {
    avatarLoading.value = false
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 监听路由参数变化
watch(() => route.query.id, () => {
  loadTargetUser()
  editMode.value = false
})

onMounted(() => {
  loadTargetUser()
})
</script>

<style scoped>
.profile-page {
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

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
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

/* 内容网格 */
.profile-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: var(--space-6);
}

/* 用户卡片 */
.user-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}

.avatar-section {
  text-align: center;
}

.user-avatar {
  width: 100px;
  height: 100px;
  margin: 0 auto var(--space-4);
  border-radius: 50%;
  overflow: hidden;
  background: var(--indigo);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-1);
}

.user-id {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0 0 var(--space-3);
}

.user-badges {
  display: flex;
  justify-content: center;
}

.badge {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
}

.badge.active {
  background: var(--bamboo-pale);
  color: var(--bamboo);
}

.badge.super {
  background: #fff3cd;
  color: #856404;
}

.avatar-upload {
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-light);
}

.upload-btn {
  width: 100%;
  padding: var(--space-2);
  font-size: var(--text-sm);
  color: var(--cinnabar);
  border: 1px solid var(--cinnabar);
  border-radius: var(--radius-md);
  background: none;
  cursor: pointer;
}

.upload-btn:hover {
  background: var(--cinnabar-pale);
}

/* 信息卡片 */
.info-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-primary);
}

.card-header h3 {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.edit-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.cancel-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.save-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: white;
  background: var(--bamboo);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.info-list {
  padding: var(--space-5);
}

.info-item {
  display: flex;
  align-items: center;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  width: 100px;
  flex-shrink: 0;
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.info-value {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.info-input {
  flex: 1;
  padding: var(--space-2);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.info-input:focus {
  outline: none;
  border-color: var(--cinnabar);
}

.actions-section {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border-primary);
  text-align: center;
}

.password-btn {
  padding: var(--space-2) var(--space-6);
  font-size: var(--text-sm);
  color: white;
  background: var(--indigo);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.reset-btn {
  padding: var(--space-2) var(--space-6);
  font-size: var(--text-sm);
  color: white;
  background: #856404;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-4);
}

.dialog {
  width: 100%;
  max-width: 400px;
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
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
}

.dialog-body {
  padding: var(--space-5);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-bottom: var(--space-2);
}

.form-group input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.form-group input:focus {
  outline: none;
  border-color: var(--cinnabar);
}

.alert-warning {
  padding: var(--space-3);
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
  color: #856404;
  background: #fff3cd;
  border-radius: var(--radius-md);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border-primary);
}

.btn-cancel {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
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

.btn-submit:disabled {
  opacity: 0.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>