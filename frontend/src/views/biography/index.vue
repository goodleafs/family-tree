<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { biographyApi } from '@/api/biography'
import { familyApi } from '@/api/family'
import { personApi } from '@/api/person'
import type { BiographyListItem } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const familyId = parseInt(route.params.id as string)

const family = ref<any>(null)
const biographies = ref<BiographyListItem[]>([])
const loading = ref(false)
const searchQuery = ref('')

const createDialog = ref(false)
const eligiblePersons = ref<any[]>([])
const selectedPersonId = ref<number | null>(null)
const newBio = ref({
  title: '',
  subtitle: '',
  summary: '',
  content: '',
  achievements: '',
  is_published: true
})
const creating = ref(false)
const loadingPersonBio = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    family.value = await familyApi.getFamily(familyId)
    await fetchBiographies()
  } catch (error) {
    console.error(error)
    ElMessage.error('加载传记数据失败')
  } finally {
    loading.value = false
  }
}

const fetchBiographies = async () => {
  try {
    const res = await biographyApi.getBiographies(familyId, {
      search: searchQuery.value || undefined
    })
    biographies.value = res.items
  } catch (error) {
    console.error(error)
  }
}

const onSearch = () => {
  fetchBiographies()
}

const openCreate = async () => {
  createDialog.value = true
  try {
    eligiblePersons.value = await biographyApi.getEligiblePersons(familyId)
  } catch (error) {
    console.error(error)
  }
}

const onPersonSelect = async (personId: number) => {
  if (!personId) return
  loadingPersonBio.value = true
  try {
    const person = await personApi.getPerson(personId)
    newBio.value.title = `${person.name}传`
    newBio.value.summary = person.biography?.substring(0, 200) || ''
  } catch (error) {
    console.error(error)
  } finally {
    loadingPersonBio.value = false
  }
}

const handleCreate = async () => {
  if (!selectedPersonId.value) {
    ElMessage.warning('请选择人员')
    return
  }
  if (!newBio.value.content) {
    ElMessage.warning('请输入传记正文')
    return
  }
  creating.value = true
  try {
    await biographyApi.createBiography({
      person_id: selectedPersonId.value,
      family_id: familyId,
      title: newBio.value.title || undefined,
      subtitle: newBio.value.subtitle || undefined,
      summary: newBio.value.summary || undefined,
      content: newBio.value.content,
      achievements: newBio.value.achievements || undefined,
      is_published: newBio.value.is_published
    })
    ElMessage.success('创建传记成功')
    createDialog.value = false
    newBio.value = { title: '', subtitle: '', summary: '', content: '', achievements: '', is_published: true }
    selectedPersonId.value = null
    fetchBiographies()
  } catch (error) {
    console.error(error)
  } finally {
    creating.value = false
  }
}

const handleDelete = async (bio: BiographyListItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除"${bio.title || bio.person.name}"的传记吗？`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await biographyApi.deleteBiography(bio.id)
    ElMessage.success('删除成功')
    fetchBiographies()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const viewBiography = (id: number) => {
  router.push(`/families/${familyId}/biographies/${id}`)
}

onMounted(fetchData)
</script>

<template>
  <div class="biography-page">
    <el-page-header @back="router.push(`/families/${familyId}`)">
      <template #content>
        <span class="page-title">人物传记</span>
      </template>
    </el-page-header>

    <div v-if="family" class="family-info">
      <span class="family-name">{{ family.name }}</span>
      <el-tag v-if="family.surname" size="small">{{ family.surname }}氏</el-tag>
    </div>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span>传记列表（{{ biographies.length }}）</span>
            <el-input
              v-model="searchQuery"
              placeholder="搜索传记标题..."
              clearable
              style="width: 250px; margin-left: 16px"
              @keyup.enter="onSearch"
              @clear="onSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </div>
          <el-button type="primary" @click="openCreate">
            <el-icon><Plus /></el-icon> 创建传记
          </el-button>
        </div>
      </template>

      <el-empty v-if="biographies.length === 0" description="暂无人物传记" />

      <el-row v-else :gutter="20">
        <el-col
          v-for="bio in biographies"
          :key="bio.id"
          :xs="24"
          :sm="12"
          :md="8"
          style="margin-bottom: 20px"
        >
          <el-card shadow="hover" class="bio-card" @click="viewBiography(bio.id)">
            <div class="bio-header">
              <el-avatar :size="56" :src="bio.person.photo_url || ''" shape="square">
                {{ bio.person.name.charAt(0) }}
              </el-avatar>
              <div class="bio-person-info">
                <h4>{{ bio.title || bio.person.name + '传' }}</h4>
                <p class="bio-person-name">
                  {{ bio.person.name }}
                  <el-tag v-if="bio.person.generation_number" size="small">
                    第{{ bio.person.generation_number }}代
                  </el-tag>
                  <el-tag v-if="bio.person.branch_name" size="small" type="info">
                    {{ bio.person.branch_name }}
                  </el-tag>
                </p>
              </div>
            </div>
            <p v-if="bio.summary" class="bio-summary">{{ bio.summary }}</p>
            <div class="bio-footer">
              <span class="bio-views">
                <el-icon><View /></el-icon> {{ bio.views_count }} 次浏览
              </span>
              <span class="bio-date">{{ new Date(bio.created_at).toLocaleDateString('zh-CN') }}</span>
              <el-button type="danger" size="small" link @click.stop="handleDelete(bio)">
                删除
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 创建传记对话框 -->
    <el-dialog v-model="createDialog" title="创建人物传记" width="700px">
      <el-form label-position="top">
        <el-form-item label="选择人物" required>
          <el-select
            v-model="selectedPersonId"
            placeholder="选择要创建传记的家族成员"
            filterable
            style="width: 100%"
            @change="onPersonSelect"
          >
            <el-option
              v-for="p in eligiblePersons"
              :key="p.id"
              :label="`${p.name}${p.generation_number ? ' (第'+p.generation_number+'代)' : ''}${p.branch_name ? ' - '+p.branch_name : ''}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="传记标题">
          <el-input v-model="newBio.title" placeholder="如：先祖XX公传" />
        </el-form-item>

        <el-form-item label="副标题">
          <el-input v-model="newBio.subtitle" placeholder="可选" />
        </el-form-item>

        <el-form-item label="摘要/导语">
          <el-input
            v-model="newBio.summary"
            type="textarea"
            :rows="3"
            placeholder="传记摘要（显示在列表页）"
          />
        </el-form-item>

        <el-form-item label="传记正文" required>
          <el-input
            v-model="newBio.content"
            type="textarea"
            :rows="10"
            placeholder="请详细书写人物传记正文..."
          />
          <div class="form-tip">支持HTML格式，如段落、加粗、图片等</div>
        </el-form-item>

        <el-form-item label="主要成就">
          <el-input
            v-model="newBio.achievements"
            type="textarea"
            :rows="4"
            placeholder="人物的主要成就和贡献"
          />
        </el-form-item>

        <el-form-item label="发布状态">
          <el-switch v-model="newBio.is_published" active-text="发布" inactive-text="草稿" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.biography-page {
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

.bio-card {
  cursor: pointer;
  transition: transform 0.2s;
  height: 100%;
}

.bio-card:hover {
  transform: translateY(-2px);
}

.bio-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.bio-person-info h4 {
  margin: 0 0 4px;
  font-size: 16px;
}

.bio-person-name {
  font-size: 13px;
  color: #909399;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.bio-summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0 0 12px;
}

.bio-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #c0c4cc;
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
}

.bio-views {
  display: flex;
  align-items: center;
  gap: 4px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
