<template>
  <div class="document-tab">
    <div class="panel-header">
      <h3>文献库</h3>
      <div class="header-actions">
        <button class="add-btn" @click="showUpload = true">
          <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
          上传文献
        </button>
        <router-link :to="`/families/${familyId}/documents`" class="view-full-btn">查看全部</router-link>
      </div>
    </div>

    <div v-if="loading" class="loading-hint">加载中...</div>

    <div v-else-if="documents.length === 0" class="empty-hint">
      <div class="empty-icon">📄</div>
      <p>暂无文献</p>
    </div>

    <div v-else class="doc-list">
      <div class="doc-header">
        <span class="dh-title">标题</span>
        <span class="dh-cat">分类</span>
        <span class="dh-type">类型</span>
        <span class="dh-date">上传时间</span>
      </div>
      <div v-for="doc in documents" :key="doc.id" class="doc-row" @click="$router.push(`/families/${familyId}/documents`)" :title="doc.title">
        <span class="dh-title">{{ doc.title }}</span>
        <span class="dh-cat"><span class="cat-badge">{{ (doc.category && categoryMap[doc.category]) || doc.category || '其他' }}</span></span>
        <span class="dh-type">
          <span v-if="doc.file_type === 'pdf'" class="type-pdf">PDF</span>
          <span v-else-if="doc.file_type === 'image'" class="type-img">图片</span>
          <span v-else class="type-other">{{ doc.file_ext }}</span>
        </span>
        <span class="dh-date">{{ formatDate(doc.created_at) }}</span>
      </div>
    </div>

    <!-- 上传对话框 -->
    <div class="dialog-overlay" v-if="showUpload" @click="showUpload = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header"><h2>上传文献</h2><button class="close-btn" @click="showUpload = false">×</button></div>
        <div class="dialog-body">
          <div class="upload-zone" @click="triggerInput">
            <input id="doc-tab-input" type="file" accept=".pdf,.jpg,.jpeg,.png,.gif" style="display:none" @change="onFileChange" />
            <svg viewBox="0 0 24 24" fill="none"><path d="M12 4v16M4 12h16" stroke="currentColor" stroke-width="2"/></svg>
            <p>{{ file ? file.name : '点击选择文件' }}</p>
          </div>
          <div class="form-row">
            <div class="form-group flex-2"><label>标题 <span class="required">*</span></label><input v-model="title" placeholder="文献标题" /></div>
            <div class="form-group"><label>分类</label>
              <select v-model="category">
                <option value="genealogy">老谱扫描</option><option value="contract">契约文书</option><option value="writing">著作文献</option><option value="other">其他</option>
              </select>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showUpload = false">取消</button>
          <button class="btn-submit" :disabled="saving" @click="handleUpload">{{ saving ? '上传中...' : '上传' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { documentApi } from '@/api/document'
import type { Document } from '@/types'

const props = defineProps<{ familyId: number }>()

const documents = ref<Document[]>([])
const loading = ref(true)

const showUpload = ref(false)
const file = ref<File>()
const title = ref('')
const category = ref('genealogy')
const saving = ref(false)

const categoryMap: Record<string, string> = { genealogy: '老谱扫描', contract: '契约文书', writing: '著作文献', other: '其他' }

const fetchDocs = async () => {
  try {
    const res = await documentApi.getDocuments(props.familyId, { limit: 10 })
    documents.value = res.items
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const triggerInput = () => { (document.getElementById('doc-tab-input') as HTMLInputElement)?.click() }
const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.length) {
    const f = input.files[0]
    file.value = f
    if (!title.value) title.value = f.name.replace(/\.[^.]+$/, '')
  }
}

const handleUpload = async () => {
  if (!file.value || !title.value) return
  saving.value = true
  try {
    await documentApi.uploadDocument(props.familyId, file.value, { title: title.value, category: category.value || 'other' })
    showUpload.value = false
    file.value = undefined
    title.value = ''
    category.value = 'genealogy'
    fetchDocs()
  } finally { saving.value = false }
}

const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

onMounted(fetchDocs)
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

.doc-list { border: 1px solid var(--border-primary); border-radius: var(--radius-md); overflow: hidden; }
.doc-header, .doc-row { display: flex; padding: var(--space-2) var(--space-3); font-size: var(--text-sm); }
.doc-header { background: var(--bg-secondary); color: var(--text-tertiary); font-size: var(--text-xs); }
.doc-row { border-top: 1px solid var(--border-primary); cursor: pointer; }
.doc-row:hover { background: var(--bg-secondary); }
.dh-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dh-cat { width: 80px; }
.dh-type { width: 60px; }
.dh-date { width: 90px; color: var(--text-tertiary); }
.cat-badge { font-size: var(--text-xs); padding: 1px var(--space-2); background: var(--bg-secondary); border-radius: var(--radius-sm); }
.type-pdf { color: #e6a23c; font-weight: var(--font-medium); }
.type-img { color: var(--bamboo); }
.type-other { color: var(--text-tertiary); }

.upload-zone { border: 2px dashed var(--border-primary); border-radius: var(--radius-md); padding: var(--space-5); text-align: center; cursor: pointer; color: var(--text-tertiary); margin-bottom: var(--space-4); }
.upload-zone svg { width: 24px; height: 24px; }
.upload-zone:hover { border-color: var(--cinnabar); color: var(--cinnabar); }

.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 480px; max-width: 90vw; box-shadow: var(--shadow-lg); }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--border-primary); }
.dialog-header h2 { margin: 0; font-size: var(--text-lg); }
.close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
.dialog-body { padding: var(--space-5); }
.dialog-footer { display: flex; justify-content: flex-end; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border-primary); }
.form-row { display: flex; gap: var(--space-4); }
.form-group { margin-bottom: var(--space-4); flex: 1; }
.form-group.flex-2 { flex: 2; }
.form-group label { display: block; font-size: var(--text-sm); margin-bottom: var(--space-2); }
.form-group input, .form-group textarea, .form-group select { width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-base); font-family: var(--font-body); background: var(--bg-primary); box-sizing: border-box; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--cinnabar); }
.required { color: var(--cinnabar); }
.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); }
.btn-submit:disabled { opacity: 0.6; }
</style>
