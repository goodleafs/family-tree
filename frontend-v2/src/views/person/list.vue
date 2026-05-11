<template>
  <div class="person-list-page">
    <div class="page-header">
      <h1 class="page-title">成员管理</h1>
    </div>
    
    <div class="guide-card">
      <div class="guide-icon">👥</div>
      <h2 class="guide-title">请先选择家族</h2>
      <p class="guide-desc">
        成员管理需要在家族详情页面中进行。请先选择一个家族，然后在该家族的"成员列表"中管理成员。
      </p>
      <router-link to="/families" class="guide-btn">
        <svg viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="4" r="2.5" stroke="currentColor" stroke-width="1.5"/>
          <circle cx="4" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/>
          <circle cx="12" cy="10" r="2" stroke="currentColor" stroke-width="1.5"/>
          <path d="M6 6l-1 2M10 6l1 2" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        前往家族列表
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.person-list-page {
  max-width: 800px;
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

.guide-card {
  padding: var(--space-12);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
  text-align: center;
}

.guide-icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.guide-title {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin: 0 0 var(--space-3);
}

.guide-desc {
  font-size: var(--text-base);
  color: var(--text-tertiary);
  line-height: var(--leading-relaxed);
  margin: 0 0 var(--space-6);
}

.guide-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: white;
  background: var(--cinnabar);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: background var(--transition-fast);
}

.guide-btn:hover {
  background: var(--cinnabar-dark);
}

.guide-btn svg {
  width: 20px;
  height: 20px;
}

@media (max-width: 768px) {
  .guide-card { padding: var(--space-5); }
}
</style>