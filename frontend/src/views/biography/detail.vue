<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { biographyApi } from '@/api/biography'
import { personApi } from '@/api/person'
import type { Biography } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const biographyId = parseInt(route.params.bioId as string)
const familyId = parseInt(route.params.id as string)

const biography = ref<Biography | null>(null)
const loading = ref(true)

const editMode = ref(false)
const editForm = ref({
  title: '',
  subtitle: '',
  summary: '',
  content: '',
  achievements: '',
  is_published: true
})

const fetchBiography = async () => {
  loading.value = true
  try {
    biography.value = await biographyApi.getBiography(biographyId)
    if (biography.value) {
      editForm.value = {
        title: biography.value.title || '',
        subtitle: biography.value.subtitle || '',
        summary: biography.value.summary || '',
        content: biography.value.content,
        achievements: biography.value.achievements || '',
        is_published: biography.value.is_published
      }
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('加载传记失败')
    router.push(`/families/${familyId}/biographies`)
  } finally {
    loading.value = false
  }
}

const startEdit = () => {
  editMode.value = true
}

const cancelEdit = () => {
  editMode.value = false
  if (biography.value) {
    editForm.value = {
      title: biography.value.title || '',
      subtitle: biography.value.subtitle || '',
      summary: biography.value.summary || '',
      content: biography.value.content,
      achievements: biography.value.achievements || '',
      is_published: biography.value.is_published
    }
  }
}

const saveEdit = async () => {
  try {
    const updated = await biographyApi.updateBiography(biographyId, editForm.value)
    biography.value = updated
    editMode.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败')
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此传记吗？此操作不可撤销。',
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await biographyApi.deleteBiography(biographyId)
    ElMessage.success('删除成功')
    router.push(`/families/${familyId}/biographies`)
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const viewPersonDetail = () => {
  if (biography.value) {
    router.push(`/persons/${biography.value.person.id}`)
  }
}

const formatDate = (d?: string) => {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

onMounted(fetchBiography)
</script>

<template>
  <div class="bio-detail-page">
    <el-page-header @back="router.push(`/families/${familyId}/biographies`)">
      <template #content>
        <span class="page-title">{{ biography?.title || '人物传记' }}</span>
      </template>
      <template #extra>
        <el-button-group v-if="biography">
          <el-button v-if="!editMode" @click="startEdit">编辑</el-button>
          <el-button v-if="editMode" type="success" @click="saveEdit">保存</el-button>
          <el-button v-if="editMode" @click="cancelEdit">取消</el-button>
          <el-button type="danger" @click="handleDelete">删除</el-button>
        </el-button-group>
      </template>
    </el-page-header>

    <el-skeleton :rows="10" animated v-if="loading" style="margin-top: 20px" />

    <div v-else-if="biography" class="bio-content">
      <!-- 人物信息卡片 -->
      <el-card class="person-card" shadow="hover">
        <div class="person-brief">
          <el-avatar
            :size="80"
            :src="biography.portrait_url || biography.person.photo_url || ''"
            shape="square"
          >
            {{ biography.person.name.charAt(0) }}
          </el-avatar>
          <div class="person-detail">
            <h2>{{ biography.title || biography.person.name + '传' }}</h2>
            <p v-if="biography.subtitle" class="subtitle">{{ biography.subtitle }}</p>
            <div class="person-meta">
              <span class="person-name" @click="viewPersonDetail" style="cursor: pointer; color: #409eff;">
                {{ biography.person.name }}
              </span>
              <el-tag v-if="biography.person.generation_number" size="small">
                第{{ biography.person.generation_number }}代
              </el-tag>
              <el-tag v-if="biography.person.branch_name" size="small" type="info">
                {{ biography.person.branch_name }}
              </el-tag>
              <span v-if="biography.person.birth_date || biography.person.death_date" class="life-period">
                {{ biography.person.birth_date || '?' }} ~ {{ biography.person.death_date || '?' }}
              </span>
            </div>
          </div>
          <div class="views-badge">
            <el-tag type="info">
              <el-icon><View /></el-icon> {{ biography.views_count }} 次浏览
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 编辑模式 / 展示模式 -->
      <div v-if="editMode" style="margin-top: 20px">
        <el-form label-position="top">
          <el-form-item label="传记标题">
            <el-input v-model="editForm.title" />
          </el-form-item>
          <el-form-item label="副标题">
            <el-input v-model="editForm.subtitle" />
          </el-form-item>
          <el-form-item label="摘要">
            <el-input v-model="editForm.summary" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="传记正文" required>
            <el-input v-model="editForm.content" type="textarea" :rows="15" />
            <div class="form-tip">支持HTML格式</div>
          </el-form-item>
          <el-form-item label="主要成就">
            <el-input v-model="editForm.achievements" type="textarea" :rows="5" />
          </el-form-item>
          <el-form-item label="发布状态">
            <el-switch v-model="editForm.is_published" active-text="已发布" inactive-text="草稿" />
          </el-form-item>
        </el-form>
      </div>

      <div v-else class="bio-body">
        <!-- 摘要 -->
        <el-card v-if="biography.summary" class="bio-section">
          <template #header>导语</template>
          <p class="summary-text">{{ biography.summary }}</p>
        </el-card>

        <!-- 传记正文 -->
        <el-card class="bio-section">
          <template #header>传记正文</template>
          <div class="content-text" v-html="biography.content"></div>
        </el-card>

        <!-- 主要成就 -->
        <el-card v-if="biography.achievements" class="bio-section">
          <template #header>主要成就</template>
          <div class="content-text" v-html="biography.achievements"></div>
        </el-card>
      </div>
    </div>

    <el-empty v-else description="传记不存在" />
  </div>
</template>

<style scoped>
.bio-detail-page {
  padding: 20px 0;
  max-width: 900px;
  margin: 0 auto;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.person-card {
  margin-bottom: 20px;
}

.person-brief {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  position: relative;
}

.person-detail {
  flex: 1;
}

.person-detail h2 {
  margin: 0 0 6px;
  font-size: 24px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
  margin: 0 0 8px;
}

.person-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 14px;
}

.person-name {
  font-weight: 500;
}

.life-period {
  color: #909399;
  font-size: 13px;
}

.views-badge {
  position: absolute;
  top: 0;
  right: 0;
}

.bio-section {
  margin-bottom: 20px;
}

.summary-text {
  line-height: 1.8;
  color: #606266;
  font-size: 15px;
}

.content-text {
  line-height: 1.8;
  color: #303133;
  font-size: 15px;
  white-space: pre-wrap;
}

.content-text :deep(p) {
  margin-bottom: 12px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
