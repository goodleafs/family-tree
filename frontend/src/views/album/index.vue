<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { albumApi } from '@/api/album'
import { familyApi } from '@/api/family'
import type { Album, AlbumTimeline, TimelineGroup, Photo } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const familyId = parseInt(route.params.id as string)

const family = ref<any>(null)
const albums = ref<Album[]>([])
const timeline = ref<AlbumTimeline | null>(null)
const loading = ref(false)
const activeTab = ref('albums')

const createDialog = ref(false)
const newAlbum = ref({ name: '', description: '' })
const creating = ref(false)

const uploadDialog = ref(false)
const uploadAlbumId = ref<number | null>(null)
const uploadFile = ref<File | null>(null)
const uploadTitle = ref('')
const uploadDate = ref('')
const uploading = ref(false)

const selectedYear = ref<number | null>(null)

const filteredTimeline = computed(() => {
  if (!timeline.value) return []
  if (selectedYear.value) {
    return timeline.value.timeline.filter(g => g.year === selectedYear.value)
  }
  return timeline.value.timeline
})

const fetchData = async () => {
  loading.value = true
  try {
    family.value = await familyApi.getFamily(familyId)
    albums.value = (await albumApi.getAlbums(familyId)).items
    timeline.value = await albumApi.getTimeline(familyId)
  } catch (error) {
    console.error(error)
    ElMessage.error('加载相册数据失败')
  } finally {
    loading.value = false
  }
}

const handleCreateAlbum = async () => {
  if (!newAlbum.value.name) {
    ElMessage.warning('请输入相册名称')
    return
  }
  creating.value = true
  try {
    await albumApi.createAlbum({
      family_id: familyId,
      name: newAlbum.value.name,
      description: newAlbum.value.description
    })
    ElMessage.success('创建相册成功')
    createDialog.value = false
    newAlbum.value = { name: '', description: '' }
    fetchData()
  } catch (error) {
    console.error(error)
  } finally {
    creating.value = false
  }
}

const handleDeleteAlbum = async (album: Album) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除相册"${album.name}"吗？相册中的照片也会被删除。`,
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await albumApi.deleteAlbum(album.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const openUploadDialog = (albumId: number) => {
  uploadAlbumId.value = albumId
  uploadFile.value = null
  uploadTitle.value = ''
  uploadDate.value = ''
  uploadDialog.value = true
}

const onFileSelect = (file: File) => {
  uploadFile.value = file
}

const handleUploadPhoto = async () => {
  if (!uploadFile.value || !uploadAlbumId.value) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    await albumApi.uploadPhoto(uploadAlbumId.value, uploadFile.value, {
      title: uploadTitle.value || undefined,
      taken_date: uploadDate.value || undefined
    })
    ElMessage.success('上传成功')
    uploadDialog.value = false
    fetchData()
  } catch (error) {
    console.error(error)
  } finally {
    uploading.value = false
  }
}

const viewAlbum = (albumId: number) => {
  router.push(`/families/${familyId}/albums/${albumId}`)
}

const formatDate = (d?: string) => {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

const getCoverUrl = (album: Album) => {
  return album.cover_url || ''
}

onMounted(fetchData)
</script>

<template>
  <div class="album-page">
    <el-page-header @back="router.push(`/families/${familyId}`)">
      <template #content>
        <span class="page-title">家族相册</span>
      </template>
    </el-page-header>

    <div v-if="family" class="family-info">
      <span class="family-name">{{ family.name }}</span>
      <el-tag v-if="family.surname" size="small">{{ family.surname }}氏</el-tag>
    </div>

    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <!-- 相册列表 -->
      <el-tab-pane label="相册集" name="albums">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>相册集（{{ albums.length }}）</span>
              <el-button type="primary" @click="createDialog = true">
                <el-icon><Plus /></el-icon> 创建相册
              </el-button>
            </div>
          </template>

          <el-empty v-if="albums.length === 0" description="暂无相册，创建一个吧" />

          <el-row v-else :gutter="20">
            <el-col v-for="album in albums" :key="album.id" :xs="24" :sm="12" :md="8" :lg="6" style="margin-bottom: 20px">
              <el-card :body-style="{ padding: '0px' }" shadow="hover" class="album-card" @click="viewAlbum(album.id)">
                <div class="album-cover">
                  <el-image
                    v-if="getCoverUrl(album)"
                    :src="getCoverUrl(album)"
                    fit="cover"
                    style="width: 100%; height: 180px"
                  />
                  <div v-else class="album-placeholder">
                    <el-icon :size="48"><Picture /></el-icon>
                    <p>暂无照片</p>
                  </div>
                  <div class="photo-count">
                    <el-icon><Picture /></el-icon> {{ album.photo_count || 0 }}
                  </div>
                </div>
                <div class="album-info" style="padding: 14px">
                  <h4>{{ album.name }}</h4>
                  <p v-if="album.description" class="album-desc">{{ album.description }}</p>
                  <div class="album-meta">
                    <span class="album-date">{{ formatDate(album.created_at) }}</span>
                    <el-button
                      type="danger"
                      size="small"
                      link
                      @click.stop="handleDeleteAlbum(album)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>

      <!-- 时间轴 -->
      <el-tab-pane label="时间轴" name="timeline">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>照片时间轴</span>
              <el-select
                v-model="selectedYear"
                placeholder="筛选年份"
                clearable
                style="width: 150px"
              >
                <el-option
                  v-for="year in timeline?.years || []"
                  :key="year"
                  :label="`${year}年`"
                  :value="year"
                />
              </el-select>
            </div>
          </template>

          <el-empty v-if="!timeline || timeline.total === 0" description="暂无带日期的照片" />

          <div v-else class="timeline-container">
            <div v-for="group in filteredTimeline" :key="group.year" class="timeline-year">
              <div class="year-header">
                <el-tag size="large" type="primary">{{ group.year }}年</el-tag>
                <span class="year-count">{{ group.photos.length }} 张照片</span>
              </div>
              <el-row :gutter="12">
                <el-col
                  v-for="photo in group.photos"
                  :key="photo.id"
                  :xs="12"
                  :sm="8"
                  :md="6"
                  :lg="4"
                  style="margin-bottom: 12px"
                >
                  <el-image
                    :src="photo.thumbnail_url || photo.url"
                    :preview-src-list="[photo.url]"
                    fit="cover"
                    style="width: 100%; height: 150px; border-radius: 4px; cursor: pointer"
                  >
                    <template #error>
                      <div class="image-error">
                        <el-icon><Picture /></el-icon>
                      </div>
                    </template>
                  </el-image>
                  <p v-if="photo.title" class="photo-title">{{ photo.title }}</p>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建相册对话框 -->
    <el-dialog v-model="createDialog" title="创建相册" width="500px">
      <el-form label-position="top">
        <el-form-item label="相册名称" required>
          <el-input v-model="newAlbum.name" placeholder="请输入相册名称" />
        </el-form-item>
        <el-form-item label="相册描述">
          <el-input v-model="newAlbum.description" type="textarea" :rows="3" placeholder="可选描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateAlbum">创建</el-button>
      </template>
    </el-dialog>

    <!-- 上传照片对话框 -->
    <el-dialog v-model="uploadDialog" title="上传照片" width="500px">
      <el-form label-position="top">
        <el-form-item label="选择照片" required>
          <el-upload
            drag
            accept="image/*"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file) => onFileSelect(file.raw!)"
          >
            <el-icon :size="40"><Plus /></el-icon>
            <div v-if="!uploadFile">点击或拖拽照片到此区域上传</div>
            <div v-else>已选择: {{ uploadFile.name }}</div>
          </el-upload>
        </el-form-item>
        <el-form-item label="照片标题">
          <el-input v-model="uploadTitle" placeholder="可选标题" />
        </el-form-item>
        <el-form-item label="拍摄日期">
          <el-date-picker
            v-model="uploadDate"
            type="date"
            placeholder="可选拍摄日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUploadPhoto">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.album-page {
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

.album-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.album-card:hover {
  transform: translateY(-2px);
}

.album-cover {
  position: relative;
  overflow: hidden;
}

.album-placeholder {
  height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}

.album-placeholder p {
  margin-top: 8px;
  font-size: 12px;
}

.photo-count {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.album-info h4 {
  margin: 0 0 6px;
  font-size: 15px;
}

.album-desc {
  font-size: 12px;
  color: #909399;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.album-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #c0c4cc;
}

.timeline-container {
  min-height: 300px;
}

.timeline-year {
  margin-bottom: 30px;
}

.year-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e4e7ed;
}

.year-count {
  color: #909399;
  font-size: 14px;
}

.photo-title {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-error {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}
</style>
