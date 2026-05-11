<template>
  <div class="person-detail-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg viewBox="0 0 16 16" fill="none">
          <path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        返回
      </button>
      
      <div class="header-center" v-if="person">
        <div class="person-avatar" :class="person.gender">
          <img v-if="person.photo_url" :src="person.photo_url" alt="" />
          <span v-else>{{ person.name?.charAt(0) || '人' }}</span>
        </div>
        <div class="person-header-info">
          <h1 class="person-name">{{ person.name }}</h1>
          <span class="person-meta" v-if="family">{{ family.name }}</span>
        </div>
      </div>
      
      <div class="header-actions" v-if="person">
        <button v-if="!editMode" class="action-btn primary" @click="startEdit">
          <svg viewBox="0 0 16 16" fill="none">
            <path d="M2 11.5V14h2.5l7-7-2.5-2.5-7 7zM11.5 3.5l1 1-7 7-1-1 7-1z" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          编辑
        </button>
        <button v-if="editMode" class="action-btn success" @click="saveEdit">
          <svg viewBox="0 0 16 16" fill="none">
            <path d="M3 8l3 3 7-7" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          保存
        </button>
        <button v-if="editMode" class="action-btn" @click="cancelEdit">取消</button>
        <button class="action-btn danger" @click="deletePerson">
          <svg viewBox="0 0 16 16" fill="none">
            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          删除
        </button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 内容区域 -->
    <div class="detail-content" v-else-if="person">
      <!-- 选项卡 -->
      <div class="tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>
      
      <!-- 基本信息 -->
      <div class="tab-panel" v-show="activeTab === 'basic'">
        <div class="panel-grid">
          <!-- 左侧：基本信息 -->
          <div class="info-card">
            <h3 class="card-title">基本信息</h3>
            <div class="info-list">
              <div class="info-item">
                <span class="info-label">姓名</span>
                <input v-if="editMode" v-model="editingPerson.name" class="info-input" />
                <span v-else class="info-value">{{ person.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">性别</span>
                <select v-if="editMode" v-model="editingPerson.gender" class="info-select">
                  <option value="male">男性</option>
                  <option value="female">女性</option>
                </select>
                <span v-else class="info-value">{{ person.gender === 'male' ? '男性' : person.gender === 'female' ? '女性' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">出生日期</span>
                <input v-if="editMode" v-model="editingPerson.birth_date" type="date" class="info-input" />
                <div v-else class="info-value-group">
                  <span class="info-value">{{ formatDate(person.birth_date) }}</span>
                  <span class="info-lunar" v-if="person.birth_date">农历 {{ toLunarDate(person.birth_date) }}</span>
                </div>
              </div>
              <div class="info-item">
                <span class="info-label">逝世纪念</span>
                <input v-if="editMode" v-model="editingPerson.death_date" type="date" class="info-input" />
                <div v-else class="info-value-group">
                  <span class="info-value">{{ formatDate(person.death_date) }}</span>
                  <span class="info-lunar" v-if="person.death_date">农历 {{ toLunarDate(person.death_date) }}</span>
                </div>
              </div>
              <div class="info-item">
                <span class="info-label">字辈号</span>
                <input v-if="editMode" v-model.number="editingPerson.generation_number" type="number" class="info-input" />
                <span v-else class="info-value">{{ person.generation_number ? `第${person.generation_number}代` : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">分支名</span>
                <input v-if="editMode" v-model="editingPerson.branch_name" class="info-input" />
                <span v-else class="info-value">{{ person.branch_name || '-' }}</span>
              </div>
            </div>
          </div>
          
          <!-- 右侧：照片 -->
          <div class="info-card photo-card">
            <h3 class="card-title">头像照片</h3>
            <div class="photo-area">
              <div class="photo-preview" v-if="person.photo_url">
                <img :src="person.photo_url" alt="" />
              </div>
              <div class="photo-placeholder" v-else>
                <svg viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M4 20c0-4 3.5-7 8-7s8 3 8 7" stroke="currentColor" stroke-width="1.5"/>
                </svg>
                <span>暂无照片</span>
              </div>
              
              <div class="photo-upload" v-if="editMode">
                <input type="file" ref="fileInput" accept="image/*" @change="handleFileUpload" style="display: none" />
                <button class="upload-btn" @click="() => fileInput?.click()" :disabled="uploading">
                  {{ uploading ? '上传中...' : '更换照片' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 出身详情 -->
      <div class="tab-panel" v-show="activeTab === 'origin'">
        <div class="info-card">
          <h3 class="card-title">出身详情</h3>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">出生地</span>
              <input v-if="editMode" v-model="editingPerson.birthplace" class="info-input" placeholder="请输入出生地" />
              <span v-else class="info-value">{{ person.birthplace || '未填写' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">现居住地</span>
              <input v-if="editMode" v-model="editingPerson.residence" class="info-input" placeholder="请输入现居住地" />
              <span v-else class="info-value">{{ person.residence || '未填写' }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 教育职业 -->
      <div class="tab-panel" v-show="activeTab === 'career'">
        <div class="info-card">
          <h3 class="card-title">教育职业</h3>
          <div class="info-list vertical">
            <div class="info-item">
              <span class="info-label">教育背景</span>
              <textarea v-if="editMode" v-model="editingPerson.education" class="info-textarea" rows="3" placeholder="请输入教育背景"></textarea>
              <p v-else class="info-text">{{ person.education || '未填写' }}</p>
            </div>
            <div class="info-item">
              <span class="info-label">职业</span>
              <textarea v-if="editMode" v-model="editingPerson.occupation" class="info-textarea" rows="3" placeholder="请输入职业信息"></textarea>
              <p v-else class="info-text">{{ person.occupation || '未填写' }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 生平事迹 -->
      <div class="tab-panel" v-show="activeTab === 'biography'">
        <div class="info-card">
          <h3 class="card-title">生平事迹</h3>
          <div class="info-list vertical">
            <div class="info-item">
              <span class="info-label">生平简介</span>
              <textarea v-if="editMode" v-model="editingPerson.biography" class="info-textarea" rows="5" placeholder="请详细描述成员的生平事迹"></textarea>
              <p v-else class="info-text biography">{{ person.biography || '暂无生平介绍' }}</p>
            </div>
            <div class="info-item">
              <span class="info-label">主要成就</span>
              <textarea v-if="editMode" v-model="editingPerson.achievements" class="info-textarea" rows="4" placeholder="请描述成员的主要成就"></textarea>
              <p v-else class="info-text biography">{{ person.achievements || '暂无主要成就' }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 家族成员 -->
      <div class="tab-panel" v-show="activeTab === 'family'">
        <div class="info-card">
          <h3 class="card-title">同家族成员</h3>
          <div class="member-grid" v-if="familyMembers.length > 0">
            <div 
              class="member-item" 
              v-for="member in familyMembers" 
              :key="member.id"
              @click="router.push(`/persons/${member.id}`)"
            >
              <div class="member-avatar" :class="member.gender">
                {{ member.name.charAt(0) }}
              </div>
              <div class="member-info">
                <span class="member-name">{{ member.name }}</span>
                <span class="member-meta">
                  {{ member.generation_number ? `第${member.generation_number}代` : '' }}
                  {{ member.gender === 'male' ? '· 男' : member.gender === 'female' ? '· 女' : '' }}
                </span>
              </div>
            </div>
          </div>
          <div class="empty-hint" v-else>此家族暂无其他成员</div>
        </div>
      </div>
      
      <!-- 亲属关系 -->
      <div class="tab-panel" v-show="activeTab === 'relationships'">
        <div class="info-card">
          <div class="card-header">
            <h3 class="card-title">亲属关系</h3>
            <button class="add-btn" @click="openAddRelDialog">添加关系</button>
          </div>
          
          <div class="relation-list" v-if="relationships.length > 0">
            <div class="relation-item" v-for="rel in relationships" :key="rel.id">
              <div class="relation-type" :class="rel.relation_type">
                {{ relationTypeMap[rel.relation_type] }}
              </div>
              <div class="relation-person" @click="router.push(`/persons/${rel.relative_id}`)">
                {{ rel.relative_name }}
              </div>
              <div class="relation-extra">
                <span v-if="rel.relation_type === 'spouse' && rel.is_primary" class="primary-badge">主要配偶</span>
                <span v-if="rel.marriage_date" class="marriage-date">{{ rel.marriage_date }}</span>
              </div>
              <button class="delete-rel-btn" @click="deleteRelationship(rel.id)">删除</button>
            </div>
          </div>
          <div class="empty-hint" v-else>暂无亲属关系记录</div>
        </div>
      </div>
    </div>
    
    <!-- 错误状态 -->
    <div class="error-state" v-else>
      <div class="error-icon">⚠️</div>
      <h2>未找到此成员</h2>
      <button class="back-btn" @click="router.push('/families')">返回家族列表</button>
    </div>
    
    <!-- 添加关系对话框 -->
    <div class="dialog-overlay" v-if="showRelDialog" @click="showRelDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>添加亲属关系</h2>
          <button class="close-btn" @click="showRelDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>关系类型 *</label>
            <select v-model="relForm.relation_type">
              <option value="father">父亲</option>
              <option value="mother">母亲</option>
              <option value="spouse">配偶</option>
              <option value="child">子女</option>
            </select>
          </div>
          <div class="form-group">
            <label>关联成员 *</label>
            <select v-model="relForm.relative_id">
              <option :value="0">请选择成员</option>
              <option v-for="m in familyMembers" :key="m.id" :value="m.id">{{ m.name }}</option>
            </select>
          </div>
          <div class="form-group" v-if="relForm.relation_type === 'spouse'">
            <label class="checkbox-label">
              <input type="checkbox" v-model="relForm.is_primary" />
              <span>主要配偶</span>
            </label>
          </div>
          <div class="form-group" v-if="relForm.relation_type === 'spouse'">
            <label>结婚日期</label>
            <input type="date" v-model="relForm.marriage_date" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showRelDialog = false">取消</button>
          <button class="btn-submit" @click="createRelationship" :disabled="relLoading">
            {{ relLoading ? '保存中...' : '确定' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { personApi } from '@/api/person'
import { familyApi } from '@/api/family'
import type { Person, Family, Relationship } from '@/types'

const route = useRoute()
const router = useRouter()
const personId = Number(route.params.id)

const person = ref<Person | null>(null)
const family = ref<Family | null>(null)
const familyMembers = ref<Person[]>([])
const relationships = ref<Relationship[]>([])
const loading = ref(true)
const activeTab = ref('basic')
const editMode = ref(false)
const uploading = ref(false)
const showRelDialog = ref(false)
const relLoading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const editingPerson = ref<Partial<Person>>({})
const relForm = reactive({
  person_id: 0,
  relative_id: 0,
  relation_type: 'father' as 'father' | 'mother' | 'spouse' | 'child',
  is_primary: true,
  marriage_date: ''
})

const tabs = [
  { key: 'basic', label: '基本信息' },
  { key: 'origin', label: '出身详情' },
  { key: 'career', label: '教育职业' },
  { key: 'biography', label: '生平事迹' },
  { key: 'family', label: '家族成员' },
  { key: 'relationships', label: '亲属关系' }
]

const relationTypeMap: Record<string, string> = {
  father: '父亲',
  mother: '母亲',
  spouse: '配偶',
  child: '子女'
}

const formatDate = (date?: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const toLunarDate = (dateStr: string) => {
  // 简化的农历转换（实际项目应使用专业库）
  try {
    const date = new Date(dateStr)
    return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
  } catch {
    return dateStr
  }
}

const fetchPersonDetails = async () => {
  if (!personId || isNaN(personId)) {
    router.push('/families')
    return
  }
  
  loading.value = true
  try {
    const data = await personApi.getPerson(personId)
    person.value = data
    
    if (data?.family_id) {
      family.value = await familyApi.getFamily(data.family_id)
      const res = await personApi.getFamilyPersons(data.family_id)
      familyMembers.value = res.items.filter(p => p.id !== data.id)
    }
    
    relationships.value = await personApi.getRelationships(personId)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const startEdit = () => {
  if (person.value) {
    editingPerson.value = { ...person.value }
    editMode.value = true
  }
}

const saveEdit = async () => {
  if (!editingPerson.value.name) {
    alert('请填写成员姓名')
    return
  }
  
  try {
    const updated = await personApi.updatePerson(personId, editingPerson.value as any)
    person.value = updated
    editMode.value = false
    alert('保存成功')
  } catch (error: any) {
    console.error(error)
    alert(error?.response?.data?.detail || '保存失败')
  }
}

const cancelEdit = () => {
  editMode.value = false
  if (person.value) {
    editingPerson.value = { ...person.value }
  }
}

const deletePerson = async () => {
  if (!confirm('确定要删除此成员吗？此操作不可撤销。')) return
  
  try {
    await personApi.deletePerson(personId)
    alert('删除成功')
    router.push(`/families/${person.value?.family_id}`)
  } catch (error: any) {
    alert(error?.response?.data?.detail || '删除失败')
  }
}

const handleFileUpload = async (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file || !person.value) return
  
  uploading.value = true
  try {
    const res = await personApi.uploadPhoto(personId, file)
    person.value.photo_url = res.photo_url
    alert('上传成功')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

const openAddRelDialog = () => {
  if (!person.value) return
  relForm.person_id = person.value.id
  relForm.relative_id = 0
  relForm.relation_type = 'father'
  relForm.is_primary = true
  relForm.marriage_date = ''
  showRelDialog.value = true
}

const createRelationship = async () => {
  if (!relForm.relative_id) {
    alert('请选择关联成员')
    return
  }
  
  relLoading.value = true
  try {
    await personApi.addRelationship(personId, relForm)
    relationships.value = await personApi.getRelationships(personId)
    showRelDialog.value = false
    alert('添加成功')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '添加失败')
  } finally {
    relLoading.value = false
  }
}

const deleteRelationship = async (relId: number) => {
  if (!confirm('确定要删除此亲属关系吗？')) return
  
  try {
    await personApi.deleteRelationship(personId, relId)
    relationships.value = relationships.value.filter(r => r.id !== relId)
    alert('删除成功')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  fetchPersonDetails()
})
</script>

<style scoped>
.person-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-primary);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: none;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.back-btn svg {
  width: 14px;
  height: 14px;
}

.back-btn:hover {
  border-color: var(--cinnabar);
  color: var(--cinnabar);
}

.header-center {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.person-avatar {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: white;
  overflow: hidden;
}

.person-avatar.male {
  background: var(--indigo);
}

.person-avatar.female {
  background: var(--cinnabar);
}

.person-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.person-name {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  margin: 0;
}

.person-meta {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.header-actions {
  display: flex;
  gap: var(--space-2);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.action-btn:hover {
  border-color: var(--text-secondary);
}

.action-btn.primary {
  background: var(--cinnabar);
  color: white;
  border-color: var(--cinnabar);
}

.action-btn.primary:hover {
  background: var(--cinnabar-dark);
}

.action-btn.success {
  background: var(--bamboo);
  color: white;
  border-color: var(--bamboo);
}

.action-btn.danger {
  color: var(--cinnabar);
  border-color: var(--cinnabar);
}

/* 选项卡 */
.tabs {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-primary);
  flex-wrap: wrap;
}

.tab-btn {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--cinnabar);
  border-bottom-color: var(--cinnabar);
}

/* 信息卡片 */
.info-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.card-title {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  margin: 0 0 var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.add-btn {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.panel-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: var(--space-4);
}

.info-list {
  display: flex;
  flex-direction: column;
}

.info-list.vertical .info-item {
  flex-direction: column;
  align-items: flex-start;
}

.info-item {
  display: flex;
  align-items: center;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  width: 100px;
  flex-shrink: 0;
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.info-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.info-value-group {
  display: flex;
  flex-direction: column;
}

.info-lunar {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  margin-top: 2px;
}

.info-input,
.info-select,
.info-textarea {
  flex: 1;
  padding: var(--space-2);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.info-input:focus,
.info-select:focus,
.info-textarea:focus {
  outline: none;
  border-color: var(--cinnabar);
}

.info-text {
  font-size: var(--text-sm);
  color: var(--text-primary);
  line-height: var(--leading-relaxed);
  white-space: pre-wrap;
  margin: var(--space-2) 0 0;
}

.info-text.biography {
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

/* 照片区域 */
.photo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.photo-preview {
  width: 180px;
  height: 220px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 2px solid var(--border-primary);
}

.photo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  width: 180px;
  height: 220px;
  border: 2px dashed var(--border-primary);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  color: var(--text-tertiary);
}

.photo-placeholder svg {
  width: 48px;
  height: 48px;
}

.upload-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--cinnabar);
  border: 1px solid var(--cinnabar);
  border-radius: var(--radius-md);
  background: none;
  cursor: pointer;
}

.upload-btn:hover {
  background: var(--cinnabar-pale);
}

/* 成员网格 */
.member-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}

.member-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.member-item:hover {
  background: var(--cinnabar-pale);
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: white;
}

.member-avatar.male {
  background: var(--indigo);
}

.member-avatar.female {
  background: var(--cinnabar);
}

.member-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.member-meta {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* 关系列表 */
.relation-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.relation-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.relation-type {
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-sm);
}

.relation-type.father,
.relation-type.child {
  background: var(--indigo-pale);
  color: var(--indigo);
}

.relation-type.mother,
.relation-type.spouse {
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
}

.relation-person {
  flex: 1;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--cinnabar);
  cursor: pointer;
}

.relation-person:hover {
  text-decoration: underline;
}

.relation-extra {
  display: flex;
  gap: var(--space-2);
}

.primary-badge {
  font-size: var(--text-xs);
  padding: 2px 6px;
  background: var(--bamboo-pale);
  color: var(--bamboo);
  border-radius: var(--radius-sm);
}

.marriage-date {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.delete-rel-btn {
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  color: var(--cinnabar);
  background: none;
  border: none;
  cursor: pointer;
}

.empty-hint {
  text-align: center;
  padding: var(--space-8);
  color: var(--text-tertiary);
}

/* 加载和错误状态 */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-primary);
  border-top-color: var(--cinnabar);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--space-4);
}

.dialog {
  width: 100%;
  max-width: 400px;
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-primary);
}

.dialog-header h2 {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--text-tertiary);
  background: none;
  border: none;
  cursor: pointer;
}

.dialog-body {
  padding: var(--space-5);
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-bottom: var(--space-2);
}

.form-group select,
.form-group input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--border-primary);
}

.btn-cancel {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.btn-submit {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }
  
  .member-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-wrap: wrap;
  }
}
</style>