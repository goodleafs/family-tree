<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { documentApi } from '@/api/document'
import { familyApi } from '@/api/family'
import type { Document, DocumentOverview } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const familyId = parseInt(route.params.id as string)

const family = ref<any>(null)
const documents = ref<Document[]>([])
const overview = ref<DocumentOverview | null>(null)
const loading = ref(false)

const currentCategory = ref('')
const searchQuery = ref('')
const total = ref(0)

const uploadDialog = ref(false)
const uploadFile = ref<File | null>(null)
const uploadForm = ref({
  title: '',
  description: '',
  author: '',
  document_date: '',
  tags: '',
  category: ''
})
const uploading = ref(false)

const editDialog = ref(false)
const editingDoc = ref<Document | null>(null)
const editForm = ref({ title: '', description: '', author: '', document_date: '', tags: '', category: '' })

const previewDialog = ref(false)
const previewDoc = ref<Document | null>(null)

const categoryOptions = [
  { value: 'genealogy', label: '老谱扫描' },
  { value: 'contract', label: '契约文书' },
  { value: 'writing', label: '著作文献' },
  { value: 'other', label: '其他' }
]

const categoryMap: Record<string, string> = {
  genealogy: '老谱扫描',
  contract: '契约文书',
  writing: '著作文献',
  other: '其他'
}

const filteredDocs = computed(() => {
  return documents.value
})

const fetchData = async () => {
  loading.value = true
  try {
    family.value = await familyApi.getFamily(familyId)
    overview.value = await documentApi.getOverview(familyId)
    await fetchDocuments()
  } catch (error) {
    console.error(error)
    ElMessage.error('加载文献数据失败')
  } finally {
    loading.value = false
  }
}

const fetchDocuments = async () => {
  try {
    const res = await documentApi.getDocuments(familyId, {
      category: currentCategory.value || undefined,
      search: searchQuery.value || undefined
    })
    documents.value = res.items
    total.value = res.total
  } catch (error) {
    console.error(error)
  }
}

const onCategoryChange = () => {
  fetchDocuments()
}

const onSearch = () => {
  fetchDocuments()
}

const onFileSelect = (file: File) => {
  uploadFile.value = file
  if (!uploadForm.value.title) {
    uploadForm.value.title = file.name.replace(/\.[^.]+$/, '')
  }
}

const handleUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  if (!uploadForm.value.title) {
    ElMessage.warning('请输入文献标题')
    return
  }
  uploading.value = true
  try {
    await documentApi.uploadDocument(familyId, uploadFile.value, {
      title: uploadForm.value.title,
      description: uploadForm.value.description || undefined,
      author: uploadForm.value.author || undefined,
      document_date: uploadForm.value.document_date || undefined,
      tags: uploadForm.value.tags || undefined,
      category: uploadForm.value.category || 'other'
    })
    ElMessage.success('上传成功')
    uploadDialog.value = false
    uploadFile.value = null
    uploadForm.value = { title: '', description: '', author: '', document_date: '', tags: '', category: '' }
    fetchData()
  } catch (error) {
    console.error(error)
  } finally {
    uploading.value = false
  }
}

const openEdit = (doc: Document) => {
  editingDoc.value = doc
  editForm.value = {
    title: doc.title,
    description: doc.description || '',
    author: doc.author || '',
    document_date: doc.document_date || '',
    tags: doc.tags || '',
    category: doc.category || ''
  }
  editDialog.value = true
}

const handleEdit = async () => {
  if (!editingDoc.value) return
  try {
    await documentApi.updateDocument(editingDoc.value.id, editForm.value)
    ElMessage.success('更新成功')
    editDialog.value = false
    fetchDocuments()
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (doc: Document) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文献"${doc.title}"吗？`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await documentApi.deleteDocument(doc.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const openPreview = (doc: Document) => {
  previewDoc.value = doc
  previewDialog.value = true
}

const isImage = (doc: Document) => {
  return doc.file_type === 'image'
}

const formatFileSize = (bytes?: number) => {
  if (!bytes) return ''
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / (1024 * 1024)).toFixed(1) + 'MB'
}

onMounted(fetchData)
</script>

<template>
  <div class="document-page">
    <el-page-header @back="router.push(`/families/${familyId}`)">
      <template #content>
        <span class="page-title">文献库</span>
      </template>
    </el-page-header>

    <div v-if="family" class="family-info">
      <span class="family-name">{{ family.name }}</span>
      <el-tag v-if="family.surname" size="small">{{ family.surname }}氏</el-tag>
    </div>

    <!-- 概览统计 -->
    <el-row v-if="overview" :gutter="20" style="margin-top: 20px">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value">{{ overview.total }}</div>
            <div class="stat-label">文献总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value">{{ overview.pdf_count }}</div>
            <div class="stat-label">PDF文档</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value">{{ overview.image_count }}</div>
            <div class="stat-label">图片文献</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-item">
            <div class="stat-value">{{ overview.categories.length }}</div>
            <div class="stat-label">分类数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分类统计 -->
    <el-card v-if="overview && overview.categories.length > 0" style="margin-top: 16px">
      <template #header>文献分类</template>
      <el-row :gutter="12">
        <el-col v-for="cat in overview.categories" :key="cat.category" :span="6">
          <el-tag
            :type="currentCategory === cat.category ? 'primary' : 'info'"
            style="cursor: pointer; margin: 4px"
            @click="currentCategory = currentCategory === cat.category ? '' : cat.category; onCategoryChange()"
          >
            {{ categoryMap[cat.category] || cat.category }} ({{ cat.count }})
          </el-tag>
        </el-col>
        <el-col v-if="currentCategory">
          <el-button size="small" link @click="currentCategory = ''; onCategoryChange()">清除筛选</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 文献列表 -->
    <el-card style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span>文献列表（{{ total }}）</span>
            <el-input
              v-model="searchQuery"
              placeholder="搜索文献标题..."
              clearable
              style="width: 250px; margin-left: 16px"
              @keyup.enter="onSearch"
              @clear="onSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <el-button type="primary" @click="uploadDialog = true">
            <el-icon><Upload /></el-icon> 上传文献
          </el-button>
        </div>
      </template>

      <el-empty v-if="documents.length === 0" :description="currentCategory ? '该分类暂无文献' : '暂无文献，点击上传添加'" />

      <el-table v-else :data="filteredDocs" v-loading="loading">
        <el-table-column label="预览" width="80">
          <template #default="{ row }">
            <el-image
              v-if="isImage(row)"
              :src="row.file_url"
              fit="cover"
              style="width: 50px; height: 50px; border-radius: 4px; cursor: pointer"
              @click="openPreview(row)"
            />
            <el-icon v-else :size="32" style="color: #e6a23c; cursor: pointer" @click="openPreview(row)">
              <Document />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ categoryMap[row.category] || row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="author" label="作者" width="120">
          <template #default="{ row }">{{ row.author || '-' }}</template>
        </el-table-column>
        <el-table-column prop="document_date" label="文献日期" width="120">
          <template #default="{ row }">{{ row.document_date || '-' }}</template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.file_type === 'pdf'" type="warning" size="small">PDF</el-tag>
            <el-tag v-else-if="row.file_type === 'image'" type="success" size="small">图片</el-tag>
            <el-tag v-else size="small">{{ row.file_ext }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openPreview(row)">预览</el-button>
            <el-button type="primary" link size="small" @click="openEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传文献对话框 -->
    <el-dialog v-model="uploadDialog" title="上传文献" width="600px">
      <el-form label-position="top">
        <el-form-item label="选择文件" required>
          <el-upload
            drag
            accept=".pdf,.jpg,.jpeg,.png,.gif,.doc,.docx,.txt"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file) => onFileSelect(file.raw!)"
          >
            <el-icon :size="40"><Upload /></el-icon>
            <div v-if="!uploadFile">点击或拖拽文件到此区域上传<br/>支持PDF、图片、Word文档</div>
            <div v-else>已选择: {{ uploadFile.name }}</div>
          </el-upload>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="uploadForm.title" placeholder="文献标题" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="uploadForm.category" placeholder="选择分类" style="width: 100%">
                <el-option v-for="opt in categoryOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者">
              <el-input v-model="uploadForm.author" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文献日期">
          <el-input v-model="uploadForm.document_date" placeholder="如：光绪十五年（1889年）" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="uploadForm.tags" placeholder="用逗号分隔，如：族谱,光绪,张氏" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- 编辑文献对话框 -->
    <el-dialog v-model="editDialog" title="编辑文献" width="500px">
      <el-form label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="editForm.category" style="width: 100%">
                <el-option v-for="opt in categoryOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作者">
              <el-input v-model="editForm.author" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="文献日期">
          <el-input v-model="editForm.document_date" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="editForm.tags" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewDialog" :title="previewDoc?.title" fullscreen v-if="previewDoc">
      <div v-if="isImage(previewDoc)" class="preview-image-wrapper">
        <el-image
          :src="previewDoc.file_url"
          fit="contain"
          style="width: 100%; height: 80vh"
          :preview-src-list="[previewDoc.file_url]"
        />
      </div>
      <div v-else-if="previewDoc.file_type === 'pdf'" class="preview-pdf-wrapper">
        <iframe
          :src="previewDoc.file_url"
          style="width: 100%; height: 80vh; border: none"
        />
      </div>
      <div v-else class="preview-unsupported">
        <el-result icon="warning" title="无法预览" :subTitle="`此文件类型暂不支持在线预览，请下载后查看`">
          <template #extra>
            <el-button type="primary" @click="window.open(previewDoc.file_url, '_blank')">
              下载查看
            </el-button>
          </template>
        </el-result>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.document-page {
  padding: 20px 0;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.family-info {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.family-name {
  font-size: 16px;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.stat-item {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.preview-image-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f5f7fa;
  border-radius: 4px;
}

.preview-pdf-wrapper {
  background: #f5f7fa;
  border-radius: 4px;
}

.preview-unsupported {
  padding: 60px 0;
}
</style>
