<template>
  <div class="biography-tab">
    <div class="panel-header">
      <h3>人物传记</h3>
      <div class="header-actions">
        <button class="add-btn" @click="openCreate">
          <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
          创建传记
        </button>
        <router-link :to="`/families/${familyId}/biographies`" class="view-full-btn">查看全部</router-link>
      </div>
    </div>

    <div v-if="loading" class="loading-hint">加载中...</div>

    <div v-else-if="biographies.length === 0" class="empty-hint">
      <div class="empty-icon">📖</div>
      <p>暂无传记</p>
    </div>

    <div v-else class="bio-grid">
      <div v-for="bio in biographies" :key="bio.id" class="bio-card" @click="$router.push(`/families/${familyId}/biographies/${bio.id}`)">
        <div class="bio-avatar">
          <img v-if="bio.person.photo_url" :src="bio.person.photo_url" alt="" />
          <span v-else class="avatar-text">{{ bio.person.name.charAt(0) }}</span>
        </div>
        <div class="bio-info">
          <div class="bio-name">{{ bio.title || bio.person.name + '传' }}</div>
          <div class="bio-person">{{ bio.person.name }}<span v-if="bio.person.generation_number"> · 第{{ bio.person.generation_number }}代</span></div>
        </div>
        <div class="bio-views">{{ bio.views_count }} 次浏览</div>
      </div>
    </div>

    <!-- 创建对话框 -->
    <div class="dialog-overlay" v-if="showCreateDialog" @click="showCreateDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header"><h2>创建传记</h2><button class="close-btn" @click="showCreateDialog = false">×</button></div>
        <div class="dialog-body">
          <div class="form-group"><label>选择人物 <span class="required">*</span></label>
            <select v-model="selectedPersonId">
              <option :value="0">请选择</option>
              <option v-for="p in eligiblePersons" :key="p.id" :value="p.id">{{ p.name }}{{ p.generation_number ? '（第'+p.generation_number+'代）' : '' }}</option>
            </select>
          </div>
          <div class="form-group"><label>传记标题</label><input v-model="form.title" placeholder="如：XX公传" /></div>
          <div class="form-group"><label>传记正文 <span class="required">*</span></label><textarea v-model="form.content" rows="6" placeholder="请书写传记正文（支持HTML）"></textarea></div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showCreateDialog = false">取消</button>
          <button class="btn-submit" :disabled="saving" @click="handleCreate">{{ saving ? '创建中...' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { biographyApi } from '@/api/biography'
import type { BiographyListItem } from '@/types'

const props = defineProps<{ familyId: number }>()

const biographies = ref<BiographyListItem[]>([])
const loading = ref(true)

const showCreateDialog = ref(false)
const eligiblePersons = ref<any[]>([])
const selectedPersonId = ref(0)
const saving = ref(false)
const form = ref({ title: '', content: '' })

const fetchBios = async () => {
  try {
    const res = await biographyApi.getBiographies(props.familyId, { limit: 8 })
    biographies.value = res.items
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const openCreate = async () => {
  showCreateDialog.value = true
  selectedPersonId.value = 0
  form.value = { title: '', content: '' }
  eligiblePersons.value = await biographyApi.getEligiblePersons(props.familyId)
}

const handleCreate = async () => {
  if (!selectedPersonId.value || !form.value.content) return
  saving.value = true
  try {
    await biographyApi.createBiography({
      person_id: selectedPersonId.value, family_id: props.familyId,
      title: form.value.title || undefined, content: form.value.content
    })
    showCreateDialog.value = false
    fetchBios()
  } finally { saving.value = false }
}

onMounted(fetchBios)
</script>

<style scoped>
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-4); }
.panel-header h3 { margin: 0; font-size: var(--text-lg); }
.header-actions { display: flex; gap: var(--space-3); align-items: center; }
.add-btn { display: flex; align-items: center; gap: var(--space-1); padding: var(--space-1) var(--space-4); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); font-size: var(--text-sm); cursor: pointer; }
.add-btn svg { width: 12px; height: 12px; }
.view-full-btn { font-size: var(--text-sm); color: var(--cinnabar); text-decoration: none; }
.loading-hint { text-align: center; padding: var(--space-6); color: var(--text-tertiary); }
.empty-hint { text-align: center; padding: var(--space-6); color: var(--text-tertiary); }
.empty-icon { font-size: 36px; margin-bottom: var(--space-2); }
.empty-hint p { margin: 0; }

.bio-grid { display: flex; flex-direction: column; gap: var(--space-2); }
.bio-card { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; transition: all var(--transition-fast); }
.bio-card:hover { border-color: var(--border-secondary); box-shadow: var(--shadow-sm); }
.bio-avatar { width: 44px; height: 44px; border-radius: var(--radius-md); overflow: hidden; flex-shrink: 0; background: var(--bg-secondary); display: flex; align-items: center; justify-content: center; }
.bio-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-text { font-size: var(--text-lg); color: var(--text-tertiary); }
.bio-info { flex: 1; min-width: 0; }
.bio-name { font-size: var(--text-sm); font-weight: var(--font-medium); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bio-person { font-size: var(--text-xs); color: var(--text-tertiary); }
.bio-views { font-size: var(--text-xs); color: var(--text-tertiary); white-space: nowrap; }

.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 500px; max-width: 90vw; box-shadow: var(--shadow-lg); }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--border-primary); }
.dialog-header h2 { margin: 0; font-size: var(--text-lg); }
.close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
.dialog-body { padding: var(--space-5); max-height: 60vh; overflow-y: auto; }
.dialog-footer { display: flex; justify-content: flex-end; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border-primary); }
.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; font-size: var(--text-sm); margin-bottom: var(--space-2); }
.form-group input, .form-group textarea, .form-group select { width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-base); font-family: var(--font-body); background: var(--bg-primary); box-sizing: border-box; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--cinnabar); }
.required { color: var(--cinnabar); }
.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); }
.btn-submit:disabled { opacity: 0.6; }
</style>
