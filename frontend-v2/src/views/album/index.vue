<template>
  <div class="album-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push(`/families/${familyId}`)">
        <svg viewBox="0 0 16 16" fill="none"><path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/></svg>
        返回
      </button>
      <h1 class="page-title">家族相册</h1>
      <button class="create-btn" @click="showCreateDialog = true">
        <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
        创建相册
      </button>
    </div>

    <!-- 选项卡 -->
    <div class="tabs">
      <button v-for="tab in tabs" :key="tab.key" class="tab-item" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        {{ tab.label }}
      </button>
    </div>

    <!-- 相册集 -->
    <div v-if="activeTab === 'albums'" class="albums-panel">
      <div v-if="albums.length === 0" class="empty-hint">
        <div class="empty-icon">📸</div>
        <p>暂无相册，点击上方按钮创建</p>
      </div>
      <div v-else class="albums-grid">
        <div v-for="album in albums" :key="album.id" class="album-card" @click="$router.push(`/families/${familyId}/albums/${album.id}`)">
          <div class="album-cover">
            <img v-if="album.cover_url" :src="album.cover_url" alt="" />
            <div v-else class="cover-placeholder">
              <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/><circle cx="8.5" cy="10.5" r="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M21 15l-5-5-5 5" stroke="currentColor" stroke-width="1.5"/></svg>
              <span>暂无照片</span>
            </div>
            <div class="photo-badge">{{ album.photo_count || 0 }} 张</div>
          </div>
          <div class="album-info">
            <h4>{{ album.name }}</h4>
            <p v-if="album.description" class="album-desc">{{ album.description }}</p>
            <div class="album-meta">
              <span>{{ formatDate(album.created_at) }}</span>
              <button class="delete-btn" @click.stop="handleDeleteAlbum(album)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 时间轴 -->
    <div v-if="activeTab === 'timeline'" class="timeline-panel">
      <div class="panel-header">
        <select v-model="selectedYear" class="filter-select" @change="filterTimeline">
          <option :value="0">全部年份</option>
          <option v-for="y in timelineYears" :key="y" :value="y">{{ y }}年</option>
        </select>
      </div>
      <div v-if="!timeline || timeline.total === 0" class="empty-hint">
        <div class="empty-icon">📅</div>
        <p>暂无带日期的照片</p>
      </div>
      <div v-else class="timeline-list">
        <div v-for="group in filteredTimeline" :key="group.year" class="timeline-group">
          <div class="year-label">{{ group.year }}年</div>
          <div class="photos-row">
            <div v-for="photo in group.photos" :key="photo.id" class="timeline-photo">
              <img
                :src="photo.thumbnail_url || photo.url"
                class="photo-img"
                @click="openPhoto(photo.url)"
                alt=""
              />
              <p v-if="photo.title" class="photo-title">{{ photo.title }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建相册对话框 -->
    <div class="dialog-overlay" v-if="showCreateDialog" @click="showCreateDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>创建相册</h2>
          <button class="close-btn" @click="showCreateDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>相册名称 <span class="required">*</span></label>
            <input v-model="newAlbumName" placeholder="请输入相册名称" />
          </div>
          <div class="form-group">
            <label>相册描述</label>
            <textarea v-model="newAlbumDesc" rows="3" placeholder="可选"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showCreateDialog = false">取消</button>
          <button class="btn-submit" @click="handleCreateAlbum" :disabled="creating">{{ creating ? '创建中...' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { albumApi } from '@/api/album'
import type { Album, AlbumTimeline } from '@/types'

const route = useRoute()
const familyId = parseInt(route.params.id as string)

const albums = ref<Album[]>([])
const timeline = ref<AlbumTimeline | null>(null)
const activeTab = ref('albums')
const selectedYear = ref(0)

const showCreateDialog = ref(false)
const newAlbumName = ref('')
const newAlbumDesc = ref('')
const creating = ref(false)

const tabs = [
  { key: 'albums', label: '相册集' },
  { key: 'timeline', label: '时间轴' }
]

const timelineYears = computed(() => timeline.value?.years || [])
const filteredTimeline = computed(() => {
  if (!timeline.value) return []
  if (selectedYear.value) return timeline.value.timeline.filter(g => g.year === selectedYear.value)
  return timeline.value.timeline
})

const fetchData = async () => {
  try {
    albums.value = (await albumApi.getAlbums(familyId)).items
    timeline.value = await albumApi.getTimeline(familyId)
  } catch (e) {
    console.error(e)
  }
}

const handleCreateAlbum = async () => {
  if (!newAlbumName.value) return
  creating.value = true
  try {
    await albumApi.createAlbum({ family_id: familyId, name: newAlbumName.value, description: newAlbumDesc.value || undefined })
    showCreateDialog.value = false
    newAlbumName.value = ''
    newAlbumDesc.value = ''
    fetchData()
  } finally {
    creating.value = false
  }
}

const handleDeleteAlbum = async (album: Album) => {
  if (!confirm(`确定删除相册"${album.name}"吗？`)) return
  await albumApi.deleteAlbum(album.id)
  fetchData()
}

const filterTimeline = () => {}
const openPhoto = (url: string) => window.open(url, '_blank')
const formatDate = (d: string) => new Date(d).toLocaleDateString('zh-CN')

onMounted(fetchData)
</script>

<style scoped>
.album-page {
  max-width: 960px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  background: none;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
}
.back-btn svg { width: 14px; height: 14px; }

.page-title { flex: 1; font-family: var(--font-title); font-size: var(--text-2xl); color: var(--text-primary); margin: 0; }

.create-btn {
  display: flex; align-items: center; gap: var(--space-2);
  padding: var(--space-2) var(--space-5);
  background: var(--cinnabar); color: white;
  border: none; border-radius: var(--radius-md);
  font-size: var(--text-sm); cursor: pointer;
}
.create-btn svg { width: 14px; height: 14px; }

.tabs { display: flex; gap: var(--space-1); margin-bottom: var(--space-6); border-bottom: 1px solid var(--border-primary); }
.tab-item {
  padding: var(--space-3) var(--space-5);
  background: none; border: none; border-bottom: 2px solid transparent;
  color: var(--text-secondary); font-size: var(--text-sm); cursor: pointer;
  transition: all var(--transition-fast);
}
.tab-item.active { color: var(--cinnabar); border-bottom-color: var(--cinnabar); font-weight: var(--font-medium); }

.albums-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--space-5); }

.album-card {
  background: var(--bg-primary); border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg); overflow: hidden; cursor: pointer;
  transition: all var(--transition-fast);
}
.album-card:hover { border-color: var(--border-secondary); box-shadow: var(--shadow-md); transform: translateY(-2px); }

.album-cover { position: relative; height: 180px; overflow: hidden; }
.album-cover img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder {
  height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: var(--bg-secondary); color: var(--text-tertiary); gap: var(--space-2);
}
.cover-placeholder svg { width: 40px; height: 40px; }
.photo-badge {
  position: absolute; bottom: var(--space-2); right: var(--space-2);
  padding: 2px var(--space-3); background: rgba(0,0,0,0.6); color: white;
  border-radius: var(--radius-full); font-size: var(--text-xs);
}

.album-info { padding: var(--space-4); }
.album-info h4 { margin: 0 0 var(--space-1); font-size: var(--text-base); }
.album-desc { font-size: var(--text-sm); color: var(--text-tertiary); margin: 0 0 var(--space-2); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.album-meta { display: flex; justify-content: space-between; align-items: center; font-size: var(--text-xs); color: var(--text-tertiary); }
.delete-btn { background: none; border: none; color: var(--cinnabar); cursor: pointer; font-size: var(--text-xs); }

.timeline-list { display: flex; flex-direction: column; gap: var(--space-8); }
.timeline-group { }
.year-label {
  font-family: var(--font-title); font-size: var(--text-xl); color: var(--cinnabar);
  padding-bottom: var(--space-3); border-bottom: 2px solid var(--cinnabar-pale);
  margin-bottom: var(--space-4);
}
.photos-row { display: flex; flex-wrap: wrap; gap: var(--space-3); }
.timeline-photo { width: 160px; }
.photo-img { width: 160px; height: 120px; border-radius: var(--radius-md); object-fit: cover; cursor: pointer; }
.photo-title { font-size: var(--text-xs); color: var(--text-secondary); margin-top: var(--space-1); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.panel-header { margin-bottom: var(--space-4); }
.filter-select { padding: var(--space-2) var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-sm); background: var(--bg-primary); }

.empty-hint { text-align: center; padding: var(--space-10); color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: var(--space-4); }

/* Dialog */
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 480px; max-width: 90vw; box-shadow: var(--shadow-lg); }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-5); border-bottom: 1px solid var(--border-primary); }
.dialog-header h2 { margin: 0; font-size: var(--text-lg); }
.close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
.dialog-body { padding: var(--space-5); }
.dialog-footer { display: flex; justify-content: flex-end; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border-primary); }
.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; font-size: var(--text-sm); color: var(--text-primary); margin-bottom: var(--space-2); }
.form-group input, .form-group textarea, .form-group select {
  width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md);
  font-size: var(--text-base); font-family: var(--font-body); background: var(--bg-primary);
}
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--cinnabar); }
.required { color: var(--cinnabar); }
.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; }
.btn-submit:disabled { opacity: 0.6; }
</style>
