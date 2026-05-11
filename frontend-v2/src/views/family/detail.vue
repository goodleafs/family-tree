<template>
  <div class="family-detail-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push('/families')">
        <svg viewBox="0 0 16 16" fill="none">
          <path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        返回
      </button>
      <h1 class="page-title">{{ family?.name || '家族详情' }}</h1>
      <router-link :to="`/families/${familyId}/edit`" class="edit-btn">编辑</router-link>
    </div>
    
    <!-- 选项卡 -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        class="tab-item"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    
    <!-- 内容区 -->
    <div class="tab-content" v-if="family">
      <!-- 家族信息 -->
      <div v-if="activeTab === 'info'" class="info-panel">
        <div class="info-card">
          <div class="info-header">
            <h3>基本信息</h3>
          </div>
          <div class="info-body">
            <div class="info-item">
              <span class="info-label">家族名称</span>
              <span class="info-value">{{ family.name }}</span>
            </div>
            <div class="info-item" v-if="family.surname">
              <span class="info-label">姓氏</span>
              <span class="info-value">{{ family.surname }}氏</span>
            </div>
            <div class="info-item">
              <span class="info-label">简介</span>
              <span class="info-value">{{ family.description || '暂无简介' }}</span>
            </div>
            <div class="info-item" v-if="family.history">
              <span class="info-label">家族史</span>
              <span class="info-value">{{ family.history }}</span>
            </div>
            <div class="info-item" v-if="family.family_motto">
              <span class="info-label">家训</span>
              <span class="info-value motto">{{ family.family_motto }}</span>
            </div>
            <div class="info-item" v-if="family.generation_names?.length">
              <span class="info-label">字辈</span>
              <span class="info-value">{{ family.generation_names.join('、') }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">状态</span>
              <span class="info-value" :class="{ public: family.is_public }">
                {{ family.is_public ? '公开' : '私密' }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">成员数量</span>
              <span class="info-value">{{ family.person_count || 0 }} 人</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 成员列表 -->
      <div v-if="activeTab === 'members'" class="members-panel">
        <div class="panel-header">
          <h3>成员列表 ({{ persons.length }}人)</h3>
          <button class="add-btn" @click="openAddPersonDialog">添加成员</button>
        </div>
        
        <div class="members-table" v-if="persons.length > 0">
          <div class="table-header">
            <div class="col-name">姓名</div>
            <div class="col-gender">性别</div>
            <div class="col-birth">出生日期</div>
            <div class="col-gen">世代</div>
            <div class="col-occupation">职业</div>
            <div class="col-actions">操作</div>
          </div>
          <div class="table-body">
            <div class="table-row" v-for="person in persons" :key="person.id">
              <div class="col-name" @click="$router.push(`/persons/${person.id}`)">
                <div class="person-cell">
                  <div class="person-avatar" :class="person.gender">
                    {{ person.name?.charAt(0) || '人' }}
                  </div>
                  <span class="person-name">{{ person.name }}</span>
                </div>
              </div>
              <div class="col-gender">
                <span class="gender-tag" :class="person.gender">
                  {{ person.gender === 'male' ? '男' : person.gender === 'female' ? '女' : '-' }}
                </span>
              </div>
              <div class="col-birth">{{ person.birth_date || '-' }}</div>
              <div class="col-gen">{{ person.generation_number ? `第${person.generation_number}代` : '-' }}</div>
              <div class="col-occupation">{{ person.occupation || '-' }}</div>
              <div class="col-actions">
                <button class="action-btn view" @click="$router.push(`/persons/${person.id}`)">详情</button>
                <button class="action-btn delete" @click="handleDeletePerson(person)">删除</button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="empty-hint" v-else>
          <div class="empty-icon">👥</div>
          <p>暂无成员，点击上方按钮添加</p>
        </div>
      </div>
      
      <!-- 族谱树 -->
      <div v-if="activeTab === 'tree'" class="tree-panel">
        <div class="panel-header">
          <h3>族谱树可视化</h3>
          <div class="header-actions">
            <select v-model="selectedTreePerson" class="tree-select" @change="loadFamilyTree">
              <option :value="0">选择起始成员</option>
              <option v-for="p in persons" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <router-link to="/tree" class="view-full-btn">查看完整族谱树</router-link>
          </div>
        </div>
        
        <div class="tree-info" v-if="treeData">
          <span class="tree-stats">共 {{ treeData.total_members }} 人，{{ treeData.total_generations }} 代</span>
          <span class="tree-hint">（可拖拽缩放，点击节点查看详情）</span>
        </div>
        
        <div class="tree-container" v-if="persons.length > 0">
          <div v-if="!treeData && !treeLoading" class="tree-empty">
            <p>请选择起始成员查看族谱树</p>
          </div>
          <div v-else ref="treeContainerRef" class="tree-visualization" v-loading="treeLoading">
            <svg ref="treeSvgRef" class="tree-svg"></svg>
          </div>
        </div>
        
        <div class="empty-hint" v-else>
          <div class="empty-icon">🌳</div>
          <p>暂无成员数据，请先添加成员</p>
        </div>
      </div>
      
      <!-- 家族相册 -->
      <div v-if="activeTab === 'album'" class="album-panel">
        <div class="panel-header">
          <h3>家族相册</h3>
          <router-link :to="`/families/${familyId}/albums`" class="view-full-btn">进入相册</router-link>
        </div>
        <div class="empty-hint">
          <div class="empty-icon">📸</div>
          <p>点击"进入相册"查看和管理家族照片</p>
        </div>
      </div>

      <!-- 文献库 -->
      <div v-if="activeTab === 'document'" class="document-panel">
        <div class="panel-header">
          <h3>文献库</h3>
          <router-link :to="`/families/${familyId}/documents`" class="view-full-btn">进入文献库</router-link>
        </div>
        <div class="empty-hint">
          <div class="empty-icon">📄</div>
          <p>点击"进入文献库"管理老谱、契约、著作等文献</p>
        </div>
      </div>

      <!-- 人物传记 -->
      <div v-if="activeTab === 'biography'" class="biography-panel">
        <div class="panel-header">
          <h3>人物传记</h3>
          <router-link :to="`/families/${familyId}/biographies`" class="view-full-btn">进入传记</router-link>
        </div>
        <div class="empty-hint">
          <div class="empty-icon">📖</div>
          <p>点击"进入传记"为家族名人创建独立传记页面</p>
        </div>
      </div>

      <!-- 功德榜 -->
      <div v-if="activeTab === 'merit'" class="merit-panel">
        <div class="panel-header">
          <h3>功德榜</h3>
          <router-link :to="`/families/${familyId}/merit`" class="view-full-btn">进入功德榜</router-link>
        </div>
        <div class="empty-hint">
          <div class="empty-icon">🏆</div>
          <p>点击"进入功德榜"记录宗亲修谱捐款</p>
        </div>
      </div>

      <!-- 族谱权限管理 -->
      <div v-if="activeTab === 'roles'" class="roles-panel">
        <div class="panel-header">
          <h3>族谱角色管理</h3>
          <button v-if="canManageRoles" class="add-btn" @click="openAddMemberDialog">添加成员</button>
        </div>
        
        <div class="permission-notice" v-if="!canManageRoles">
          <span>您没有权限管理成员角色，需要家族管理员或超级管理员权限</span>
        </div>
        
        <div class="members-table" v-if="familyMembers.length > 0">
          <div class="table-header">
            <div class="col-username">用户名</div>
            <div class="col-email">邮箱</div>
            <div class="col-role">角色</div>
            <div class="col-super">超级管理员</div>
            <div class="col-joined">加入时间</div>
            <div class="col-actions" v-if="canManageRoles">操作</div>
          </div>
          <div class="table-body">
            <div class="table-row" v-for="member in familyMembers" :key="member.id">
              <div class="col-username">
                <span class="username">{{ member.username }}</span>
                <span v-if="member.user_id === userStore.user?.id" class="current-badge">当前用户</span>
              </div>
              <div class="col-email">{{ member.email || '-' }}</div>
              <div class="col-role">
                <select 
                  v-if="canManageRoles && member.user_id !== userStore.user?.id"
                  v-model="member.role"
                  @change="handleRoleChange(member)"
                  class="role-select"
                >
                  <option v-for="opt in roleOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
                <span v-else class="role-tag" :class="member.role">{{ roleTypeMap[member.role] || member.role }}</span>
              </div>
              <div class="col-super">
                <span v-if="member.is_superuser" class="super-badge">是</span>
                <span v-else class="super-no">否</span>
              </div>
              <div class="col-joined">{{ formatDate(member.created_at) }}</div>
              <div class="col-actions" v-if="canManageRoles">
                <button 
                  v-if="member.user_id !== userStore.user?.id"
                  class="action-btn delete" 
                  @click="handleRemoveMember(member)"
                >移除</button>
              </div>
            </div>
          </div>
        </div>
        
        <div class="empty-hint" v-else>
          <div class="empty-icon">👤</div>
          <p>暂无家族成员</p>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div class="loading-state" v-else>
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 添加成员对话框 -->
    <div class="dialog-overlay" v-if="showAddPersonDialog" @click="showAddPersonDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>添加成员</h2>
          <button class="close-btn" @click="showAddPersonDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>姓名 <span class="required">*</span></label>
            <input v-model="newPerson.name" placeholder="请输入姓名" />
          </div>
          <div class="form-group">
            <label>性别</label>
            <div class="radio-group">
              <label class="radio-item">
                <input type="radio" v-model="newPerson.gender" value="male" />
                <span>男</span>
              </label>
              <label class="radio-item">
                <input type="radio" v-model="newPerson.gender" value="female" />
                <span>女</span>
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>出生日期</label>
            <input type="date" v-model="newPerson.birth_date" />
          </div>
          <div class="form-group">
            <label>世代</label>
            <input type="number" v-model.number="newPerson.generation_number" placeholder="第几代" />
          </div>
          <div class="form-group">
            <label>职业</label>
            <input v-model="newPerson.occupation" placeholder="请输入职业" />
          </div>
          <div class="form-group">
            <label>生平简介</label>
            <textarea v-model="newPerson.biography" rows="3" placeholder="请输入生平简介"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showAddPersonDialog = false">取消</button>
          <button class="btn-submit" @click="handleAddPerson" :disabled="addPersonLoading">
            {{ addPersonLoading ? '添加中...' : '添加' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加系统用户为家族成员对话框 -->
    <div class="dialog-overlay" v-if="showAddMemberDialog" @click="showAddMemberDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>添加家族成员</h2>
          <button class="close-btn" @click="showAddMemberDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>选择用户 <span class="required">*</span></label>
            <select v-model="selectedUserId">
              <option :value="0">请选择用户</option>
              <option v-for="user in usersList" :key="user.id" :value="user.id">
                {{ user.username }}{{ user.email ? ` (${user.email})` : '' }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>角色 <span class="required">*</span></label>
            <select v-model="selectedRole">
              <option v-for="opt in roleOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showAddMemberDialog = false">取消</button>
          <button class="btn-submit" @click="handleAddMember" :disabled="addMemberLoading">
            {{ addMemberLoading ? '添加中...' : '添加' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { familyApi } from '@/api/family'
import { personApi } from '@/api/person'
import { adminApi } from '@/api/admin'
import { useUserStore } from '@/stores/user'
import type { Family, Person, FamilyMemberInfo, User, FamilyTree, TreeNode } from '@/types'
import * as d3 from 'd3'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const familyId = parseInt(route.params.id as string)

const family = ref<Family | null>(null)
const persons = ref<Person[]>([])
const familyMembers = ref<FamilyMemberInfo[]>([])
const activeTab = ref('info')

// 选项卡配置
const tabs = [
  { key: 'info', label: '家族信息' },
  { key: 'members', label: '成员列表' },
  { key: 'tree', label: '族谱树' },
  { key: 'album', label: '家族相册' },
  { key: 'document', label: '文献库' },
  { key: 'biography', label: '人物传记' },
  { key: 'merit', label: '功德榜' },
  { key: 'roles', label: '权限管理' }
]

// 角色配置
const roleOptions = [
  { value: 'admin', label: '家族管理员' },
  { value: 'family_admin', label: '家族信息管理员' },
  { value: 'editor', label: '编辑者' },
  { value: 'member', label: '普通成员' }
]

const roleTypeMap: Record<string, string> = {
  admin: '家族管理员',
  family_admin: '家族信息管理员',
  editor: '编辑者',
  member: '普通成员'
}

// 添加成员相关
const showAddPersonDialog = ref(false)
const addPersonLoading = ref(false)
const newPerson = ref({
  family_id: familyId,
  name: '',
  gender: 'male' as 'male' | 'female',
  birth_date: '',
  generation_number: undefined as number | undefined,
  occupation: '',
  biography: ''
})

// 族谱树相关
const treeData = ref<FamilyTree | null>(null)
const treeLoading = ref(false)
const treeSvgRef = ref<SVGSVGElement | null>(null)
const treeContainerRef = ref<HTMLDivElement | null>(null)
const selectedTreePerson = ref(0)

// 添加系统用户相关
const showAddMemberDialog = ref(false)
const usersList = ref<User[]>([])
const selectedUserId = ref(0)
const selectedRole = ref('member')
const addMemberLoading = ref(false)

// D3树节点类型
interface D3TreeNode {
  id: number
  name: string
  gender?: string
  birth_date?: string
  death_date?: string
  photo_url?: string
  generation_number?: number
  children?: D3TreeNode[]
}

// 权限判断
const canManageRoles = computed(() => {
  if (userStore.isSuperuser) return true
  const currentMember = familyMembers.value.find(m => m.user_id === userStore.user?.id)
  return currentMember?.role === 'admin'
})

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 获取家族信息
const fetchFamily = async () => {
  try {
    family.value = await familyApi.getFamily(familyId)
  } catch (error) {
    console.error(error)
    alert('获取家族信息失败')
  }
}

// 获取成员列表
const fetchPersons = async () => {
  try {
    const res = await personApi.getFamilyPersons(familyId)
    persons.value = res.items
  } catch (error) {
    console.error(error)
  }
}

// 获取家族成员（系统用户）
const fetchFamilyMembers = async () => {
  try {
    familyMembers.value = await familyApi.getFamilyMembers(familyId)
  } catch (error) {
    console.error(error)
  }
}

// 打开添加成员对话框
const openAddPersonDialog = () => {
  newPerson.value = {
    family_id: familyId,
    name: '',
    gender: 'male',
    birth_date: '',
    generation_number: undefined,
    occupation: '',
    biography: ''
  }
  showAddPersonDialog.value = true
}

// 添加成员
const handleAddPerson = async () => {
  if (!newPerson.value.name) {
    alert('请输入成员姓名')
    return
  }
  
  addPersonLoading.value = true
  try {
    await personApi.createPerson({
      family_id: familyId,
      name: newPerson.value.name,
      gender: newPerson.value.gender,
      birth_date: newPerson.value.birth_date || undefined,
      generation_number: newPerson.value.generation_number,
      occupation: newPerson.value.occupation || undefined,
      biography: newPerson.value.biography || undefined
    })
    showAddPersonDialog.value = false
    await fetchPersons()
    alert('添加成功')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '添加失败')
  } finally {
    addPersonLoading.value = false
  }
}

// 删除成员
const handleDeletePerson = async (person: Person) => {
  if (!confirm(`确定要删除成员"${person.name}"吗？此操作不可撤销。`)) return
  
  try {
    await personApi.deletePerson(person.id)
    await fetchPersons()
    alert('删除成功')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '删除失败')
  }
}

// 转换族谱树数据
const transformTreeData = (node: TreeNode): D3TreeNode => {
  const result: D3TreeNode = {
    id: node.id,
    name: node.name,
    gender: node.gender,
    birth_date: node.birth_date,
    death_date: node.death_date,
    photo_url: node.photo_url,
    generation_number: node.generation_number,
    children: []
  }
  
  if (node.spouses && node.spouses.length > 0) {
    node.spouses.forEach(spouse => {
      result.children!.push({
        id: spouse.id,
        name: spouse.name + ' (配偶)',
        gender: spouse.gender,
        birth_date: spouse.birth_date,
        death_date: spouse.death_date,
        photo_url: spouse.photo_url,
        generation_number: spouse.generation_number,
        children: []
      })
    })
  }
  
  if (node.children && node.children.length > 0) {
    node.children.forEach(child => {
      result.children!.push(transformTreeData(child))
    })
  }
  
  if (result.children!.length === 0) {
    delete result.children
  }
  
  return result
}

// 渲染族谱树
const renderTree = () => {
  if (!treeData.value || !treeSvgRef.value || !treeContainerRef.value) return
  
  const svg = d3.select(treeSvgRef.value)
  svg.selectAll('*').remove()
  
  const containerWidth = treeContainerRef.value.clientWidth
  
  // 计算树的深度来动态调整高度
  const root = d3.hierarchy<D3TreeNode>(transformTreeData(treeData.value.root))
  const treeLayout = d3.tree<D3TreeNode>()
  
  // 先计算布局以获取深度信息
  treeLayout.nodeSize([150, 100])(root)
  
  const maxDepth = root.height || 0
  const containerHeight = Math.max(500, (maxDepth + 1) * 120 + 100)
  
  const margin = { top: 40, right: 60, bottom: 40, left: 60 }
  const width = containerWidth - margin.left - margin.right
  const height = containerHeight - margin.top - margin.bottom
  
  svg.attr('width', containerWidth).attr('height', containerHeight)
  
  const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`)
  
  // 使用垂直布局
  treeLayout.size([width, height])
  treeLayout(root)
  
  // 缩放功能
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })
  svg.call(zoom)
  
  // 绘制连线 - 垂直方向
  g.selectAll('.link')
    .data(root.links())
    .enter()
    .append('path')
    .attr('class', 'link')
    .attr('fill', 'none')
    .attr('stroke', '#d4c5b0')
    .attr('stroke-width', 2)
    .attr('d', d3.linkVertical<any, any>().x((d: any) => d.x).y((d: any) => d.y))
  
  // 绘制节点
  const nodes = g.selectAll('.node')
    .data(root.descendants())
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr('transform', (d: any) => `translate(${d.x},${d.y})`)
    .style('cursor', 'pointer')
    .on('click', (event: MouseEvent, d: any) => {
      event.stopPropagation()
      router.push(`/persons/${d.data.id}`)
    })
  
  // 节点背景
  nodes.append('rect')
    .attr('x', -60)
    .attr('y', -20)
    .attr('width', 120)
    .attr('height', 40)
    .attr('rx', 6)
    .attr('ry', 6)
    .attr('fill', (d: any) => {
      if (d.data.gender === 'male') return '#e8f0f8'
      if (d.data.gender === 'female') return '#fef0f2'
      return '#f5f5f0'
    })
    .attr('stroke', (d: any) => {
      if (d.data.gender === 'male') return '#2c4a6e'
      if (d.data.gender === 'female') return '#c41e3a'
      return '#d4c5b0'
    })
    .attr('stroke-width', 2)
  
  // 节点文字
  nodes.append('text')
    .attr('dy', 5)
    .attr('text-anchor', 'middle')
    .attr('font-size', '14px')
    .attr('font-family', '"Noto Serif SC", serif')
    .attr('fill', '#333')
    .text((d: any) => {
      const name = d.data.name
      return name.length > 8 ? name.substring(0, 8) + '...' : name
    })
  
  // 提示信息
  nodes.append('title').text((d: any) => {
    const data = d.data
    let tooltip = `姓名: ${data.name}\n`
    if (data.gender) tooltip += `性别: ${data.gender === 'male' ? '男' : '女'}\n`
    if (data.birth_date) tooltip += `出生: ${data.birth_date}\n`
    if (data.death_date) tooltip += `逝世: ${data.death_date}\n`
    if (data.generation_number) tooltip += `第${data.generation_number}代`
    return tooltip
  })
  
  // 图例
  const legend = svg.append('g').attr('transform', 'translate(10, 10)')
  
  legend.append('rect').attr('width', 16).attr('height', 16).attr('fill', '#e8f0f8').attr('stroke', '#2c4a6e').attr('stroke-width', 2).attr('rx', 3)
  legend.append('text').attr('x', 22).attr('y', 13).attr('font-size', '12px').attr('fill', '#666').text('男性')
  
  legend.append('rect').attr('y', 24).attr('width', 16).attr('height', 16).attr('fill', '#fef0f2').attr('stroke', '#c41e3a').attr('stroke-width', 2).attr('rx', 3)
  legend.append('text').attr('x', 22).attr('y', 37).attr('font-size', '12px').attr('fill', '#666').text('女性')
}

// 加载族谱树
const loadFamilyTree = async () => {
  if (!selectedTreePerson.value) {
    treeData.value = null
    return
  }
  
  treeLoading.value = true
  try {
    const res = await personApi.getFamilyTree(selectedTreePerson.value)
    treeData.value = res
    await nextTick()
    renderTree()
  } catch (error) {
    console.error(error)
    alert('加载族谱树失败')
  } finally {
    treeLoading.value = false
  }
}

// 打开添加系统用户对话框
const openAddMemberDialog = async () => {
  try {
    const res = await adminApi.getUsers({ limit: 1000 })
    const memberUserIds = new Set(familyMembers.value.map(m => m.user_id))
    usersList.value = res.items.filter(u => !memberUserIds.has(u.id) && u.id !== userStore.user?.id)
    selectedUserId.value = 0
    selectedRole.value = 'member'
    showAddMemberDialog.value = true
  } catch (error) {
    alert('获取用户列表失败')
  }
}

// 添加系统用户为家族成员
const handleAddMember = async () => {
  if (!selectedUserId.value) {
    alert('请选择要添加的用户')
    return
  }
  
  addMemberLoading.value = true
  try {
    await familyApi.addFamilyMember(familyId, {
      user_id: selectedUserId.value,
      role: selectedRole.value
    })
    showAddMemberDialog.value = false
    await fetchFamilyMembers()
    alert('添加成功')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '添加失败')
  } finally {
    addMemberLoading.value = false
  }
}

// 移除家族成员
const handleRemoveMember = async (member: FamilyMemberInfo) => {
  if (!confirm(`确定要将 ${member.username} 从家族中移除吗？`)) return
  
  try {
    await familyApi.removeFamilyMember(familyId, member.user_id)
    await fetchFamilyMembers()
    alert('移除成功')
  } catch (error: any) {
    alert(error?.response?.data?.detail || '移除失败')
  }
}

// 修改成员角色
const handleRoleChange = async (member: FamilyMemberInfo) => {
  if (!confirm(`确定要将 ${member.username} 的角色修改为 "${roleTypeMap[member.role]}" 吗？`)) {
    await fetchFamilyMembers()
    return
  }
  
  try {
    await familyApi.updateMemberRole(familyId, member.user_id, member.role)
    alert('角色修改成功')
  } catch (error: any) {
    await fetchFamilyMembers()
    alert(error?.response?.data?.detail || '修改失败')
  }
}

// 监听选项卡变化，自动加载族谱树
watch(activeTab, (newTab) => {
  if (newTab === 'tree' && persons.value.length > 0 && !selectedTreePerson.value) {
    selectedTreePerson.value = persons.value[0].id
    loadFamilyTree()
  }
})

onMounted(() => {
  fetchFamily()
  fetchPersons()
  fetchFamilyMembers()
})
</script>

<style scoped>
.family-detail-page {
  max-width: 1100px;
  margin: 0 auto;
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

.page-title {
  flex: 1;
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.edit-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--cinnabar);
  border: 1px solid var(--cinnabar);
  border-radius: var(--radius-md);
  text-decoration: none;
}

.edit-btn:hover {
  background: var(--cinnabar);
  color: white;
}

/* 选项卡 */
.tabs {
  display: flex;
  gap: var(--space-1);
  margin-bottom: var(--space-6);
  border-bottom: 1px solid var(--border-primary);
}

.tab-item {
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-item:hover {
  color: var(--text-primary);
}

.tab-item.active {
  color: var(--cinnabar);
  border-bottom-color: var(--cinnabar);
}

/* 信息卡片 */
.info-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
}

.info-header {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-primary);
}

.info-header h3 {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  margin: 0;
}

.info-body {
  padding: var(--space-5);
}

.info-item {
  display: flex;
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
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.info-value.motto {
  font-family: var(--font-title);
  font-style: italic;
  color: var(--cinnabar);
}

.info-value.public {
  color: var(--bamboo);
}

/* 面板头部 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.panel-header h3 {
  font-family: var(--font-title);
  font-size: var(--text-lg);
  margin: 0;
}

.add-btn {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: white;
  background: var(--cinnabar);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.add-btn:hover {
  background: var(--cinnabar-dark);
}

/* 表格样式 */
.members-table {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-header {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-tertiary);
}

.table-header > div {
  padding: var(--space-3);
}

.table-body {
  max-height: 500px;
  overflow-y: auto;
}

.table-row {
  display: flex;
  border-bottom: 1px solid var(--border-light);
  transition: background var(--transition-fast);
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: var(--bg-secondary);
}

.table-row > div {
  padding: var(--space-3);
  display: flex;
  align-items: center;
}

.col-name { width: 180px; }
.col-gender { width: 80px; }
.col-birth { width: 120px; }
.col-gen { width: 100px; }
.col-occupation { flex: 1; }
.col-actions { width: 140px; justify-content: flex-end; gap: var(--space-2); }
.col-username { width: 180px; }
.col-email { width: 200px; }
.col-role { width: 150px; }
.col-super { width: 100px; }
.col-joined { width: 150px; }

.person-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.person-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: white;
}

.person-avatar.male { background: var(--indigo); }
.person-avatar.female { background: var(--cinnabar); }

.person-name {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.person-name:hover {
  color: var(--cinnabar);
}

.gender-tag {
  padding: 2px 8px;
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
}

.gender-tag.male {
  background: var(--indigo-pale);
  color: var(--indigo);
}

.gender-tag.female {
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
}

.action-btn {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
  cursor: pointer;
  border: none;
}

.action-btn.view {
  background: var(--indigo-pale);
  color: var(--indigo);
}

.action-btn.delete {
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
}

/* 空状态 */
.empty-hint {
  text-align: center;
  padding: var(--space-12);
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-3);
}

/* 族谱树样式 */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.tree-select {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
  min-width: 160px;
}

.view-full-btn {
  font-size: var(--text-sm);
  color: var(--cinnabar);
  text-decoration: none;
}

.view-full-btn:hover {
  text-decoration: underline;
}

.tree-info {
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
}

.tree-stats {
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.tree-hint {
  color: var(--text-tertiary);
}

.tree-container {
  min-height: 500px;
}

.tree-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  color: var(--text-tertiary);
}

.tree-visualization {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-primary);
  overflow: auto;
}

.tree-svg {
  display: block;
  min-width: 100%;
  min-height: 500px;
}

/* 权限管理 */
.permission-notice {
  padding: var(--space-3) var(--space-4);
  background: #fef3cd;
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
  color: #856404;
}

.username {
  font-weight: var(--font-medium);
}

.current-badge {
  margin-left: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.role-select {
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
}

.role-tag {
  padding: 2px 8px;
  font-size: var(--text-xs);
  border-radius: var(--radius-sm);
}

.role-tag.admin { background: #f8d7da; color: #721c24; }
.role-tag.family_admin { background: #fff3cd; color: #856404; }
.role-tag.editor { background: #d4edda; color: #155724; }
.role-tag.member { background: #e2e3e5; color: #383d41; }

.super-badge {
  font-size: var(--text-xs);
  color: var(--cinnabar);
}

.super-no {
  color: var(--text-tertiary);
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-4);
}

.dialog {
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  overflow-y: auto;
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-bottom: var(--space-2);
  color: var(--text-primary);
}

.required {
  color: var(--cinnabar);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  background: var(--bg-primary);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--cinnabar);
}

.radio-group {
  display: flex;
  gap: var(--space-4);
}

.radio-item {
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
  cursor: not-allowed;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  color: var(--text-tertiary);
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

/* 响应式 */
@media (max-width: 768px) {
  .table-header,
  .table-row {
    display: block;
  }
  
  .table-header {
    display: none;
  }
  
  .table-row {
    padding: var(--space-3);
    flex-direction: column;
    gap: var(--space-2);
  }
  
  .table-row > div {
    padding: 0;
    width: 100% !important;
    justify-content: space-between;
  }
  
  .col-actions {
    justify-content: flex-start;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>