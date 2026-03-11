<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { personApi } from '@/api/person'
import { familyApi } from '@/api/family'
import type { Person, Family, Relationship, RelationshipCreate } from '@/types'
import { ElMessage, ElMessageBox, ElButtonGroup } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { toLunarYearWithDate } from '@/utils/lunar'
import html2pdf from 'html2pdf.js'

// HTML2PDF选项类型
type Html2PdfOptions = {
  margin: number[];
  filename: string;
  image: { type: string; quality: number };
  html2canvas: { scale: number; useCORS: boolean; logging: boolean };
  jsPDF: { unit: string; format: string; orientation: string };
}

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

const editingPerson = ref<Partial<Person>>({})
const uploading = ref(false)

const showRelDialog = ref(false)
const relForm = ref<RelationshipCreate>({
  person_id: 0,
  relative_id: 0,
  relation_type: 'father',
  is_primary: true
})

// PDF导出区域引用
const pdfContentRef = ref<HTMLElement | null>(null)

// 计算属性：获取带时间戳的照片URL（防止缓存）
const personPhotoUrl = computed(() => {
  if (!person.value?.photo_url) return '/default-avatar.png'
  // 如果URL已经包含时间戳，则不再添加
  if (person.value.photo_url.includes('?t=')) return person.value.photo_url
  return person.value.photo_url + '?t=' + new Date().getTime()
})

const relLoading = ref(false)

const relationTypeMap: Record<string, string> = {
  father: '父亲',
  mother: '母亲',
  spouse: '配偶',
  child: '子女'
}

const fetchPersonDetails = async () => {
  if (!personId || isNaN(personId)) {
    console.error('无效的参数:', personId)
    ElMessage.error('无效的参数')
    router.push('/families')
    return
  }
  
  try {
    loading.value = true
    const data = await personApi.getPerson(personId)
    person.value = data
    
    if (data) {
      if (data.family_id) {
        family.value = await familyApi.getFamily(data.family_id)
        const familyPersonsRes = await personApi.getFamilyPersons(data.family_id, { limit: 50 })
        familyMembers.value = familyPersonsRes.items.filter(p => p.id !== data.id)
      }
      relationships.value = await personApi.getRelationships(personId)
    }
  } catch (error) {
    console.error('获取成员详情失败:', error)
    ElMessage.error('获取成员详情失败')
    router.push('/families')
  } finally {
    loading.value = false
  }
}

// 初始化页面
onMounted(() => {
  fetchPersonDetails()
})

// 编辑/保存/取消/删除相关函数
const startEdit = () => {
  if (person.value) {
    editingPerson.value = { ...person.value }
    editMode.value = true
  }
}

const saveEdit = async () => {
  if (!editingPerson.value.name) {
    ElMessage.warning('请填写成员姓名')
    return
  }
  
  try {
    if (person.value) {
      const updated = await personApi.updatePerson(personId, editingPerson.value as Person)
      person.value = updated
      editMode.value = false
      ElMessage.success('更新成功')
    }
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
  }
}

const cancelEdit = () => {
  editMode.value = false
  if (person.value) {
    editingPerson.value = { ...person.value }
  }
}

const deletePerson = async () => {
  try {
    await ElMessageBox.confirm('确定要删除此成员吗？此操作不可撤销。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await personApi.deletePerson(personId)
    ElMessage.success('删除成员成功')
    router.push(`/families/${person.value?.family_id}`)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// PDF导出功能
const exportToPDF = async () => {
  if (!person.value || !pdfContentRef.value) return
  
  // 临时显示PDF内容区域
  const originalDisplay = pdfContentRef.value.style.display
  pdfContentRef.value.style.display = 'block'
  
  const opt = {
    margin: [10, 10, 10, 10],
    filename: `${person.value.name}_家族成员信息.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { 
      scale: 2,
      useCORS: true,
      logging: false
    },
    jsPDF: { 
      unit: 'mm', 
      format: 'a4', 
      orientation: 'portrait' 
    }
  }
  
  try {
    ElMessage.info('正在生成PDF，请稍候...')
    await html2pdf().set(opt).from(pdfContentRef.value).save()
    ElMessage.success('PDF导出成功')
  } catch (error) {
    console.error('PDF导出失败:', error)
    ElMessage.error('PDF导出失败')
  } finally {
    // 恢复原始显示状态
    pdfContentRef.value.style.display = originalDisplay
  }
}

// 文件上传
const handleFileUpload = (file: any) => {
  console.log('Upload file:', file)
  
  // Element Plus el-upload 返回的对象包含 raw 属性
  const rawFile = file.raw || file
  if (!rawFile || !person.value) return
  
  if (!rawFile.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }
  
  uploading.value = true
  personApi.uploadPhoto(personId, rawFile)
    .then(async (res) => {
      console.log('上传成功，返回的photo_url:', res.photo_url)
      
      // 更新 person 和 editingPerson 的 photo_url
      if (person.value) {
        person.value.photo_url = res.photo_url
      }
      if (editingPerson.value) {
        editingPerson.value.photo_url = res.photo_url
      }
      
      ElMessage.success('上传成功')
      
      // 等待一小段时间确保数据库事务已提交
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 重新获取成员数据以确保显示最新数据
      await fetchPersonDetails()
    })
    .catch(err => {
      console.error('上传失败:', err)
      ElMessage.error('上传失败')
    })
    .finally(() => {
      uploading.value = false
    })
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const openAddRelDialog = () => {
  if (!person.value) return
  relForm.value = {
    person_id: person.value.id,
    relative_id: 0,
    relation_type: 'father',
    is_primary: true
  }
  showRelDialog.value = true
}

const createRelationship = async () => {
  if (!relForm.value.relative_id) {
    ElMessage.warning('请选择关联成员')
    return
  }
  
  try {
    relLoading.value = true
    await personApi.createRelationship(relForm.value)
    relationships.value = await personApi.getRelationships(personId)
    showRelDialog.value = false
    ElMessage.success('添加关系成功')
  } catch (error) {
    console.error('创建关系失败:', error)
    ElMessage.error('创建关系失败')
  } finally {
    relLoading.value = false
  }
}

const deleteRelationship = async (relId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除此亲属关系吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await personApi.deleteRelationship(relId)
    relationships.value = relationships.value.filter(r => r.id !== relId)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除关系失败:', error)
      ElMessage.error('删除失败')
    }
  }
}
</script>

<template>
  <div class="person-detail">
    <el-page-header @back="router.go(-1)">
      <template #content>
        <div class="header-content">
          <el-avatar v-if="person" :size="40" :src="personPhotoUrl" shape="square" bg-color="#f0f2f5">
            {{ person.name?.charAt(0) || '人' }}
          </el-avatar>
          <span v-if="person" class="person-name">{{ person.name || '成员详情' }}</span>
        </div>
      </template>
      
      <template #extra>
        <el-button-group v-if="person">
          <el-button v-if="!editMode" :disabled="loading" @click="exportToPDF" type="primary">
            <el-icon><Download /></el-icon>
            导出PDF
          </el-button>
          <el-button v-if="!editMode" :disabled="loading" @click="startEdit">编辑</el-button>
          <el-button v-if="editMode" :disabled="loading" @click="saveEdit" type="success">保存</el-button>
          <el-button v-if="editMode" :disabled="loading" @click="cancelEdit">取消</el-button>
          <el-button type="danger" :disabled="loading" @click="deletePerson">删除</el-button>
        </el-button-group>
      </template>
    </el-page-header>

    <div v-if="!loading && person" class="person-detail-content">
      <el-tabs v-model="activeTab" style="margin-top: 20px;">
        <el-tab-pane label="基本信息" name="basic">
          <el-card>
            <div class="person-info">
              <div class="info-section">
                <h4>个人信息</h4>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="姓名">
                    <el-input v-if="editMode" v-model="editingPerson.name" placeholder="请输入姓名" />
                    <span v-else>{{ person.name }}</span>
                  </el-descriptions-item>
                  
                  <el-descriptions-item label="性别">
                    <el-select v-if="editMode" v-model="editingPerson.gender" placeholder="请选择性别">
                      <el-option label="男性" value="male" />
                      <el-option label="女性" value="female" />
                    </el-select>
                    <span v-else>{{ person.gender === 'male' ? '男性' : person.gender === 'female' ? '女性' : '-' }}</span>
                  </el-descriptions-item>
                  
                  <el-descriptions-item label="出生日期">
                    <el-date-picker
                      v-if="editMode"
                      v-model="editingPerson.birth_date"
                      type="date"
                      placeholder="选择日期"
                      value-format="YYYY-MM-DD"
                    />
                    <div v-else>
                      <div>{{ formatDate(person.birth_date) }}</div>
                      <div v-if="person.birth_date" class="lunar-date">
                        农历: {{ toLunarYearWithDate(person.birth_date) }}
                      </div>
                    </div>
                  </el-descriptions-item>
                  
                  <el-descriptions-item label="逝世纪念">
                    <el-date-picker
                      v-if="editMode"
                      v-model="editingPerson.death_date"
                      type="date"
                      placeholder="选择日期"
                      value-format="YYYY-MM-DD"
                    />
                    <div v-else>
                      <div>{{ formatDate(person.death_date) }}</div>
                      <div v-if="person.death_date" class="lunar-date">
                        农历: {{ toLunarYearWithDate(person.death_date) }}
                      </div>
                    </div>
                  </el-descriptions-item>
                  
                  <el-descriptions-item label="所属家族" :span="2">
                    <el-tag type="info" v-if="family">{{ family?.name }}</el-tag>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  
                  <el-descriptions-item label="字辈号">
                    <el-input 
                      v-if="editMode" 
                      v-model.number="editingPerson.generation_number"
                      type="number"
                      placeholder="请输入字辈号" 
                    />
                    <span v-else>{{ person.generation_number || '-' }}</span>
                  </el-descriptions-item>
                  
                  <el-descriptions-item label="分支名">
                    <el-input 
                      v-if="editMode" 
                      v-model="editingPerson.branch_name"
                      placeholder="请输入分支名" 
                    />
                    <span v-else>{{ person.branch_name || '-' }}</span>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
              
              <div class="info-section">
                <h4>头像照片</h4>
                <div class="avatar-upload">
                  <div class="current-avatar">
                    <el-image 
                      v-if="person && person.photo_url" 
                      :src="personPhotoUrl" 
                      :preview-src-list="[personPhotoUrl]"
                      fit="cover"
                      style="width: 200px; height: 200px; border-radius: 8px;"
                    />
                    <div v-else class="avatar-placeholder">
                      <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" width="60" height="60">
                        <path d="M512 128c141.4 0 256 114.6 256 256s-114.6 256-256 256S256 525.4 256 384 370.6 128 512 128m0-64C339.2 64 200 198.6 200 368s139.2 304 312 304 312-139.2 312-304S684.8 64 512 64z" fill="#8C92A4"></path>
                        <path d="M512 512c132.4 0 242.7 74.1 288 176H224c45.3-101.9 155.6-176 288-176m0-64c-141.4 0-256 114.6-256 256h512c0-141.4-114.6-256-256-256z" fill="#8C92A4"></path>
                      </svg>
                      <p>暂无照片</p>
                    </div>
                        
                    <div v-if="editMode" class="upload-btn">
                      <p style="font-size: 12px; color: #999; margin-bottom: 10px;">
                        photo_url: {{ person?.photo_url || 'null' }}
                      </p>
                      <el-upload
                        class="avatar-uploader"
                        :show-file-list="false"
                        accept=".jpg,.jpeg,.png,.gif"
                        action="#"
                        :auto-upload="false"
                        @change="handleFileUpload"
                      >
                        <el-button type="primary" :loading="uploading">
                          {{ uploading ? '上传中...' : '更换照片' }}
                        </el-button>
                      </el-upload>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="出身详情" name="origin">
          <el-card>
            <el-form :model="editingPerson" label-position="top" v-if="editMode && person">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="出生地">
                    <el-input v-model="editingPerson.birthplace" placeholder="请输入出生地" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="现居住地">
                    <el-input v-model="editingPerson.residence" placeholder="请输入居住地" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
            
            <el-descriptions :column="2" border v-else-if="person">
              <el-descriptions-item label="出生地" :span="2">
                {{ person.birthplace || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="现居住地" :span="2">
                {{ person.residence || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="教育职业" name="career">
          <el-card>
            <el-form :model="editingPerson" label-position="top" v-if="editMode && person">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="教育背景">
                    <el-input v-model="editingPerson.education" type="textarea" :rows="3" placeholder="请输入教育背景信息" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="职业">
                    <el-input v-model="editingPerson.occupation" type="textarea" :rows="3" placeholder="请输入职业信息" />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
            
            <el-descriptions :column="2" border v-else-if="person">
              <el-descriptions-item label="教育背景" :span="2">
                {{ person.education || '未填写' }}
              </el-descriptions-item>
              <el-descriptions-item label="职业" :span="2">
                {{ person.occupation || '未填写' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="生平事迹" name="biography">
          <el-card>
            <el-form :model="editingPerson" label-position="top" v-if="editMode && person">
              <el-form-item label="生平简介">
                <el-input 
                  v-model="editingPerson.biography" 
                  type="textarea" 
                  :rows="5"
                  placeholder="请详细描述成员的生平事迹、品德修养、重要经历等" 
                />
              </el-form-item>
              
              <el-form-item label="主要成就">
                <el-input 
                  v-model="editingPerson.achievements" 
                  type="textarea" 
                  :rows="4"
                  placeholder="请描述成员的主要成就、贡献、荣誉等" 
                />
              </el-form-item>
            </el-form>
            
            <div v-else-if="person">
              <div class="section-content">
                <h4>生平简介</h4>
                <p class="biography-text">{{ person.biography || '暂无生平介绍' }}</p>
              </div>
              
              <el-divider />
              
              <div class="section-content">
                <h4>主要成就</h4>
                <p class="biography-text">{{ person.achievements || '暂无主要成就' }}</p>
              </div>
            </div>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="家族成员" name="family">
          <el-card>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="同家族成员">
                <el-scrollbar height="200px">
                  <div class="member-grid">
                    <div 
                      v-for="member in familyMembers" 
                      :key="member.id"
                      class="member-item"
                      @click="$router.push(`/persons/${member.id}`)"
                    >
                      <el-avatar :size="40" :src="member.photo_url || '/default-avatar.png'" shape="square">
                        {{ member.name.charAt(0) }}
                      </el-avatar>
                      <div class="member-info">
                        <div class="member-name">{{ member.name }}</div>
                        <div class="member-generation">
                          第{{ member.generation_number }}代 · 
                          {{ member.gender === 'male' ? '男' : member.gender === 'female' ? '女' : '' }}
                        </div>
                      </div>
                    </div>
                    
                    <div v-if="familyMembers.length === 0" class="empty-members">
                      此家族暂无其他成员
                    </div>
                  </div>
                </el-scrollbar>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-tab-pane>
        
        <el-tab-pane label="亲属关系" name="relationships">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>亲属关系列表</span>
                <el-button type="primary" size="small" @click="openAddRelDialog">添加关系</el-button>
              </div>
            </template>
            
            <el-table :data="relationships" stripe v-if="relationships.length > 0">
              <el-table-column prop="relation_type" label="关系类型" width="100">
                <template #default="{ row }">
                  <el-tag>{{ relationTypeMap[row.relation_type] || row.relation_type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="relative_name" label="关联成员" width="150">
                <template #default="{ row }">
                  <el-link type="primary" @click="$router.push(`/persons/${row.relative_id}`)">
                    {{ row.relative_name || '-' }}
                  </el-link>
                </template>
              </el-table-column>
              <el-table-column prop="is_primary" label="主要配偶" width="100" v-if="relationships.some(r => r.relation_type === 'spouse')">
                <template #default="{ row }">
                  <el-tag v-if="row.relation_type === 'spouse'" :type="row.is_primary ? 'success' : 'info'">
                    {{ row.is_primary ? '是' : '否' }}
                  </el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="marriage_date" label="结婚日期" width="120">
                <template #default="{ row }">
                  {{ row.marriage_date ? formatDate(row.marriage_date) : '-' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button type="danger" size="small" link @click="deleteRelationship(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <el-empty v-else description="暂无亲属关系记录" />
          </el-card>
        </el-tab-pane>
      </el-tabs>
      
      <!-- PDF导出专用区域（隐藏，只包含只读内容） -->
      <div ref="pdfContentRef" class="pdf-export-content" style="display: none;">
        <div class="pdf-header">
          <h1>{{ person.name }} - 家族成员详细信息</h1>
          <div class="pdf-photo" v-if="person.photo_url">
            <img :src="personPhotoUrl" style="width: 120px; height: 150px; object-fit: cover; border-radius: 4px;" />
          </div>
        </div>
        
        <!-- 基本信息 -->
        <div class="pdf-section">
          <h2>一、基本信息</h2>
          <table class="pdf-table">
            <tr>
              <td class="label">姓名</td>
              <td>{{ person.name }}</td>
              <td class="label">性别</td>
              <td>{{ person.gender === 'male' ? '男性' : person.gender === 'female' ? '女性' : '-' }}</td>
            </tr>
            <tr>
              <td class="label">出生日期</td>
              <td>
                {{ formatDate(person.birth_date) }}
                <span v-if="person.birth_date" class="pdf-lunar">（农历: {{ toLunarYearWithDate(person.birth_date) }}）</span>
              </td>
              <td class="label">逝世纪念</td>
              <td>
                {{ formatDate(person.death_date) }}
                <span v-if="person.death_date" class="pdf-lunar">（农历: {{ toLunarYearWithDate(person.death_date) }}）</span>
              </td>
            </tr>
            <tr>
              <td class="label">所属家族</td>
              <td>{{ family?.name || '-' }}</td>
              <td class="label">字辈号</td>
              <td>{{ person.generation_number || '-' }}</td>
            </tr>
            <tr>
              <td class="label">分支名</td>
              <td colspan="3">{{ person.branch_name || '-' }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 出身详情 -->
        <div class="pdf-section">
          <h2>二、出身详情</h2>
          <table class="pdf-table">
            <tr>
              <td class="label" style="width: 120px;">出生地</td>
              <td>{{ person.birthplace || '未填写' }}</td>
            </tr>
            <tr>
              <td class="label">现居住地</td>
              <td>{{ person.residence || '未填写' }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 教育职业 -->
        <div class="pdf-section">
          <h2>三、教育职业</h2>
          <table class="pdf-table">
            <tr>
              <td class="label" style="width: 120px;">教育背景</td>
              <td>{{ person.education || '未填写' }}</td>
            </tr>
            <tr>
              <td class="label">职业</td>
              <td>{{ person.occupation || '未填写' }}</td>
            </tr>
          </table>
        </div>
        
        <!-- 生平事迹 -->
        <div class="pdf-section">
          <h2>四、生平事迹</h2>
          <div class="pdf-content-block">
            <h4>生平简介</h4>
            <p>{{ person.biography || '暂无生平介绍' }}</p>
          </div>
          <div class="pdf-content-block">
            <h4>主要成就</h4>
            <p>{{ person.achievements || '暂无主要成就' }}</p>
          </div>
        </div>
        
        <!-- 家族成员 -->
        <div class="pdf-section">
          <h2>五、同家族成员</h2>
          <table class="pdf-table" v-if="familyMembers.length > 0">
            <thead>
              <tr>
                <th style="width: 80px;">姓名</th>
                <th style="width: 60px;">性别</th>
                <th style="width: 80px;">字辈</th>
                <th>出生日期</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="member in familyMembers.slice(0, 20)" :key="member.id">
                <td>{{ member.name }}</td>
                <td>{{ member.gender === 'male' ? '男' : member.gender === 'female' ? '女' : '-' }}</td>
                <td>第{{ member.generation_number }}代</td>
                <td>{{ member.birth_date || '-' }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="pdf-empty">此家族暂无其他成员</p>
        </div>
        
        <!-- 亲属关系 -->
        <div class="pdf-section">
          <h2>六、亲属关系</h2>
          <table class="pdf-table" v-if="relationships.length > 0">
            <thead>
              <tr>
                <th style="width: 80px;">关系类型</th>
                <th style="width: 100px;">关联成员</th>
                <th style="width: 80px;">主要配偶</th>
                <th>结婚日期</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="rel in relationships" :key="rel.id">
                <td>{{ relationTypeMap[rel.relation_type] || rel.relation_type }}</td>
                <td>{{ rel.relative_name || '-' }}</td>
                <td>
                  <span v-if="rel.relation_type === 'spouse'">{{ rel.is_primary ? '是' : '否' }}</span>
                  <span v-else>-</span>
                </td>
                <td>{{ rel.marriage_date || '-' }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="pdf-empty">暂无亲属关系记录</p>
        </div>
      </div>
    </div>
    
    <el-dialog v-model="showRelDialog" title="添加亲属关系" width="500px">
      <el-form :model="relForm" label-width="100px">
        <el-form-item label="关系类型" required>
          <el-select v-model="relForm.relation_type" placeholder="请选择关系类型">
            <el-option label="父亲" value="father" />
            <el-option label="母亲" value="mother" />
            <el-option label="配偶" value="spouse" />
            <el-option label="子女" value="child" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关联成员" required>
          <el-select v-model="relForm.relative_id" placeholder="请选择成员" filterable>
            <el-option
              v-for="member in familyMembers"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="主要配偶" v-if="relForm.relation_type === 'spouse'">
          <el-switch v-model="relForm.is_primary" />
        </el-form-item>
        
        <el-form-item label="结婚日期" v-if="relForm.relation_type === 'spouse'">
          <el-date-picker
            v-model="relForm.marriage_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showRelDialog = false">取消</el-button>
        <el-button type="primary" :loading="relLoading" @click="createRelationship">确定</el-button>
      </template>
    </el-dialog>
    
    <el-card v-if="!loading && !person">
      <el-result icon="error" title="错误" subTitle="未找到此成员">
        <template #extra>
          <el-button type="primary" @click="$router.go(-1)">返回</el-button>
        </template>
      </el-result>
    </el-card>
    
    <el-skeleton v-if="loading" :rows="8" animated />
  </div>
</template>

<style scoped>
.person-detail {
  padding: 20px 0;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.person-name {
  font-size: 18px;
  font-weight: bold;
}

.person-info {
  display: flex;
  gap: 30px;
}

.info-section {
  flex: 1;
}

.info-section h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #303133;
  border-bottom: 1px solid #dcdfe6;
  padding-bottom: 8px;
}

.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.current-avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.avatar-placeholder {
  width: 200px;
  height: 200px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #c0c4cc;
}

.section-content h4 {
  margin-bottom: 10px;
  color: #303133;
}

.biography-text {
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: border-color 0.3s;
}

.member-item:hover {
  border-color: #409eff;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.member-generation {
  font-size: 12px;
  color: #909399;
}

.empty-members {
  grid-column: 1 / -1;
  text-align: center;
  color: #909399;
  padding: 20px;
}

.upload-btn {
  display: flex;
  justify-content: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lunar-date {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* PDF导出样式 */
@media print {
  .person-detail {
    padding: 0;
  }
  
  .el-page-header {
    display: none;
  }
  
  .el-tabs__header {
    display: none;
  }
  
  .el-tab-pane {
    display: block !important;
  }
  
  .el-card {
    break-inside: avoid;
    margin-bottom: 20px;
  }
}

/* PDF导出容器样式 */
.person-detail-content {
  background: white;
}

/* PDF导出内容区域样式 */
.pdf-export-content {
  padding: 20px;
  background: white;
  font-family: 'SimSun', 'Songti SC', serif;
}

.pdf-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #333;
}

.pdf-header h1 {
  font-size: 24px;
  margin-bottom: 15px;
  color: #333;
}

.pdf-photo {
  margin-top: 10px;
}

.pdf-section {
  margin-bottom: 25px;
  page-break-inside: avoid;
}

.pdf-section h2 {
  font-size: 16px;
  color: #333;
  border-left: 4px solid #409eff;
  padding-left: 10px;
  margin-bottom: 15px;
}

.pdf-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.pdf-table td,
.pdf-table th {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.pdf-table .label {
  background-color: #f5f7fa;
  font-weight: bold;
  width: 100px;
  color: #606266;
}

.pdf-table th {
  background-color: #f5f7fa;
  font-weight: bold;
  color: #606266;
}

.pdf-lunar {
  color: #909399;
  font-size: 11px;
}

.pdf-content-block {
  margin-bottom: 15px;
}

.pdf-content-block h4 {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.pdf-content-block p {
  font-size: 12px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.pdf-empty {
  color: #909399;
  font-size: 12px;
  text-align: center;
  padding: 20px;
}
</style>