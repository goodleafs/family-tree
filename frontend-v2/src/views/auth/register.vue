<template>
  <div class="register-page">
    <!-- 背景 -->
    <div class="bg-pattern"></div>
    <div class="ink-wash"></div>
    
    <!-- 注册卡片 -->
    <div class="register-container">
      <div class="register-card">
        <!-- 顶部装饰 -->
        <div class="card-decoration-top">
          <svg viewBox="0 0 200 20" fill="none">
            <path d="M0 10 Q50 0 100 10 T200 10" stroke="var(--cinnabar)" stroke-width="1" fill="none" opacity="0.3"/>
          </svg>
        </div>
        
        <!-- 标题 -->
        <div class="register-header">
          <h1 class="register-title">创建账号</h1>
          <p class="register-subtitle">加入寻根族谱，开启您的家族传承之旅</p>
        </div>
        
        <!-- 表单 -->
        <form class="register-form" @submit.prevent="handleRegister">
          <div class="form-group">
            <label class="form-label">用户名 <span class="required">*</span></label>
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
            <label class="form-label">密码 <span class="required">*</span></label>
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
                placeholder="请输入密码（至少6位）"
                class="form-input"
                autocomplete="new-password"
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
          
          <div class="form-group">
            <label class="form-label">确认密码 <span class="required">*</span></label>
            <div class="input-wrapper">
              <span class="input-icon">
                <svg viewBox="0 0 16 16" fill="none">
                  <rect x="3" y="6" width="10" height="8" rx="1" stroke="currentColor" stroke-width="1.5"/>
                  <circle cx="8" cy="10" r="1" fill="currentColor"/>
                  <path d="M5 6V4a3 3 0 116 0v2" stroke="currentColor" stroke-width="1.5"/>
                </svg>
              </span>
              <input
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="请再次输入密码"
                class="form-input"
                autocomplete="new-password"
              />
              <button type="button" class="password-toggle" @click="showConfirmPassword = !showConfirmPassword">
                <svg v-if="showConfirmPassword" viewBox="0 0 16 16" fill="none">
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
          
          <div class="form-row">
            <div class="form-group half">
              <label class="form-label">邮箱</label>
              <input
                v-model="form.email"
                type="email"
                placeholder="请输入邮箱"
                class="form-input plain"
                autocomplete="email"
              />
            </div>
            <div class="form-group half">
              <label class="form-label">手机号</label>
              <input
                v-model="form.phone"
                type="tel"
                placeholder="请输入手机号"
                class="form-input plain"
                autocomplete="tel"
              />
            </div>
          </div>
          
          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            <span v-else>注 册</span>
          </button>
        </form>
        
        <!-- 底部链接 -->
        <div class="register-footer">
          <span class="footer-text">已有账号？</span>
          <router-link to="/auth/login" class="login-link">立即登录</router-link>
        </div>
        
        <!-- 底部装饰 -->
        <div class="card-decoration-bottom">
          <svg viewBox="0 0 200 20" fill="none">
            <path d="M0 10 Q50 20 100 10 T200 10" stroke="var(--cinnabar)" stroke-width="1" fill="none" opacity="0.3"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()

const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
  phone: ''
})

const handleRegister = async () => {
  // 验证
  if (!form.username || !form.password) {
    alert('请填写用户名和密码')
    return
  }
  
  if (form.password.length < 6) {
    alert('密码至少需要6位')
    return
  }
  
  if (form.password !== form.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }
  
  loading.value = true
  try {
    await authApi.register({
      username: form.username,
      password: form.password,
      email: form.email || undefined,
      phone: form.phone || undefined
    })
    
    alert('注册成功！请登录')
    router.push('/auth/login')
  } catch (error: any) {
    console.error(error)
    alert(error?.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  position: relative;
  overflow: hidden;
}

/* 背景样式与登录页相同 */
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

/* 注册容器 */
.register-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 480px;
}

/* 注册卡片 */
.register-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
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

/* 标题 */
.register-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.register-title {
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  letter-spacing: 0.15em;
  margin: 0 0 var(--space-2);
}

.register-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin: 0;
}

/* 表单 */
.register-form {
  margin-bottom: var(--space-4);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-row {
  display: flex;
  gap: var(--space-4);
}

.form-group.half {
  flex: 1;
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.required {
  color: var(--cinnabar);
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

.form-input.plain {
  padding-left: var(--space-4);
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
  margin-top: var(--space-2);
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
.register-footer {
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.footer-text {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.login-link {
  font-size: var(--text-sm);
  color: var(--cinnabar);
  font-weight: var(--font-medium);
}

.login-link:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 480px) {
  .register-card {
    padding: var(--space-6);
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>