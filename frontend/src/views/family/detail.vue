<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { familyApi } from '@/api/family'
import { personApi } from '@/api/person'
import { adminApi } from '@/api/admin'
import { useUserStore } from '@/stores/user'
import type { Family, Person, FamilyMemberInfo, User, FamilyTree, TreeNode } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as d3 from 'd3'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const familyId = parseInt(route.params.id as string)

const family = ref<Family | null>(null)
const persons = ref<Person[]>([])
const familyMembers = ref<FamilyMemberInfo[]>([])
const loading = ref(false)
const membersLoading = ref(false)
const activeTab = ref('info')

const addPersonDialog = ref(false)
const newPerson = ref<Partial<Person>>({
  family_id: familyId,
  name: '',
  gender: undefined,
  birth_date: undefined,
  biography: ''
})

// 家谱树相关
const treeData = ref<FamilyTree | null>(null)
const treeLoading = ref(false)
const svgRef = ref<SVGSVGElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)
const treePersons = ref<Person[]>([])
const selectedTreePerson = ref<number | null>(null)

interface D3TreeNode {
  id: number
  name: string
  gender?: string
  birth_date?: string
  death_date?: string
  photo_url?: string
  generation_number?: number
  children?: D3TreeNode[]
  spouses?: D3TreeNode[]
}

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

const renderTree = () => {
  if (!treeData.value || !svgRef.value || !containerRef.value) return
  
  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()
  
  const containerWidth = containerRef.value.clientWidth
  const containerHeight = 500
  
  const margin = { top: 40, right: 120, bottom: 40, left: 120 }
  const width = containerWidth - margin.left - margin.right
  const height = containerHeight - margin.top - margin.bottom
  
  svg.attr('width', containerWidth)
     .attr('height', containerHeight)
  
  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  
  const root = d3.hierarchy<D3TreeNode>(transformTreeData(treeData.value.root))
  
  const treeLayout = d3.tree<D3TreeNode>()
    .size([height, width])
  
  treeLayout(root)
  
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })
  
  svg.call(zoom)
  
  g.selectAll('.link')
    .data(root.links())
    .enter()
    .append('path')
    .attr('class', 'link')
    .attr('fill', 'none')
    .attr('stroke', '#ccc')
    .attr('stroke-width', 2)
    .attr('d', d3.linkHorizontal<any, any>()
      .x((d: any) => d.y)
      .y((d: any) => d.x))
  
  const nodes = g.selectAll('.node')
    .data(root.descendants())
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr('transform', (d: any) => `translate(${d.y},${d.x})`)
    .style('cursor', 'pointer')
    .on('click', (event: MouseEvent, d: any) => {
      event.stopPropagation()
      router.push(`/persons/${d.data.id}`)
    })
  
  nodes.append('rect')
    .attr('x', -60)
    .attr('y', -20)
    .attr('width', 120)
    .attr('height', 40)
    .attr('rx', 6)
    .attr('ry', 6)
    .attr('fill', (d: any) => {
      const gender = d.data.gender
      if (gender === 'male') return '#e6f7ff'
      if (gender === 'female') return '#fff0f6'
      return '#f5f5f5'
    })
    .attr('stroke', (d: any) => {
      const gender = d.data.gender
      if (gender === 'male') return '#1890ff'
      if (gender === 'female') return '#eb2f96'
      return '#d9d9d9'
    })
    .attr('stroke-width', 2)
  
  nodes.append('text')
    .attr('dy', 5)
    .attr('text-anchor', 'middle')
    .attr('font-size', '14px')
    .attr('fill', '#333')
    .text((d: any) => {
      const name = d.data.name
      return name.length > 8 ? name.substring(0, 8) + '...' : name
    })
  
  nodes.append('title')
    .text((d: any) => {
      const data = d.data
      let tooltip = `姓名: ${data.name}\n`
      if (data.gender) tooltip += `性别: ${data.gender === 'male' ? '男' : '女'}\n`
      if (data.birth_date) tooltip += `出生: ${data.birth_date}\n`
      if (data.death_date) tooltip += `逝世: ${data.death_date}\n`
      if (data.generation_number) tooltip += `第${data.generation_number}代`
      return tooltip
    })
  
  const legend = svg.append('g')
    .attr('transform', `translate(10, 10)`)
  
  legend.append('rect')
    .attr('width', 16)
    .attr('height', 16)
    .attr('fill', '#e6f7ff')
    .attr('stroke', '#1890ff')
    .attr('stroke-width', 2)
    .attr('rx', 3)
  
  legend.append('text')
    .attr('x', 22)
    .attr('y', 13)
    .attr('font-size', '12px')
    .attr('fill', '#666')
    .text('男性')
  
  legend.append('rect')
    .attr('y', 24)
    .attr('width', 16)
    .attr('height', 16)
    .attr('fill', '#fff0f6')
    .attr('stroke', '#eb2f96')
    .attr('stroke-width', 2)
    .attr('rx', 3)
  
  legend.append('text')
    .attr('x', 22)
    .attr('y', 37)
    .attr('font-size', '12px')
    .attr('fill', '#666')
    .text('女性')
}

const loadFamilyTree = async (personId?: number) => {
  if (!personId && persons.value.length === 0) {
    await fetchPersons()
  }
  
  const targetPersonId = personId || (persons.value.length > 0 ? persons.value[0].id : null)
  
  if (!targetPersonId) {
    treeData.value = null
    return
  }
  
  treeLoading.value = true
  selectedTreePerson.value = targetPersonId
  
  try {
    const res = await personApi.getFamilyTree(targetPersonId)
    treeData.value = res
    await nextTick()
    renderTree()
  } catch (error) {
    console.error(error)
    ElMessage.error('加载家谱树失败')
  } finally {
    treeLoading.value = false
  }
}

const onTreePersonChange = async (personId: number) => {
  await loadFamilyTree(personId)
}

// 添加系统用户为家族成员
const addMemberDialog = ref(false)
const usersList = ref<User[]>([])
const selectedUserId = ref<number | null>(null)
const selectedRole = ref('member')
const addMemberLoading = ref(false)

const fetchUsers = async () => {
  try {
    const res = await adminApi.getUsers({ limit: 1000 })
    // 过滤掉已经是家族成员的用户
    const memberUserIds = new Set(familyMembers.value.map(m => m.user_id))
    usersList.value = res.items.filter(u => !memberUserIds.has(u.id) && u.id !== userStore.user?.id)
  } catch (error) {
    console.error(error)
    ElMessage.error('获取用户列表失败')
  }
}

const handleAddMember = async () => {
  if (!selectedUserId.value) {
    ElMessage.warning('请选择要添加的用户')
    return
  }
  
  addMemberLoading.value = true
  try {
    await familyApi.addFamilyMember(familyId, {
      user_id: selectedUserId.value,
      role: selectedRole.value
    })
    ElMessage.success('添加成员成功')
    addMemberDialog.value = false
    selectedUserId.value = null
    selectedRole.value = 'member'
    await fetchFamilyMembers()
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '添加成员失败')
  } finally {
    addMemberLoading.value = false
  }
}

const handleRemoveMember = async (member: FamilyMemberInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要将 ${member.username} 从家族中移除吗？`,
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await familyApi.removeFamilyMember(familyId, member.user_id)
    ElMessage.success('移除成员成功')
    await fetchFamilyMembers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('移除失败')
    }
  }
}

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

const canManageRoles = computed(() => {
  if (userStore.isSuperuser) return true
  const currentMember = familyMembers.value.find(m => m.user_id === userStore.user?.id)
  return currentMember?.role === 'admin'
})

const fetchFamily = async () => {
  try {
    family.value = await familyApi.getFamily(familyId)
  } catch (error) {
    console.error(error)
    ElMessage.error('获取家族信息失败')
  }
}

const fetchPersons = async () => {
  loading.value = true
  try {
    const res = await personApi.getFamilyPersons(familyId)
    persons.value = res.items
    // 如果在tree选项卡且还没有加载家谱树，自动加载
    if (activeTab.value === 'tree' && !treeData.value && persons.value.length > 0) {
      await loadFamilyTree()
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchFamilyMembers = async () => {
  membersLoading.value = true
  try {
    familyMembers.value = await familyApi.getFamilyMembers(familyId)
  } catch (error) {
    console.error(error)
  } finally {
    membersLoading.value = false
  }
}

const handleAddPerson = async () => {
  if (!newPerson.value.name) {
    ElMessage.warning('请输入成员姓名')
    return
  }
  
  try {
    await personApi.createPerson(newPerson.value)
    ElMessage.success('添加成员成功')
    addPersonDialog.value = false
    fetchPersons()
    newPerson.value = {
      family_id: familyId,
      name: '',
      gender: undefined,
      birth_date: undefined,
      biography: ''
    }
  } catch (error) {
    console.error(error)
  }
}

const deletePerson = async (person: Person) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除成员"${person.name}"吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await personApi.deletePerson(person.id)
    ElMessage.success('删除成员成功')
    fetchPersons()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('删除失败')
    }
  }
}

const viewPersonTree = (personId: number) => {
  if (!personId || isNaN(personId)) {
    ElMessage.warning('无效的成员ID')
    return
  }
  router.push(`/persons/${personId}`)
}

const handleRoleChange = async (member: FamilyMemberInfo, newRole: string) => {
  if (!canManageRoles.value) {
    ElMessage.error('您没有权限修改成员角色')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要将 ${member.username} 的角色修改为 "${roleTypeMap[newRole]}" 吗？`,
      '确认修改',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await familyApi.updateMemberRole(familyId, member.user_id, newRole)
    ElMessage.success('角色修改成功')
    await fetchFamilyMembers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('修改失败')
    }
  }
}

onMounted(() => {
  fetchFamily()
  fetchPersons()
  fetchFamilyMembers()
})

// 监听选项卡变化，切换到家谱树时自动加载
watch(activeTab, (newTab) => {
  if (newTab === 'tree' && !treeData.value && persons.value.length > 0) {
    loadFamilyTree()
  }
})
</script>

<template>
  <div v-if="family" class="family-detail">
    <el-page-header @back="$router.push('/families')">
      <template #content>
        <span class="family-title">家族详情</span>
      </template>
    </el-page-header>
    
    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <!-- 家族信息 -->
      <el-tab-pane label="家族信息" name="info">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="family-title">
                {{ family.name }}
                <el-tag v-if="family.surname" size="small" style="margin-left: 10px">
                  {{ family.surname }}氏
                </el-tag>
              </span>
              <el-button type="primary" @click="$router.push(`/families/${familyId}/edit`)">
                编辑信息
              </el-button>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="家族简介" :span="2">
              {{ family.description || '暂无简介' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="家族史" :span="2">
              {{ family.history || '暂无记载' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="家训" :span="2">
              {{ family.family_motto || '暂无家训' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="字辈">
              {{ family.generation_names?.join('、') || '未设置' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="公开状态">
              {{ family.is_public ? '公开' : '私密' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="成员数量">
              {{ family.person_count }} 人
            </el-descriptions-item>
            
            <el-descriptions-item label="创建时间">
              {{ new Date(family.created_at).toLocaleString() }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-tab-pane>
      
      <!-- 成员列表 -->
      <el-tab-pane label="成员列表" name="members">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>成员列表（{{ persons.length }} 人）</span>
              <el-button type="primary" @click="addPersonDialog = true">
                <el-icon><Plus /></el-icon> 添加成员
              </el-button>
            </div>
          </template>
          
          <el-empty v-if="persons.length === 0" description="暂无成员" />
          
          <el-table v-else :data="persons" v-loading="loading">
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="gender" label="性别" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.gender === 'male'" type="primary">男</el-tag>
                <el-tag v-else-if="row.gender === 'female'" type="danger">女</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="birth_date" label="出生日期" width="120">
              <template #default="{ row }">
                {{ row.birth_date || '-' }}
              </template>
            </el-table-column>
            
            <el-table-column prop="generation_number" label="世代" width="80">
              <template #default="{ row }">
                {{ row.generation_number || '-' }}
              </template>
            </el-table-column>
            
            <el-table-column prop="occupation" label="职业" />
            
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" link @click="viewPersonTree(row.id)">
                  查看详情
                </el-button>
                <el-button type="danger" link @click="deletePerson(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <!-- 家谱树 -->
      <el-tab-pane label="家谱树" name="tree">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>家谱树可视化</span>
              <div class="header-actions">
                <el-select
                  v-model="selectedTreePerson"
                  placeholder="选择起始成员"
                  style="width: 180px; margin-right: 10px"
                  @change="onTreePersonChange"
                >
                  <el-option
                    v-for="person in persons"
                    :key="person.id"
                    :label="person.name"
                    :value="person.id"
                  />
                </el-select>
                <el-button type="primary" @click="$router.push('/tree')">
                  查看完整家谱树
                </el-button>
              </div>
            </div>
          </template>
          
          <div v-if="persons.length === 0" class="tree-empty">
            <el-empty description="暂无成员数据，请先添加成员" />
          </div>
          
          <div v-else v-loading="treeLoading" class="tree-container">
            <div v-if="treeData" class="tree-info">
              <el-alert
                :title="`共 ${treeData.total_members} 人，${treeData.total_generations} 代（可拖拽缩放，点击节点查看详情）`"
                type="info"
                :closable="false"
              />
            </div>
            
            <div ref="containerRef" class="tree-visualization">
              <svg ref="svgRef" class="tree-svg"></svg>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 成员管理 -->
      <el-tab-pane label="家谱权限管理" name="roles">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>家谱角色管理</span>
              <el-button 
                v-if="canManageRoles" 
                type="primary" 
                @click="addMemberDialog = true; fetchUsers()"
              >
                <el-icon><Plus /></el-icon> 添加成员
              </el-button>
            </div>
          </template>
          
          <el-alert 
            v-if="!canManageRoles" 
            type="warning" 
            :closable="false"
            style="margin-bottom: 16px"
          >
            您没有权限管理成员角色，需要家族管理员或超级管理员权限
          </el-alert>
          
          <el-table :data="familyMembers" v-loading="membersLoading">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="email" label="邮箱" width="200">
              <template #default="{ row }">
                {{ row.email || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="role" label="角色" width="180">
              <template #default="{ row }">
                <el-select
                  v-if="canManageRoles && row.user_id !== userStore.user?.id"
                  :model-value="row.role"
                  @change="(val: string) => handleRoleChange(row, val)"
                  size="small"
                >
                  <el-option
                    v-for="opt in roleOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
                <span v-else>
                  <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'family_admin' ? 'warning' : 'info'">
                    {{ roleTypeMap[row.role] || row.role }}
                  </el-tag>
                  <span v-if="row.user_id === userStore.user?.id" style="margin-left: 8px; color: #909399; font-size: 12px;">
                    (当前用户)
                  </span>
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="is_superuser" label="超级管理员" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.is_superuser" type="warning" size="small">是</el-tag>
                <span v-else style="color: #909399;">否</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="加入时间" width="180">
              <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleString('zh-CN') }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" v-if="canManageRoles">
              <template #default="{ row }">
                <el-button
                  v-if="row.user_id !== userStore.user?.id"
                  type="danger"
                  link
                  size="small"
                  @click="handleRemoveMember(row)"
                >
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 添加家谱成员对话框 -->
    <el-dialog v-model="addPersonDialog" title="添加成员" width="500px">
      <el-form :model="newPerson" label-position="top">
        <el-form-item label="姓名" required>
          <el-input v-model="newPerson.name" placeholder="请输入姓名" />
        </el-form-item>
        
        <el-form-item label="性别">
          <el-radio-group v-model="newPerson.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="出生日期">
          <el-date-picker
            v-model="newPerson.birth_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="生平简介">
          <el-input
            v-model="newPerson.biography"
            type="textarea"
            :rows="3"
            placeholder="请输入生平简介"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="addPersonDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddPerson">添加</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加系统用户为家族成员对话框 -->
    <el-dialog v-model="addMemberDialog" title="添加家族成员" width="500px">
      <el-form label-position="top">
        <el-form-item label="选择用户" required>
          <el-select
            v-model="selectedUserId"
            placeholder="搜索并选择用户"
            filterable
            remote
            :remote-method="(query: string) => {
              if (query) {
                adminApi.getUsers({ search: query, limit: 20 }).then(res => {
                  const memberUserIds = new Set(familyMembers.map(m => m.user_id))
                  usersList = res.items.filter(u => !memberUserIds.has(u.id) && u.id !== userStore.user?.id)
                })
              }
            }"
            style="width: 100%"
          >
            <el-option
              v-for="user in usersList"
              :key="user.id"
              :label="user.username + (user.email ? ' (' + user.email + ')' : '')"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="角色" required>
          <el-select v-model="selectedRole" style="width: 100%">
            <el-option
              v-for="opt in roleOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="addMemberDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddMember" :loading="addMemberLoading">添加</el-button>
      </template>
    </el-dialog>
  </div>
  
  <el-empty v-else description="加载中..." />
</template>

<style scoped>
.family-detail {
  padding: 20px 0;
}

.family-title {
  font-size: 20px;
  font-weight: bold;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.tree-hint {
  text-align: center;
  padding: 40px;
}

.tree-hint p {
  margin-bottom: 20px;
  color: #909399;
}

.tree-empty {
  padding: 60px 0;
}

.tree-container {
  min-height: 500px;
}

.tree-info {
  margin-bottom: 20px;
}

.tree-visualization {
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
}

.tree-svg {
  display: block;
  width: 100%;
  height: 500px;
}

:deep(.node rect) {
  transition: all 0.2s ease;
}

:deep(.node:hover rect) {
  filter: brightness(0.95);
  transform: scale(1.02);
}

:deep(.node text) {
  user-select: none;
  pointer-events: none;
}
</style>
