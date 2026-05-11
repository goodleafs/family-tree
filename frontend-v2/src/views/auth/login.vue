<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="bg-pattern"></div>
    <div class="ink-wash"></div>
    
    <!-- 登录卡片 -->
    <div class="login-container">
      <div class="login-card">
        <!-- 顶部装饰 -->
        <div class="card-decoration-top">
          <svg viewBox="0 0 200 20" fill="none">
            <path d="M0 10 Q50 0 100 10 T200 10" stroke="var(--cinnabar)" stroke-width="1" fill="none" opacity="0.3"/>
          </svg>
        </div>
        
        <!-- Logo区域 -->
        <div class="login-header">
          <div class="logo-seal">
            <span>寻根</span>
          </div>
          <h1 class="login-title">寻根族谱</h1>
          <p class="login-subtitle">传承家族记忆 · 延续血脉亲情</p>
        </div>
        
        <!-- 表单区域 -->
        <form class="login-form" @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <svg viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="5" r="3" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M2 14c0-2.5 2.5-4.5 6-4.5s6 2 6 4.5" stroke="currentColor" stroke-width="1.5"/>
                </svg>
              </span>
              <input
                v-model="form.username"
                type="text"
                placeholder="请输入用户名"
                class="form-input"
                autocomplete="username"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">密码</label>
            <div class="input-wrapper">
              <span class="input-icon">
                <svg viewBox="0 0 16 16" fill="none">
                  <rect x="3" y="6" width="10" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
                  <circle cx="8" cy="10" r="1" fill="currentColor"/>
                  <path d="M5 6V4a3 3 0 116 0v2" stroke="currentColor" stroke-width="1.5"/>
                </svg>
              </span>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                class="form-input"
                autocomplete="current-password"
              />
              <button type="button" class="password-toggle" @click="showPassword = !showPassword">
                <svg v-if="showPassword" viewBox="0 0 16 16" fill="none">
                  <path d="M1 8s2-4 7-4 7 4 7 4-2 4-7 4-7-4-7-4z" stroke="currentColor" stroke-width="1.5"/>
                  <circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                <svg v-else viewBox="0 0 16 16" fill="none">
                  <path d="M1 8s2-4 7-4 7 4 7 4-2 4-7 4-7-4-7-4z" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M1 1l14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>
          
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else>登 录</span>
          </button>
        </form>
        
        <!-- 底部链接 -->
        <div class="login-footer">
          <div class="divider">
            <span>还没有账号？</span>
          </div>
          <router-link to="/auth/register" class="register-link">
            立即注册，创建您的家族族谱
          </router-link>
        </div>
        
        <!-- 底部装饰 -->
        <div class="card-decoration-bottom">
          <svg viewBox="0 0 200 20" fill="none">
            <path d="M0 10 Q50 20 100 10 T200 10" stroke="var(--cinnabar)" stroke-width="1" fill="none" opacity="0.3"/>
          </svg>
        </div>
      </div>
      
      <!-- 底部版权 -->
      <p class="copyright">© 2024 寻根族谱 · 传承中华家族文化</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const showPassword = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    return
  }
  
  loading.value = true
  try {
    const res = await authApi.login(form)
    localStorage.setItem('token', res.access_token)
    await userStore.fetchUser()
    
    // 跳转到之前的页面或首页
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (error: any) {
    console.error(error)
    alert(error?.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  position: relative;
  overflow: hidden;
}

/* 背景 */
.bg-pattern {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0L60 30L30 60L0 30z' fill='none' stroke='%23b5b5b5' stroke-width='0.5' opacity='0.1'/%3E%3C/svg%3E");
  opacity: 0.5;
}

.ink-wash {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(196, 30, 58, 0.05) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(44, 74, 110, 0.05) 0%, transparent 50%),
    linear-gradient(135deg, var(--paper-cream) 0%, var(--paper-white) 50%, var(--paper-cream) 100%);
}

/* 登录容器 */
.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
}

/* 登录卡片 */
.login-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-10);
  position: relative;
  box-shadow: 
    0 4px 6px rgba(0, 0, 0, 0.05),
    0 10px 20px rgba(0, 0, 0, 0.08);
}

/* 装饰 */
.card-decoration-top,
.card-decoration-bottom {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
}

.card-decoration-top {
  top: var(--space-4);
}

.card-decoration-bottom {
  bottom: var(--space-4);
}

/* Logo区域 */
.login-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.logo-seal {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--space-4);
  background: linear-gradient(135deg, var(--cinnabar) 0%, var(--cinnabar-dark) 100%);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  letter-spacing: 0.1em;
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
  position: relative;
}

.logo-seal::after {
  content: '';
  position: absolute;
  inset: 3px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: var(--radius-sm);
}

.login-title {
  font-family: var(--font-title);
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  letter-spacing: 0.15em;
  margin: 0 0 var(--space-2);
}

.login-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  letter-spacing: 0.05em;
  margin: 0;
}

/* 表单 */
.login-form {
  margin-bottom: var(--space-6);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: var(--space-4);
  width: 16px;
  height: 16px;
  color: var(--text-tertiary);
  pointer-events: none;
}

.input-icon svg {
  width: 100%;
  height: 100%;
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  padding-left: calc(var(--space-4) * 2 + 16px);
  font-size: var(--text-base);
  font-family: var(--font-body);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.form-input::placeholder {
  color: var(--text-tertiary);
}

.form-input:hover {
  border-color: var(--border-secondary);
}

.form-input:focus {
  outline: none;
  border-color: var(--cinnabar);
  box-shadow: 0 0 0 3px var(--cinnabar-pale);
}

.password-toggle {
  position: absolute;
  right: var(--space-3);
  width: 20px;
  height: 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover {
  color: var(--text-secondary);
}

.password-toggle svg {
  width: 16px;
  height: 16px;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  padding: var(--space-3) var(--space-6);
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  letter-spacing: 0.2em;
  color: white;
  background: linear-gradient(135deg, var(--cinnabar) 0%, var(--cinnabar-dark) 100%);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 底部 */
.login-footer {
  text-align: center;
}

.divider {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-primary);
}

.register-link {
  display: inline-block;
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--cinnabar);
  border: 1px solid var(--cinnabar);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.register-link:hover {
  background: var(--cinnabar);
  color: white;
}

.copyright {
  margin-top: var(--space-6);
  text-align: center;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    padding: var(--space-6);
  }
  
  .login-title {
    font-size: var(--text-2xl);
  }
  
  .logo-seal {
    width: 60px;
    height: 60px;
    font-size: var(--text-xl);
  }
}
</style>