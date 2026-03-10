<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { adminApi } from '@/api/admin'
import type { User } from '@/types'
import { ElMessage } from 'element-plus'

const route = useRoute()
const userStore = useUserStore()

const editMode = ref(false)
const loading = ref(false)
const passwordLoading = ref(false)
const userLoading = ref(false)

// 判断是否是查看其他用户（管理员查看）
const targetUserId = computed(() => {
  const id = route.query.id
  return id ? parseInt(id as string) : null
})

// 是否是查看自己的资料
const isOwnProfile = computed(() => !targetUserId.value || targetUserId.value === userStore.user?.id)

// 目标用户信息（可能是自己或其他用户）
const targetUser = ref<User | null>(null)

const editForm = ref({
  email: '',
  phone: ''
})

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

// 显示的用户信息
const userInfo = computed(() => {
  if (isOwnProfile.value) {
    return userStore.user
  }
  return targetUser.value
})

// 加载目标用户信息
const loadTargetUser = async () => {
  if (!targetUserId.value || isOwnProfile.value) {
    targetUser.value = null
    return
  }
  
  userLoading.value = true
  try {
    const user = await adminApi.getUser(targetUserId.value)
    targetUser.value = user
  } catch (error) {
    console.error(error)
    ElMessage.error('获取用户信息失败')
  } finally {
    userLoading.value = false
  }
}

const startEdit = () => {
  editForm.value = {
    email: userInfo.value?.email || '',
    phone: userInfo.value?.phone || ''
  }
  editMode.value = true
}

const cancelEdit = () => {
  editMode.value = false
}

const saveEdit = async () => {
  loading.value = true
  try {
    // 如果是编辑其他用户（管理员权限）
    if (targetUserId.value && !isOwnProfile.value) {
      await adminApi.updateUser(targetUserId.value, {
        email: editForm.value.email || undefined,
        phone: editForm.value.phone || undefined
      })
      await loadTargetUser()
    } else {
      // 编辑自己
      await authApi.updateUser({
        email: editForm.value.email || undefined,
        phone: editForm.value.phone || undefined
      })
      await userStore.fetchUser()
    }
    editMode.value = false
    ElMessage.success('信息更新成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('更新失败')
  } finally {
    loading.value = false
  }
}

const changePassword = async () => {
  if (!passwordForm.value.currentPassword || !passwordForm.value.newPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  
  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.warning('密码长度至少6位')
    return
  }
  
  passwordLoading.value = true
  try {
    await authApi.changePassword({
      current_password: passwordForm.value.currentPassword,
      new_password: passwordForm.value.newPassword
    })
    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('密码修改失败，请检查当前密码是否正确')
  } finally {
    passwordLoading.value = false
  }
}

const resetPassword = async () => {
  if (!resetPasswordForm.value.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  
  if (resetPasswordForm.value.newPassword !== resetPasswordForm.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  if (resetPasswordForm.value.newPassword.length < 6) {
    ElMessage.warning('密码长度至少6位')
    return
  }
  
  if (!targetUserId.value) {
    ElMessage.error('未选择目标用户')
    return
  }
  
  resetPasswordLoading.value = true
  try {
    await adminApi.resetUserPassword(targetUserId.value, resetPasswordForm.value.newPassword)
    ElMessage.success('密码重置成功')
    showResetPasswordDialog.value = false
    resetPasswordForm.value = {
      newPassword: '',
      confirmPassword: ''
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('密码重置失败')
  } finally {
    resetPasswordLoading.value = false
  }
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

<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>{{ isOwnProfile ? '个人中心' : '用户详情' }}</h2>
    </div>
    
    <el-row :gutter="20" v-loading="userLoading">
      <el-col :span="8">
        <el-card>
          <div class="user-card">
            <el-avatar :size="80" :src="userInfo?.avatar_url || '/default-avatar.png'">
              {{ userInfo?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <h3>{{ userInfo?.username }}</h3>
            <p class="user-id">ID: {{ userInfo?.id }}</p>
            <el-tag v-if="userInfo?.is_superuser" type="warning">超级管理员</el-tag>
            <el-tag v-else :type="userInfo?.is_active ? 'success' : 'danger'">
              {{ userInfo?.is_active ? '正常' : '禁用' }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <div>
                <el-button v-if="!editMode && (isOwnProfile || userStore.isSuperuser)" type="primary" @click="startEdit">编辑</el-button>
                <template v-else-if="editMode">
                  <el-button @click="cancelEdit">取消</el-button>
                  <el-button type="primary" :loading="loading" @click="saveEdit">保存</el-button>
                </template>
              </div>
            </div>
          </template>
          
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">
              {{ userInfo?.username }}
            </el-descriptions-item>
            
            <el-descriptions-item label="邮箱">
              <el-input
                v-if="editMode"
                v-model="editForm.email"
                placeholder="请输入邮箱"
              />
              <span v-else>{{ userInfo?.email || '未设置' }}</span>
            </el-descriptions-item>
            
            <el-descriptions-item label="手机号">
              <el-input
                v-if="editMode"
                v-model="editForm.phone"
                placeholder="请输入手机号"
              />
              <span v-else>{{ userInfo?.phone || '未设置' }}</span>
            </el-descriptions-item>
            
            <el-descriptions-item label="注册时间">
              {{ new Date(userInfo?.created_at || '').toLocaleString('zh-CN') }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div class="actions">
            <el-button v-if="isOwnProfile" type="primary" @click="showPasswordDialog = true">
              修改密码
            </el-button>
            <el-button v-else-if="userStore.isSuperuser" type="warning" @click="showResetPasswordDialog = true">
              重置密码
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="新密码">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="changePassword">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="showResetPasswordDialog" title="重置用户密码" width="400px">
      <el-alert
        :title="`正在为 ${userInfo?.username} 重置密码`"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />
      <el-form :model="resetPasswordForm" label-width="100px">
        <el-form-item label="新密码">
          <el-input
            v-model="resetPasswordForm.newPassword"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码">
          <el-input
            v-model="resetPasswordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showResetPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="resetPasswordLoading" @click="resetPassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile-page {
  padding: 20px 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.user-card {
  text-align: center;
  padding: 20px 0;
}

.user-card h3 {
  margin: 16px 0 8px;
}

.user-id {
  color: #909399;
  font-size: 12px;
  margin: 0 0 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  margin-top: 20px;
  text-align: center;
}
</style>