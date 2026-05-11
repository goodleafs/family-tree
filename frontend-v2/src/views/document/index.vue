<template>
  <div class="document-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push(`/families/${familyId}`)">
        <svg viewBox="0 0 16 16" fill="none"><path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/></svg>
        返回
      </button>
      <h1 class="page-title">文献库</h1>
      <button class="upload-btn" @click="showUploadDialog = true">
        <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
        上传文献
      </button>
    </div>

    <!-- 统计卡片 -->
    <div v-if="overview" class="stats-row">
      <div class="stat-card"><span class="stat-val">{{ overview.total }}</span><span class="stat-lbl">文献总数</span></div>
      <div class="stat-card"><span class="stat-val">{{ overview.pdf_count }}</span><span class="stat-lbl">PDF文档</span></div>
      <div class="stat-card"><span class="stat-val">{{ overview.image_count }}</span><span class="stat-lbl">图片文献</span></div>
      <div class="stat-card"><span class="stat-val">{{ overview.categories.length }}</span><span class="stat-lbl">分类数</span></div>
    </div>

    <!-- 分类标签 -->
    <div v-if="overview && overview.categories.length" class="categories-row">
      <button v-for="cat in overview.categories" :key="cat.category" class="cat-tag" :class="{ active: currentCategory === cat.category }" @click="toggleCategory(cat.category)">
        {{ categoryMap[cat.category] || cat.category }} ({{ cat.count }})
      </button>
    </div>

    <!-- 搜索和列表 -->
    <div class="toolbar">
      <input v-model="searchQuery" placeholder="搜索文献标题..." class="search-input" @keyup.enter="fetchDocs" />
      <span class="doc-count">共 {{ total }} 篇</span>
    </div>

    <div v-if="docs.length === 0" class="empty-hint">
      <div class="empty-icon">📄</div>
      <p>暂无文献</p>
    </div>

    <div v-else class="docs-table">
      <div class="table-header">
        <div class="th-preview">预览</div>
        <div class="th-title">标题</div>
        <div class="th-cat">分类</div>
        <div class="th-author">作者</div>
        <div class="th-type">类型</div>
        <div class="th-size">大小</div>
        <div class="th-actions">操作</div>
      </div>
      <div class="table-body">
        <div v-for="doc in docs" :key="doc.id" class="table-row">
          <div class="td-preview">
            <div v-if="doc.file_type === 'image'" class="preview-img" @click="previewDoc = doc; showPreview = true">
              <img :src="doc.file_url" alt="" />
            </div>
            <div v-else class="preview-icon" @click="previewDoc = doc; showPreview = true">
              <svg viewBox="0 0 16 16" fill="none"><path d="M4 2h6l3 3v9a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="#e6a23c" stroke-width="1.5"/><path d="M10 2v3h3" stroke="#e6a23c" stroke-width="1.5"/></svg>
            </div>
          </div>
          <div class="td-title">{{ doc.title }}</div>
          <div class="td-cat"><span class="cat-badge">{{ (doc.category && categoryMap[doc.category]) || doc.category }}</span></div>
          <div class="td-author">{{ doc.author || '-' }}</div>
          <div class="td-type">
            <span v-if="doc.file_type === 'pdf'" class="type-pdf">PDF</span>
            <span v-else-if="doc.file_type === 'image'" class="type-img">图片</span>
            <span v-else class="type-other">{{ doc.file_ext }}</span>
          </div>
          <div class="td-size">{{ formatSize(doc.file_size) }}</div>
          <div class="td-actions">
            <button class="action-btn" @click="previewDoc = doc; showPreview = true">预览</button>
            <button class="action-btn edit" @click="openEdit(doc)">编辑</button>
            <button class="action-btn danger" @click="handleDelete(doc)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <div class="dialog-overlay" v-if="showUploadDialog" @click="showUploadDialog = false">
      <div class="dialog wide" @click.stop>
        <div class="dialog-header"><h2>上传文献</h2><button class="close-btn" @click="showUploadDialog = false">×</button></div>
        <div class="dialog-body">
          <div class="upload-zone" @click="triggerFileInput()">
            <input id="doc-file-input" type="file" accept=".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.txt" style="display:none" @change="onFileChange" />
            <svg viewBox="0 0 24 24" fill="none"><path d="M12 4v16M4 12h16" stroke="currentColor" stroke-width="2"/></svg>
            <p v-if="!uploadFile">点击选择文件（PDF、图片、Word）</p>
            <p v-else>{{ uploadFile.name }}</p>
          </div>
          <div class="form-row">
            <div class="form-group flex-2"><label>标题 <span class="required">*</span></label><input v-model="form.title" placeholder="文献标题" /></div>
            <div class="form-group"><label>分类</label>
              <select v-model="form.category">
                <option value="">请选择</option><option value="genealogy">老谱扫描</option><option value="contract">契约文书</option><option value="writing">著作文献</option><option value="other">其他</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group"><label>作者</label><input v-model="form.author" placeholder="可选" /></div>
            <div class="form-group"><label>文献日期</label><input v-model="form.docDate" placeholder="如：光绪十五年" /></div>
          </div>
          <div class="form-group"><label>描述</label><textarea v-model="form.description" rows="2" placeholder="可选"></textarea></div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showUploadDialog = false">取消</button>
          <button class="btn-submit" :disabled="uploading" @click="handleUpload">{{ uploading ? '上传中...' : '上传' }}</button>
        </div>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <div class="dialog-overlay" v-if="showEditDialog" @click="showEditDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header"><h2>编辑文献</h2><button class="close-btn" @click="showEditDialog = false">×</button></div>
        <div class="dialog-body">
          <div class="form-group"><label>标题</label><input v-model="editForm.title" /></div>
          <div class="form-group"><label>分类</label>
            <select v-model="editForm.category">
              <option value="genealogy">老谱扫描</option><option value="contract">契约文书</option><option value="writing">著作文献</option><option value="other">其他</option>
            </select>
          </div>
          <div class="form-group"><label>作者</label><input v-model="editForm.author" /></div>
          <div class="form-group"><label>文献日期</label><input v-model="editForm.docDate" /></div>
          <div class="form-group"><label>描述</label><textarea v-model="editForm.description" rows="2"></textarea></div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showEditDialog = false">取消</button>
          <button class="btn-submit" @click="handleEdit">保存</button>
        </div>
      </div>
    </div>

    <!-- 预览对话框 -->
    <div class="dialog-overlay fullscreen" v-if="showPreview && previewDoc" @click="showPreview = false">
      <div class="preview-content" @click.stop>
        <div class="preview-header">
          <h3>{{ previewDoc.title }}</h3>
          <button class="close-btn" @click="showPreview = false">×</button>
        </div>
        <div class="preview-body">
          <img v-if="previewDoc.file_type === 'image'" :src="previewDoc.file_url" class="preview-image" />
          <iframe v-else-if="previewDoc.file_type === 'pdf'" :src="previewDoc.file_url" class="preview-pdf"></iframe>
          <div v-else class="preview-unsupported">
            <p>暂不支持在线预览此文件类型</p>
            <a :href="previewDoc.file_url" target="_blank" class="btn-submit" style="text-decoration:none;display:inline-block;margin-top:var(--space-4)">下载查看</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { documentApi } from '@/api/document'
import type { Document, DocumentOverview } from '@/types'

const route = useRoute()
const familyId = parseInt(route.params.id as string)

const overview = ref<DocumentOverview | null>(null)
const docs = ref<Document[]>([])
const total = ref(0)
const currentCategory = ref('')
const searchQuery = ref('')

const showUploadDialog = ref(false)
const uploadFile = ref<File | null>(null)
const uploading = ref(false)
const form = ref({ title: '', description: '', author: '', docDate: '', category: '' })

const showEditDialog = ref(false)
const editingDoc = ref<Document | null>(null)
const editForm = ref({ title: '', description: '', author: '', docDate: '', category: '' })

const showPreview = ref(false)
const previewDoc = ref<Document | null>(null)

const categoryMap: Record<string, string> = { genealogy: '老谱扫描', contract: '契约文书', writing: '著作文献', other: '其他', '': '' }

const fetchData = async () => {
  try {
    overview.value = await documentApi.getOverview(familyId)
    await fetchDocs()
  } catch (e) { console.error(e) }
}

const fetchDocs = async () => {
  const res = await documentApi.getDocuments(familyId, {
    category: currentCategory.value || undefined,
    search: searchQuery.value || undefined
  })
  docs.value = res.items
  total.value = res.total
}

const toggleCategory = (cat: string) => {
  currentCategory.value = currentCategory.value === cat ? '' : cat
  fetchDocs()
}

const triggerFileInput = () => {
  (document.getElementById('doc-file-input') as HTMLInputElement)?.click()
}
const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.length) {
    uploadFile.value = input.files[0]
    if (!form.value.title) form.value.title = uploadFile.value.name.replace(/\.[^.]+$/, '')
  }
}

const handleUpload = async () => {
  if (!uploadFile.value || !form.value.title) return
  uploading.value = true
  try {
    await documentApi.uploadDocument(familyId, uploadFile.value, {
      title: form.value.title, description: form.value.description || undefined,
      author: form.value.author || undefined, document_date: form.value.docDate || undefined,
      category: form.value.category || 'other'
    })
    showUploadDialog.value = false
    uploadFile.value = null
    form.value = { title: '', description: '', author: '', docDate: '', category: '' }
    fetchData()
  } finally { uploading.value = false }
}

const openEdit = (doc: Document) => {
  editingDoc.value = doc
  editForm.value = { title: doc.title, description: doc.description || '', author: doc.author || '', docDate: doc.document_date || '', category: doc.category || '' }
  showEditDialog.value = true
}

const handleEdit = async () => {
  if (!editingDoc.value) return
  await documentApi.updateDocument(editingDoc.value.id, {
    title: editForm.value.title, description: editForm.value.description || undefined,
    author: editForm.value.author || undefined, document_date: editForm.value.docDate || undefined,
    category: editForm.value.category || undefined
  })
  showEditDialog.value = false
  fetchDocs()
}

const handleDelete = async (doc: Document) => {
  if (!confirm(`确定删除"${doc.title}"吗？`)) return
  await documentApi.deleteDocument(doc.id)
  fetchData()
}

const formatSize = (bytes?: number) => {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / (1024 * 1024)).toFixed(1) + 'MB'
}

onMounted(fetchData)
</script>

<style scoped>
.document-page { max-width: 960px; }
.page-header { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-6); }
.back-btn { display: flex; align-items: center; gap: var(--space-1); padding: var(--space-2) var(--space-3); background: none; border: 1px solid var(--border-primary); border-radius: var(--radius-md); color: var(--text-secondary); font-size: var(--text-sm); cursor: pointer; }
.back-btn svg { width: 14px; height: 14px; }
.page-title { flex: 1; font-family: var(--font-title); font-size: var(--text-2xl); margin: 0; }
.upload-btn { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); font-size: var(--text-sm); cursor: pointer; }
.upload-btn svg { width: 14px; height: 14px; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-4); margin-bottom: var(--space-5); }
.stat-card { background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: var(--radius-lg); padding: var(--space-5); text-align: center; }
.stat-val { display: block; font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--cinnabar); }
.stat-lbl { font-size: var(--text-sm); color: var(--text-tertiary); margin-top: var(--space-1); }

.categories-row { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-4); }
.cat-tag { padding: var(--space-1) var(--space-4); border: 1px solid var(--border-primary); border-radius: var(--radius-full); background: none; font-size: var(--text-sm); color: var(--text-secondary); cursor: pointer; }
.cat-tag.active { border-color: var(--cinnabar); color: var(--cinnabar); background: var(--cinnabar-pale); }

.toolbar { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-4); }
.search-input { flex: 1; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-sm); }
.search-input:focus { outline: none; border-color: var(--cinnabar); }
.doc-count { font-size: var(--text-sm); color: var(--text-tertiary); }

.docs-table { border: 1px solid var(--border-primary); border-radius: var(--radius-lg); overflow: hidden; }
.table-header { display: flex; background: var(--bg-secondary); font-size: var(--text-xs); color: var(--text-tertiary); padding: var(--space-3) var(--space-4); font-weight: var(--font-medium); }
.table-row { display: flex; padding: var(--space-3) var(--space-4); border-top: 1px solid var(--border-primary); align-items: center; font-size: var(--text-sm); }
.table-row:hover { background: var(--bg-secondary); }
.th-preview, .td-preview { width: 60px; flex-shrink: 0; }
.th-title, .td-title { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.th-cat, .td-cat { width: 100px; }
.th-author, .td-author { width: 100px; }
.th-type, .td-type { width: 70px; }
.th-size, .td-size { width: 80px; }
.th-actions, .td-actions { width: 160px; display: flex; gap: var(--space-2); }

.preview-img { width: 40px; height: 40px; border-radius: var(--radius-sm); overflow: hidden; cursor: pointer; }
.preview-img img { width: 100%; height: 100%; object-fit: cover; }
.preview-icon { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.preview-icon svg { width: 28px; height: 28px; }

.cat-badge { padding: 2px var(--space-2); background: var(--bg-secondary); border-radius: var(--radius-sm); font-size: var(--text-xs); }
.type-pdf { color: #e6a23c; font-weight: var(--font-medium); }
.type-img { color: var(--bamboo); }
.type-other { color: var(--text-tertiary); }
.action-btn { background: none; border: none; font-size: var(--text-xs); color: var(--text-secondary); cursor: pointer; padding: 0; }
.action-btn:hover { color: var(--cinnabar); }
.action-btn.edit:hover { color: var(--indigo); }
.action-btn.danger { color: var(--cinnabar); }

.empty-hint { text-align: center; padding: var(--space-10); color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: var(--space-4); }

/* Dialog/Form */
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog-overlay.fullscreen { align-items: stretch; padding: var(--space-6); }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 480px; max-width: 90vw; box-shadow: var(--shadow-lg); max-height: 90vh; overflow-y: auto; }
.dialog.wide { width: 640px; }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-5); border-bottom: 1px solid var(--border-primary); }
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

.upload-zone { border: 2px dashed var(--border-primary); border-radius: var(--radius-md); padding: var(--space-6); text-align: center; cursor: pointer; color: var(--text-tertiary); margin-bottom: var(--space-4); }
.upload-zone svg { width: 28px; height: 28px; }
.upload-zone:hover { border-color: var(--cinnabar); color: var(--cinnabar); }

.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; }
.btn-submit:disabled { opacity: 0.6; }

/* Preview */
.preview-content { background: var(--bg-primary); border-radius: var(--radius-lg); width: 90vw; height: 90vh; display: flex; flex-direction: column; overflow: hidden; }
.preview-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--border-primary); }
.preview-header h3 { margin: 0; }
.preview-body { flex: 1; display: flex; align-items: center; justify-content: center; background: var(--bg-secondary); overflow: auto; }
.preview-image { max-width: 100%; max-height: 100%; object-fit: contain; }
.preview-pdf { width: 100%; height: 100%; border: none; }
.preview-unsupported { text-align: center; color: var(--text-tertiary); }
</style>
