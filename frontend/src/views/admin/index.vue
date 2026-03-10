<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const editMode = ref(false)
const loading = ref(false)
const passwordLoading = ref(false)

const editForm = ref({
  email: userStore.user?.email || '',
  phone: userStore.user?.phone || ''
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const showPasswordDialog = ref(false)

const userInfo = computed(() => userStore.user)

const startEdit = () => {
  editForm.value = {
    email: userStore.user?.email || '',
    phone: userStore.user?.phone || ''
  }
  editMode.value = true
}

const cancelEdit = () => {
  editMode.value = false
}

const saveEdit = async () => {
  loading.value = true
  try {
    await authApi.updateUser({
      email: editForm.value.email || undefined,
      phone: editForm.value.phone || undefined
    })
    await userStore.fetchUser()
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
</script>

<template>
  <div class="profile-page">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>
    
    <el-row :gutter="20">
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
                <el-button v-if="!editMode" type="primary" @click="startEdit">编辑</el-button>
                <template v-else>
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
            <el-button type="primary" @click="showPasswordDialog = true">
              修改密码
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