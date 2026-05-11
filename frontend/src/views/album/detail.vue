<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { albumApi } from '@/api/album'
import type { AlbumDetail, Photo } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const albumId = parseInt(route.params.albumId as string)
const familyId = parseInt(route.params.id as string)

const album = ref<AlbumDetail | null>(null)
const loading = ref(false)

const uploadDialog = ref(false)
const uploadFile = ref<File | null>(null)
const uploadTitle = ref('')
const uploadDate = ref('')
const uploading = ref(false)

const fetchAlbum = async () => {
  loading.value = true
  try {
    album.value = await albumApi.getAlbum(albumId)
  } catch (error) {
    console.error(error)
    ElMessage.error('加载相册失败')
    router.push(`/families/${familyId}/albums`)
  } finally {
    loading.value = false
  }
}

const onFileSelect = (file: File) => {
  uploadFile.value = file
}

const handleUpload = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    await albumApi.uploadPhoto(albumId, uploadFile.value, {
      title: uploadTitle.value || undefined,
      taken_date: uploadDate.value || undefined
    })
    ElMessage.success('上传成功')
    uploadDialog.value = false
    uploadFile.value = null
    uploadTitle.value = ''
    uploadDate.value = ''
    fetchAlbum()
  } catch (error) {
    console.error(error)
  } finally {
    uploading.value = false
  }
}

const handleDeletePhoto = async (photo: Photo) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此照片吗？',
      '确认删除',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await albumApi.deletePhoto(photo.id)
    ElMessage.success('删除成功')
    fetchAlbum()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const formatDate = (d?: string) => {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

onMounted(fetchAlbum)
</script>

<template>
  <div class="album-detail-page">
    <el-page-header @back="router.push(`/families/${familyId}/albums`)">
      <template #content>
        <span class="page-title">{{ album?.name || '相册详情' }}</span>
      </template>
      <template #extra>
        <el-button type="primary" @click="uploadDialog = true">
          <el-icon><Upload /></el-icon> 上传照片
        </el-button>
      </template>
    </el-page-header>

    <div v-if="album" class="album-info-bar">
      <p v-if="album.description" class="album-desc">{{ album.description }}</p>
      <span class="photo-total">共 {{ album.photos.length }} 张照片</span>
    </div>

    <div v-loading="loading" style="margin-top: 20px">
      <el-empty v-if="album && album.photos.length === 0" description="暂无照片" />

      <el-row v-if="album && album.photos.length > 0" :gutter="12">
        <el-col
          v-for="(photo, index) in album.photos"
          :key="photo.id"
          :xs="12"
          :sm="8"
          :md="6"
          :lg="4"
          style="margin-bottom: 12px"
        >
          <el-card :body-style="{ padding: '0px' }" shadow="hover" class="photo-card">
            <div class="photo-wrapper">
              <el-image
                :src="photo.thumbnail_url || photo.url"
                :preview-src-list="previewPhotos"
                :initial-index="index"
                fit="cover"
                style="width: 100%; height: 180px; cursor: pointer"
              >
                <template #error>
                  <div class="photo-error"><el-icon><Picture /></el-icon></div>
                </template>
              </el-image>
            </div>
            <div class="photo-info">
              <p v-if="photo.title" class="photo-title">{{ photo.title }}</p>
              <p v-if="photo.taken_date" class="photo-date">{{ photo.taken_date }}</p>
              <el-button type="danger" size="small" link @click="handleDeletePhoto(photo)">
                删除
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

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
        <el-form-item label="标题">
          <el-input v-model="uploadTitle" placeholder="可选" />
        </el-form-item>
        <el-form-item label="拍摄日期">
          <el-date-picker
            v-model="uploadDate"
            type="date"
            placeholder="可选"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>


  </div>
</template>

<style scoped>
.album-detail-page {
  padding: 20px 0;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.album-info-bar {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.album-desc {
  color: #909399;
  margin: 0;
}

.photo-total {
  font-size: 14px;
  color: #606266;
}

.photo-card {
  cursor: default;
}

.photo-wrapper {
  overflow: hidden;
}

.photo-info {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.photo-title {
  margin: 0;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.photo-date {
  margin: 0;
  font-size: 11px;
  color: #c0c4cc;
}

.photo-error {
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}
</style>
