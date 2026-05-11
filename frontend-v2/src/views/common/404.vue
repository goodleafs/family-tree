<template>
  <div class="not-found-page">
    <div class="error-content">
      <div class="error-icon">卷</div>
      <h1 class="error-code">404</h1>
      <p class="error-message">页面不存在</p>
      <router-link to="/" class="back-btn">返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.error-content {
  max-width: 400px;
}

.error-icon {
  font-family: var(--font-title);
  font-size: 80px;
  color: var(--cinnabar);
  opacity: 0.2;
  margin-bottom: var(--space-4);
}

.error-code {
  font-family: var(--font-title);
  font-size: var(--text-6xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0 0 var(--space-2);
}

.error-message {
  font-size: var(--text-lg);
  color: var(--text-tertiary);
  margin: 0 0 var(--space-6);
}

.back-btn {
  display: inline-block;
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: white;
  background: var(--cinnabar);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: background var(--transition-fast);
}

.back-btn:hover {
  background: var(--cinnabar-dark);
}
</style>