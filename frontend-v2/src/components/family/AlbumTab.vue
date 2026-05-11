<template>
  <div class="album-tab">
    <div class="panel-header">
      <h3>家族相册</h3>
      <div class="header-actions">
        <button class="add-btn" @click="showCreate = true">
          <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
          创建相册
        </button>
        <router-link :to="`/families/${familyId}/albums`" class="view-full-btn">查看全部</router-link>
      </div>
    </div>

    <div v-if="loading" class="loading-hint">加载中...</div>

    <div v-else-if="albums.length === 0" class="empty-hint">
      <div class="empty-icon">📸</div>
      <p>暂无相册，点击上方按钮创建</p>
    </div>

    <div v-else class="album-grid">
      <div v-for="album in albums" :key="album.id" class="album-card" @click="$router.push(`/families/${familyId}/albums/${album.id}`)">
        <div class="album-cover">
          <img v-if="album.cover_url" :src="album.cover_url" alt="" />
          <div v-else class="cover-placeholder">
            <svg viewBox="0 0 24 24" fill="none"><rect x="3" y="5" width="18" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/><circle cx="8.5" cy="10.5" r="1.5" stroke="currentColor" stroke-width="1.5"/><path d="M21 15l-5-5-5 5" stroke="currentColor" stroke-width="1.5"/></svg>
            <span>{{ album.photo_count || 0 }} 张</span>
          </div>
        </div>
        <div class="album-name">{{ album.name }}</div>
      </div>
    </div>

    <!-- 创建相册对话框 -->
    <div class="dialog-overlay" v-if="showCreate" @click="showCreate = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header"><h2>创建相册</h2><button class="close-btn" @click="showCreate = false">×</button></div>
        <div class="dialog-body">
          <div class="form-group"><label>相册名称 <span class="required">*</span></label><input v-model="newName" placeholder="请输入相册名称" /></div>
          <div class="form-group"><label>描述</label><textarea v-model="newDesc" rows="2" placeholder="可选"></textarea></div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showCreate = false">取消</button>
          <button class="btn-submit" :disabled="creating" @click="handleCreate">{{ creating ? '创建中...' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { albumApi } from '@/api/album'
import type { Album } from '@/types'

const props = defineProps<{ familyId: number }>()

const albums = ref<Album[]>([])
const loading = ref(true)
const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')
const creating = ref(false)

const fetchAlbums = async () => {
  try {
    albums.value = (await albumApi.getAlbums(props.familyId, { limit: 8 })).items
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleCreate = async () => {
  if (!newName.value) return
  creating.value = true
  try {
    await albumApi.createAlbum({ family_id: props.familyId, name: newName.value, description: newDesc.value || undefined })
    showCreate.value = false
    newName.value = ''
    newDesc.value = ''
    fetchAlbums()
  } finally { creating.value = false }
}

onMounted(fetchAlbums)
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
.album-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: var(--space-4); }
.album-card { border: 1px solid var(--border-primary); border-radius: var(--radius-md); overflow: hidden; cursor: pointer; transition: all var(--transition-fast); }
.album-card:hover { border-color: var(--border-secondary); box-shadow: var(--shadow-sm); transform: translateY(-1px); }
.album-cover { height: 110px; overflow: hidden; }
.album-cover img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--bg-secondary); color: var(--text-tertiary); font-size: var(--text-xs); gap: var(--space-1); }
.cover-placeholder svg { width: 28px; height: 28px; }
.album-name { padding: var(--space-2) var(--space-3); font-size: var(--text-sm); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 440px; max-width: 90vw; box-shadow: var(--shadow-lg); }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-4) var(--space-5); border-bottom: 1px solid var(--border-primary); }
.dialog-header h2 { margin: 0; font-size: var(--text-lg); }
.close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
.dialog-body { padding: var(--space-5); }
.dialog-footer { display: flex; justify-content: flex-end; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border-primary); }
.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; font-size: var(--text-sm); margin-bottom: var(--space-2); }
.form-group input, .form-group textarea { width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-base); font-family: var(--font-body); background: var(--bg-primary); box-sizing: border-box; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--cinnabar); }
.required { color: var(--cinnabar); }
.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--text-sm); }
.btn-submit:disabled { opacity: 0.6; }
</style>
