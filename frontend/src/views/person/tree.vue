<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { familyApi } from '@/api/family'
import { personApi } from '@/api/person'
import type { Family, Person, FamilyTree, TreeNode } from '@/types'
import { ElMessage } from 'element-plus'
import { Share } from '@element-plus/icons-vue'
import * as d3 from 'd3'

const router = useRouter()

const families = ref<Family[]>([])
const selectedFamily = ref<number | null>(null)
const persons = ref<Person[]>([])
const selectedPerson = ref<number | null>(null)
const treeData = ref<FamilyTree | null>(null)
const loading = ref(false)

const svgRef = ref<SVGSVGElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)

const fetchFamilies = async () => {
  try {
    const res = await familyApi.getFamilies()
    families.value = res.items
    
    // 如果有家族，自动选择第一个并加载其成员
    if (families.value.length > 0) {
      selectedFamily.value = families.value[0].id
      await onFamilyChange()
    }
  } catch (error) {
    console.error(error)
  }
}

const onFamilyChange = async () => {
  if (!selectedFamily.value) {
    persons.value = []
    selectedPerson.value = null
    treeData.value = null
    return
  }
  
  try {
    const res = await personApi.getFamilyPersons(selectedFamily.value)
    persons.value = res.items
    
    // 如果有成员，自动选择第一个并加载家谱树
    if (persons.value.length > 0) {
      selectedPerson.value = persons.value[0].id
      await onPersonChange()
    }
  } catch (error) {
    console.error(error)
  }
}

const onPersonChange = async () => {
  if (!selectedPerson.value) {
    treeData.value = null
    return
  }
  
  loading.value = true
  try {
    const res = await personApi.getFamilyTree(selectedPerson.value)
    treeData.value = res
    ElMessage.success('家谱树加载成功')
    await nextTick()
    renderTree()
  } catch (error) {
    console.error(error)
    ElMessage.error('加载家谱树失败')
  } finally {
    loading.value = false
  }
}

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
  x0?: number
  y0?: number
  _children?: D3TreeNode[]
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
  const containerHeight = 600
  
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

watch(treeData, () => {
  nextTick(() => {
    renderTree()
  })
})

onMounted(() => {
  fetchFamilies()
})
</script>

<template>
  <div class="tree-view">
    <div class="page-header">
      <h2>家谱树</h2>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>家谱树可视化</span>
          <div class="header-actions">
            <el-select
              v-model="selectedFamily"
              placeholder="选择家族"
              style="width: 180px; margin-right: 10px"
              @change="onFamilyChange"
            >
              <el-option
                v-for="family in families"
                :key="family.id"
                :label="family.name"
                :value="family.id"
              />
            </el-select>
            
            <el-select
              v-model="selectedPerson"
              placeholder="选择起始成员"
              style="width: 180px"
              :disabled="!selectedFamily"
              @change="onPersonChange"
            >
              <el-option
                v-for="person in persons"
                :key="person.id"
                :label="person.name"
                :value="person.id"
              />
            </el-select>
          </div>
        </div>
      </template>
      
      <div v-if="!treeData" class="empty-state">
        <el-empty description="暂无家谱数据，请先创建家族和成员">
          <template #image>
            <el-icon :size="60" color="#909399"><Share /></el-icon>
          </template>
        </el-empty>
      </div>
      
      <div v-else v-loading="loading" class="tree-container">
        <div class="tree-info">
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
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
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

.empty-state {
  padding: 60px 0;
}

.tree-container {
  min-height: 600px;
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
  height: 600px;
}

.node rect {
  transition: all 0.2s ease;
}

.node:hover rect {
  filter: brightness(0.95);
  transform: scale(1.02);
}

.node text {
  user-select: none;
  pointer-events: none;
}
</style>