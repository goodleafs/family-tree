<template>
  <div class="bio-list-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push(`/families/${familyId}`)">
        <svg viewBox="0 0 16 16" fill="none"><path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/></svg>
        返回
      </button>
      <h1 class="page-title">人物传记</h1>
      <button class="create-btn" @click="openCreateDialog">
        <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
        创建传记
      </button>
    </div>

    <div class="toolbar">
      <input v-model="searchQuery" placeholder="搜索传记标题..." class="search-input" @keyup.enter="fetchBios" />
    </div>

    <div v-if="biographies.length === 0" class="empty-hint">
      <div class="empty-icon">📖</div>
      <p>暂无传记，创建一篇吧</p>
    </div>

    <div v-else class="bio-grid">
      <div v-for="bio in biographies" :key="bio.id" class="bio-card" @click="$router.push(`/families/${familyId}/biographies/${bio.id}`)">
        <div class="bio-header">
          <div class="bio-avatar">
            <img v-if="bio.person.photo_url" :src="bio.person.photo_url" alt="" />
            <span v-else class="avatar-text">{{ bio.person.name.charAt(0) }}</span>
          </div>
          <div class="bio-meta">
            <h4>{{ bio.title || bio.person.name + '传' }}</h4>
            <div class="bio-tags">
              <span class="bio-name">{{ bio.person.name }}</span>
              <span v-if="bio.person.generation_number" class="gen-tag">第{{ bio.person.generation_number }}代</span>
              <span v-if="bio.person.branch_name" class="branch-tag">{{ bio.person.branch_name }}</span>
            </div>
          </div>
        </div>
        <p v-if="bio.summary" class="bio-summary">{{ bio.summary }}</p>
        <div class="bio-footer">
          <span class="bio-views">
            <svg viewBox="0 0 16 16" fill="none"><path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.5"/></svg>
            {{ bio.views_count }}
          </span>
          <span class="bio-date">{{ formatDate(bio.created_at) }}</span>
          <button class="delete-btn" @click.stop="handleDelete(bio)">删除</button>
        </div>
      </div>
    </div>

    <!-- 创建传记对话框 -->
    <div class="dialog-overlay" v-if="showCreateDialog" @click="showCreateDialog = false">
      <div class="dialog wide" @click.stop>
        <div class="dialog-header"><h2>创建人物传记</h2><button class="close-btn" @click="showCreateDialog = false">×</button></div>
        <div class="dialog-body">
          <div class="form-group">
            <label>选择人物 <span class="required">*</span></label>
            <select v-model="selectedPersonId" @change="onPersonSelect(selectedPersonId)">
              <option :value="0">请选择家族成员</option>
              <option v-for="p in eligiblePersons" :key="p.id" :value="p.id">{{ p.name }}{{ p.generation_number ? '（第'+p.generation_number+'代）' : '' }}{{ p.branch_name ? ' - '+p.branch_name : '' }}</option>
            </select>
          </div>
          <div class="form-group"><label>传记标题</label><input v-model="form.title" placeholder="如：先祖XX公传" /></div>
          <div class="form-group"><label>副标题</label><input v-model="form.subtitle" placeholder="可选" /></div>
          <div class="form-group"><label>摘要</label><textarea v-model="form.summary" rows="3" placeholder="显示在列表页的摘要"></textarea></div>
          <div class="form-group"><label>传记正文 <span class="required">*</span></label><textarea v-model="form.content" rows="10" placeholder="请详细书写人物传记正文...（支持HTML格式）"></textarea></div>
          <div class="form-group"><label>主要成就</label><textarea v-model="form.achievements" rows="4" placeholder="可选"></textarea></div>
          <div class="form-group">
            <label class="switch-label"><input type="checkbox" v-model="form.isPublished" /> 发布（勾选为发布，不勾选为草稿）</label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showCreateDialog = false">取消</button>
          <button class="btn-submit" :disabled="creating" @click="handleCreate">{{ creating ? '创建中...' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { biographyApi } from '@/api/biography'
import { personApi } from '@/api/person'
import type { BiographyListItem } from '@/types'

const route = useRoute()
const familyId = parseInt(route.params.id as string)

const biographies = ref<BiographyListItem[]>([])
const searchQuery = ref('')

const showCreateDialog = ref(false)
const eligiblePersons = ref<any[]>([])
const selectedPersonId = ref(0)
const form = ref({ title: '', subtitle: '', summary: '', content: '', achievements: '', isPublished: true })
const creating = ref(false)

const fetchBios = async () => {
  const res = await biographyApi.getBiographies(familyId, { search: searchQuery.value || undefined })
  biographies.value = res.items
}

const openCreateDialog = async () => {
  showCreateDialog.value = true
  selectedPersonId.value = 0
  form.value = { title: '', subtitle: '', summary: '', content: '', achievements: '', isPublished: true }
  eligiblePersons.value = await biographyApi.getEligiblePersons(familyId)
}

const onPersonSelect = async (pid: number) => {
  if (!pid) return
  try {
    const p = await personApi.getPerson(pid)
    form.value.title = `${p.name}传`
    form.value.summary = p.biography?.substring(0, 200) || ''
  } catch (e) {}
}

const handleCreate = async () => {
  if (!selectedPersonId.value || !form.value.content) return
  creating.value = true
  try {
    await biographyApi.createBiography({
      person_id: selectedPersonId.value, family_id: familyId,
      title: form.value.title || undefined, subtitle: form.value.subtitle || undefined,
      summary: form.value.summary || undefined, content: form.value.content,
      achievements: form.value.achievements || undefined, is_published: form.value.isPublished
    })
    showCreateDialog.value = false
    fetchBios()
  } finally { creating.value = false }
}

const handleDelete = async (bio: BiographyListItem) => {
  if (!confirm(`确定删除"${bio.title || bio.person.name}"的传记吗？`)) return
  await biographyApi.deleteBiography(bio.id)
  fetchBios()
}

const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

onMounted(fetchBios)
</script>

<style scoped>
.bio-list-page { max-width: 960px; }
.page-header { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-6); }
.back-btn { display: flex; align-items: center; gap: var(--space-1); padding: var(--space-2) var(--space-3); background: none; border: 1px solid var(--border-primary); border-radius: var(--radius-md); color: var(--text-secondary); font-size: var(--text-sm); cursor: pointer; }
.back-btn svg { width: 14px; height: 14px; }
.page-title { flex: 1; font-family: var(--font-title); font-size: var(--text-2xl); margin: 0; }
.create-btn { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); font-size: var(--text-sm); cursor: pointer; }
.create-btn svg { width: 14px; height: 14px; }

.toolbar { margin-bottom: var(--space-5); }
.search-input { width: 300px; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-sm); }
.search-input:focus { outline: none; border-color: var(--cinnabar); }

.bio-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-5); }

.bio-card { background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: var(--radius-lg); padding: var(--space-5); cursor: pointer; transition: all var(--transition-fast); }
.bio-card:hover { border-color: var(--border-secondary); box-shadow: var(--shadow-md); transform: translateY(-2px); }

.bio-header { display: flex; gap: var(--space-4); margin-bottom: var(--space-4); }
.bio-avatar { width: 56px; height: 56px; border-radius: var(--radius-md); overflow: hidden; flex-shrink: 0; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; }
.bio-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-text { font-size: var(--text-xl); color: var(--text-tertiary); font-weight: var(--font-semibold); }
.bio-meta { flex: 1; min-width: 0; }
.bio-meta h4 { margin: 0 0 var(--space-1); font-size: var(--text-base); }
.bio-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); font-size: var(--text-xs); color: var(--text-tertiary); }
.bio-name { font-weight: var(--font-medium); color: var(--text-secondary); }
.gen-tag, .branch-tag { padding: 1px var(--space-2); background: var(--bg-secondary); border-radius: var(--radius-sm); }

.bio-summary { font-size: var(--text-sm); color: var(--text-secondary); line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; margin: 0 0 var(--space-4); }

.bio-footer { display: flex; align-items: center; gap: var(--space-4); font-size: var(--text-xs); color: var(--text-tertiary); border-top: 1px solid var(--border-primary); padding-top: var(--space-3); }
.bio-views { display: flex; align-items: center; gap: var(--space-1); }
.bio-views svg { width: 14px; height: 14px; }
.bio-date { flex: 1; }
.delete-btn { background: none; border: none; color: var(--cinnabar); font-size: var(--text-xs); cursor: pointer; }

.empty-hint { text-align: center; padding: var(--space-10); color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: var(--space-4); }

/* Dialog */
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 480px; max-width: 90vw; box-shadow: var(--shadow-lg); max-height: 90vh; overflow-y: auto; }
.dialog.wide { width: 680px; }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-5); border-bottom: 1px solid var(--border-primary); }
.dialog-header h2 { margin: 0; font-size: var(--text-lg); }
.close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
.dialog-body { padding: var(--space-5); }
.dialog-footer { display: flex; justify-content: flex-end; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border-primary); }
.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; font-size: var(--text-sm); margin-bottom: var(--space-2); }
.form-group input, .form-group textarea, .form-group select { width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-base); font-family: var(--font-body); background: var(--bg-primary); box-sizing: border-box; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--cinnabar); }
.required { color: var(--cinnabar); }
.switch-label { display: flex; align-items: center; gap: var(--space-2); cursor: pointer; font-size: var(--text-sm); }
.switch-label input { width: auto; }
.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; }
.btn-submit:disabled { opacity: 0.6; }
</style>
