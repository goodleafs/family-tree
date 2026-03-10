<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const showLayout = computed(() => {
  return !route.path.startsWith('/auth')
})

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/auth/login')
}

onMounted(() => {
  if (userStore.token && !userStore.user) {
    userStore.fetchUser()
  }
})
</script>

<template>
  <div id="app">
    <!-- 登录页面不需要布局 -->
    <router-view v-if="!showLayout" />
    
    <!-- 其他页面使用布局 -->
    <el-container v-else class="layout-container">
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>家谱系统V1.0</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item index="/families">
            <el-icon><UserFilled /></el-icon>
            <span>家族管理</span>
          </el-menu-item>
          
          <el-menu-item v-if="userStore.isSuperuser" index="/users">
            <el-icon><Avatar /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          
          <el-menu-item v-else index="/profile">
            <el-icon><Avatar /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
          
          <el-menu-item index="/tree">
            <el-icon><Share /></el-icon>
            <span>家谱树</span>
          </el-menu-item>
          
          <el-menu-item index="/memorial">
            <el-icon><Help /></el-icon>
            <span>祭拜管理</span>
          </el-menu-item>
          
          <el-menu-item v-if="userStore.isSuperuser" index="/admin">
            <el-icon><Setting /></el-icon>
            <span>个人中心</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container class="main-container">
        <el-header class="header">
<div class="header-right">
            <el-dropdown>
              <span class="user-info">
                <el-icon><User /></el-icon>
                <span>{{ userStore.user?.username || '用户' }}</span>
                <el-tag v-if="userStore.isSuperuser" type="warning" size="small" style="margin-left: 8px;">超管</el-tag>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>个人设置</el-dropdown-item>
                  <el-dropdown-item v-if="userStore.isSuperuser" @click="$router.push('/admin')">系统管理</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  margin: 0;
  color: #fff;
  font-size: 20px;
}

.sidebar-menu {
  border-right: none;
}

.main-container {
  background-color: #f0f2f5;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-info span {
  margin: 0 8px;
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}
</style>
