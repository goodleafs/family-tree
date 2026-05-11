<template>
  <div class="bio-detail-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push(`/families/${familyId}/biographies`)">
        <svg viewBox="0 0 16 16" fill="none"><path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/></svg>
        返回
      </button>
      <h1 class="page-title">{{ biography?.title || '传记详情' }}</h1>
      <div class="header-actions" v-if="biography">
        <button v-if="!editMode" class="edit-btn" @click="startEdit">
          <svg viewBox="0 0 16 16" fill="none"><path d="M11 2l3 3-9 9H2v-3l9-9z" stroke="currentColor" stroke-width="1.5"/></svg>
          编辑
        </button>
        <button v-if="editMode" class="save-btn" @click="saveEdit">
          <svg viewBox="0 0 16 16" fill="none"><path d="M13 4L6 11l-3-3" stroke="currentColor" stroke-width="1.5"/></svg>
          保存
        </button>
        <button v-if="editMode" class="cancel-btn" @click="cancelEdit">取消</button>
        <button class="danger-btn" @click="handleDelete">
          <svg viewBox="0 0 16 16" fill="none"><path d="M3 4h10M6 4V2h4v2M4 4v10h8V4" stroke="currentColor" stroke-width="1.5"/></svg>
          删除
        </button>
      </div>
    </div>

    <div v-if="!biography && !loading" class="empty-hint">
      <div class="empty-icon">📖</div>
      <p>传记不存在</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-if="biography && !loading">
      <!-- 人物信息卡片 -->
      <div class="person-card">
        <div class="person-brief">
          <div class="person-avatar">
            <img v-if="biography.portrait_url || biography.person.photo_url" :src="biography.portrait_url || biography.person.photo_url" alt="" />
            <span v-else class="avatar-text">{{ biography.person.name.charAt(0) }}</span>
          </div>
          <div class="person-info">
            <h2>{{ biography.title || biography.person.name + '传' }}</h2>
            <p v-if="biography.subtitle" class="subtitle">{{ biography.subtitle }}</p>
            <div class="person-tags">
              <span class="person-link" @click="$router.push(`/persons/${biography.person.id}`)">{{ biography.person.name }}</span>
              <span v-if="biography.person.generation_number" class="gen-tag">第{{ biography.person.generation_number }}代</span>
              <span v-if="biography.person.branch_name" class="branch-tag">{{ biography.person.branch_name }}</span>
              <span v-if="biography.person.birth_date || biography.person.death_date" class="life-range">
                {{ biography.person.birth_date || '?' }} ~ {{ biography.person.death_date || '?' }}
              </span>
            </div>
          </div>
          <div class="views-count">
            <svg viewBox="0 0 16 16" fill="none"><path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/></svg>
            {{ biography.views_count }}
          </div>
        </div>
      </div>

      <!-- 编辑模式 -->
      <div v-if="editMode" class="edit-section">
        <div class="form-group"><label>传记标题</label><input v-model="editForm.title" /></div>
        <div class="form-group"><label>副标题</label><input v-model="editForm.subtitle" /></div>
        <div class="form-group"><label>摘要</label><textarea v-model="editForm.summary" rows="3"></textarea></div>
        <div class="form-group"><label>传记正文</label><textarea v-model="editForm.content" rows="15" style="font-family:var(--font-body);"></textarea><span class="form-hint">支持HTML格式</span></div>
        <div class="form-group"><label>主要成就</label><textarea v-model="editForm.achievements" rows="5"></textarea></div>
        <div class="form-group"><label class="switch-label"><input type="checkbox" v-model="editForm.isPublished" /> 已发布</label></div>
      </div>

      <!-- 展示模式 -->
      <div v-else class="bio-body">
        <div v-if="biography.summary" class="bio-section">
          <div class="section-label">导语</div>
          <p class="summary-text">{{ biography.summary }}</p>
        </div>
        <div class="bio-section">
          <div class="section-label">传记正文</div>
          <div class="content-text" v-html="biography.content"></div>
        </div>
        <div v-if="biography.achievements" class="bio-section">
          <div class="section-label">主要成就</div>
          <div class="content-text" v-html="biography.achievements"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { biographyApi } from '@/api/biography'
import type { Biography } from '@/types'

const route = useRoute()
const router = useRouter()
const biographyId = parseInt(route.params.bioId as string)
const familyId = parseInt(route.params.id as string)

const biography = ref<Biography | null>(null)
const loading = ref(true)
const editMode = ref(false)
const editForm = ref({ title: '', subtitle: '', summary: '', content: '', achievements: '', isPublished: true })

const fetchBiography = async () => {
  loading.value = true
  try {
    biography.value = await biographyApi.getBiography(biographyId)
    if (biography.value) {
      editForm.value = {
        title: biography.value.title || '', subtitle: biography.value.subtitle || '',
        summary: biography.value.summary || '', content: biography.value.content,
        achievements: biography.value.achievements || '', isPublished: biography.value.is_published
      }
    }
  } catch (e) {
    router.push(`/families/${familyId}/biographies`)
  } finally { loading.value = false }
}

const startEdit = () => { editMode.value = true }
const cancelEdit = () => {
  editMode.value = false
  if (biography.value) {
    editForm.value = {
      title: biography.value.title || '', subtitle: biography.value.subtitle || '',
      summary: biography.value.summary || '', content: biography.value.content,
      achievements: biography.value.achievements || '', isPublished: biography.value.is_published
    }
  }
}
const saveEdit = async () => {
  try {
    biography.value = await biographyApi.updateBiography(biographyId, {
      title: editForm.value.title || undefined, subtitle: editForm.value.subtitle || undefined,
      summary: editForm.value.summary || undefined, content: editForm.value.content,
      achievements: editForm.value.achievements || undefined, is_published: editForm.value.isPublished
    })
    editMode.value = false
  } catch (e) { console.error(e) }
}
const handleDelete = async () => {
  if (!confirm('确定删除此传记吗？')) return
  await biographyApi.deleteBiography(biographyId)
  router.push(`/families/${familyId}/biographies`)
}

onMounted(fetchBiography)
</script>

<style scoped>
.bio-detail-page { max-width: 800px; margin: 0 auto; }
.page-header { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-6); }
.back-btn { display: flex; align-items: center; gap: var(--space-1); padding: var(--space-2) var(--space-3); background: none; border: 1px solid var(--border-primary); border-radius: var(--radius-md); color: var(--text-secondary); font-size: var(--text-sm); cursor: pointer; }
.back-btn svg { width: 14px; height: 14px; }
.page-title { flex: 1; font-family: var(--font-title); margin: 0; }
.header-actions { display: flex; gap: var(--space-2); }
.edit-btn, .save-btn, .cancel-btn, .danger-btn { display: flex; align-items: center; gap: var(--space-1); padding: var(--space-2) var(--space-4); border-radius: var(--radius-md); font-size: var(--text-sm); cursor: pointer; border: 1px solid transparent; }
.edit-btn { background: var(--indigo); color: white; }
.save-btn { background: var(--bamboo); color: white; }
.cancel-btn { background: var(--bg-secondary); border-color: var(--border-primary); }
.danger-btn { color: var(--cinnabar); border: 1px solid var(--cinnabar); background: none; }
.edit-btn svg, .save-btn svg, .danger-btn svg { width: 14px; height: 14px; }

.person-card { background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: var(--radius-lg); padding: var(--space-6); margin-bottom: var(--space-6); }
.person-brief { display: flex; gap: var(--space-5); position: relative; }
.person-avatar { width: 80px; height: 80px; border-radius: var(--radius-md); overflow: hidden; flex-shrink: 0; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; }
.person-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-text { font-size: var(--text-2xl); color: var(--text-tertiary); font-weight: var(--font-semibold); }
.person-info { flex: 1; }
.person-info h2 { margin: 0 0 var(--space-1); font-size: var(--text-2xl); }
.subtitle { margin: 0 0 var(--space-2); color: var(--text-tertiary); font-size: var(--text-sm); }
.person-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); font-size: var(--text-sm); align-items: center; }
.person-link { color: var(--cinnabar); cursor: pointer; font-weight: var(--font-medium); }
.gen-tag, .branch-tag { padding: 2px var(--space-2); background: var(--bg-secondary); border-radius: var(--radius-sm); font-size: var(--text-xs); }
.life-range { color: var(--text-tertiary); font-size: var(--text-xs); }
.views-count { position: absolute; top: 0; right: 0; display: flex; align-items: center; gap: var(--space-1); font-size: var(--text-sm); color: var(--text-tertiary); }
.views-count svg { width: 16px; height: 16px; }

.bio-section { background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: var(--radius-lg); padding: var(--space-5); margin-bottom: var(--space-5); }
.section-label { font-size: var(--text-sm); font-weight: var(--font-semibold); color: var(--text-primary); margin-bottom: var(--space-3); padding-bottom: var(--space-2); border-bottom: 1px solid var(--border-primary); }
.summary-text { line-height: 1.8; color: var(--text-secondary); font-size: var(--text-base); }
.content-text { line-height: 1.9; color: var(--text-primary); font-size: var(--text-base); }
.content-text :deep(p) { margin-bottom: var(--space-3); }

/* Edit mode */
.edit-section { background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: var(--radius-lg); padding: var(--space-5); }
.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; font-size: var(--text-sm); margin-bottom: var(--space-2); font-weight: var(--font-medium); }
.form-group input, .form-group textarea { width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-base); background: var(--bg-primary); box-sizing: border-box; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--cinnabar); }
.form-hint { font-size: var(--text-xs); color: var(--text-tertiary); margin-top: var(--space-1); display: block; }
.switch-label { display: flex; align-items: center; gap: var(--space-2); cursor: pointer; }
.switch-label input { width: auto; }

.loading-state { text-align: center; padding: var(--space-10); color: var(--text-tertiary); }
.empty-hint { text-align: center; padding: var(--space-10); color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: var(--space-4); }
.loading-spinner { width: 32px; height: 32px; border: 3px solid var(--border-primary); border-top-color: var(--cinnabar); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto var(--space-4); }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .person-brief { flex-direction: column; align-items: center; text-align: center; }
  .person-tags { justify-content: center; }
  .views-count { position: static; margin-top: var(--space-2); }
  .header-actions { flex-wrap: wrap; justify-content: flex-start; }
  .page-title { font-size: var(--text-xl); }
}
</style>
