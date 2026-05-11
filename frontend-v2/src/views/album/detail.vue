<template>
  <div class="album-detail-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push(`/families/${familyId}/albums`)">
        <svg viewBox="0 0 16 16" fill="none"><path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/></svg>
        返回
      </button>
      <h1 class="page-title">{{ album?.name || '相册详情' }}</h1>
      <button class="upload-btn" @click="showUploadDialog = true">
        <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
        上传照片
      </button>
    </div>

    <div v-if="album" class="album-info-bar">
      <p v-if="album.description" class="album-desc">{{ album.description }}</p>
      <span class="photo-count">共 {{ album.photos.length }} 张照片</span>
    </div>

    <div v-if="album && album.photos.length === 0" class="empty-hint">
      <div class="empty-icon">📷</div>
      <p>暂无照片，点击上传</p>
    </div>

    <div v-if="album && album.photos.length > 0" class="photos-grid">
      <div v-for="photo in album.photos" :key="photo.id" class="photo-card">
        <div class="photo-wrapper">
          <img
            :src="photo.thumbnail_url || photo.url"
            class="photo-img"
            @click="previewUrl = photo.url; showPreview = true"
            alt=""
          />
          <button class="remove-btn" @click="handleDeletePhoto(photo)">×</button>
        </div>
        <div class="photo-info">
          <p v-if="photo.title" class="photo-title">{{ photo.title }}</p>
          <p v-if="photo.taken_date" class="photo-date">{{ photo.taken_date }}</p>
        </div>
      </div>
    </div>

    <!-- 图片预览 -->
    <div class="dialog-overlay preview-overlay" v-if="showPreview" @click="showPreview = false">
      <div class="preview-container" @click.stop>
        <button class="preview-close" @click="showPreview = false">×</button>
        <img :src="previewUrl" class="preview-image" alt="" />
      </div>
    </div>

    <!-- 上传对话框 -->
    <div class="dialog-overlay" v-if="showUploadDialog" @click="showUploadDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>上传照片</h2>
          <button class="close-btn" @click="showUploadDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="upload-zone" @click="triggerFileInput()">
            <input id="album-file-input" type="file" accept="image/*" style="display:none" @change="onFileChange" />
            <svg viewBox="0 0 24 24" fill="none"><path d="M12 4v16M4 12h16" stroke="currentColor" stroke-width="2"/></svg>
            <p v-if="!selectedFile">点击选择照片</p>
            <p v-else>{{ selectedFile.name }}</p>
          </div>
          <div class="form-group">
            <label>标题</label>
            <input v-model="uploadTitle" placeholder="可选" />
          </div>
          <div class="form-group">
            <label>拍摄日期</label>
            <input type="date" v-model="uploadDate" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showUploadDialog = false">取消</button>
          <button class="btn-submit" @click="handleUpload" :disabled="uploading">{{ uploading ? '上传中...' : '上传' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { albumApi } from '@/api/album'
import type { AlbumDetail, Photo } from '@/types'

const route = useRoute()
const router = useRouter()
const albumId = parseInt(route.params.albumId as string)
const familyId = parseInt(route.params.id as string)

const album = ref<AlbumDetail | null>(null)

const showUploadDialog = ref(false)
const selectedFile = ref<File | null>(null)
const uploadTitle = ref('')
const uploadDate = ref('')
const uploading = ref(false)

const showPreview = ref(false)
const previewUrl = ref('')

const fetchAlbum = async () => {
  try {
    album.value = await albumApi.getAlbum(albumId)
  } catch (e) {
    router.push(`/families/${familyId}/albums`)
  }
}

const triggerFileInput = () => {
  (document.getElementById('album-file-input') as HTMLInputElement)?.click()
}
const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input?.files?.length) selectedFile.value = input.files[0]
}

const handleUpload = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    await albumApi.uploadPhoto(albumId, selectedFile.value, {
      title: uploadTitle.value || undefined,
      taken_date: uploadDate.value || undefined
    })
    showUploadDialog.value = false
    selectedFile.value = null
    uploadTitle.value = ''
    uploadDate.value = ''
    fetchAlbum()
  } finally {
    uploading.value = false
  }
}

const handleDeletePhoto = async (photo: Photo) => {
  if (!confirm('确定删除此照片吗？')) return
  await albumApi.deletePhoto(photo.id)
  fetchAlbum()
}

onMounted(fetchAlbum)
</script>

<style scoped>
.album-detail-page { max-width: 960px; }
.page-header { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-6); }
.back-btn { display: flex; align-items: center; gap: var(--space-1); padding: var(--space-2) var(--space-3); background: none; border: 1px solid var(--border-primary); border-radius: var(--radius-md); color: var(--text-secondary); font-size: var(--text-sm); cursor: pointer; }
.back-btn svg { width: 14px; height: 14px; }
.page-title { flex: 1; font-family: var(--font-title); margin: 0; }
.upload-btn { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); font-size: var(--text-sm); cursor: pointer; }
.upload-btn svg { width: 14px; height: 14px; }
.album-info-bar { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-5); }
.album-desc { color: var(--text-tertiary); margin: 0; }
.photo-count { font-size: var(--text-sm); color: var(--text-secondary); }

.photos-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--space-4); }
.photo-card { background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); overflow: hidden; }
.photo-wrapper { position: relative; height: 180px; }
.photo-img { width: 100%; height: 100%; object-fit: cover; cursor: pointer; display: block; }
.remove-btn { position: absolute; top: 4px; right: 4px; width: 24px; height: 24px; border-radius: 50%; background: rgba(0,0,0,0.5); color: white; border: none; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity var(--transition-fast); }
.photo-card:hover .remove-btn { opacity: 1; }
.photo-info { padding: var(--space-3); }
.photo-title { margin: 0; font-size: var(--text-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photo-date { margin: var(--space-1) 0 0; font-size: var(--text-xs); color: var(--text-tertiary); }

.empty-hint { text-align: center; padding: var(--space-10); color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: var(--space-4); }

/* 图片预览 */
.preview-overlay { background: rgba(0,0,0,0.85); }
.preview-container { position: relative; max-width: 90vw; max-height: 90vh; display: flex; align-items: center; justify-content: center; }
.preview-image { max-width: 100%; max-height: 90vh; object-fit: contain; border-radius: var(--radius-md); }
.preview-close { position: fixed; top: 20px; right: 20px; width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.2); color: white; border: none; font-size: 28px; cursor: pointer; display: flex; align-items: center; justify-content: center; line-height: 1; }

/* Upload zone */
.upload-zone { border: 2px dashed var(--border-primary); border-radius: var(--radius-md); padding: var(--space-8); text-align: center; cursor: pointer; color: var(--text-tertiary); margin-bottom: var(--space-4); }
.upload-zone svg { width: 32px; height: 32px; margin-bottom: var(--space-2); }
.upload-zone:hover { border-color: var(--cinnabar); color: var(--cinnabar); }

.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; font-size: var(--text-sm); color: var(--text-primary); margin-bottom: var(--space-2); }
.form-group input { width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-base); }
.form-group input:focus { outline: none; border-color: var(--cinnabar); }

.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 480px; max-width: 90vw; box-shadow: var(--shadow-lg); }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-5); border-bottom: 1px solid var(--border-primary); }
.dialog-header h2 { margin: 0; }
.close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
.dialog-body { padding: var(--space-5); }
.dialog-footer { display: flex; justify-content: flex-end; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border-primary); }
.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; }
.btn-submit:disabled { opacity: 0.6; }
</style>
