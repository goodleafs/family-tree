<template>
  <div class="tree-page">
    <div class="page-header">
      <h1 class="page-title">族谱树</h1>
      <div class="header-actions">
        <select v-model="selectedFamily" @change="onFamilyChange" class="family-select">
          <option :value="null">选择家族</option>
          <option v-for="f in families" :key="f.id" :value="f.id">{{ f.name }}</option>
        </select>
        <select v-model="selectedPerson" @change="onPersonChange" class="person-select" :disabled="!selectedFamily">
          <option :value="null">选择起始成员</option>
          <option v-for="p in persons" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
      </div>
    </div>
    
    <!-- 族谱展示区 -->
    <div class="tree-container" ref="containerRef">
      <div class="scroll-frame" v-if="treeData">
        <div class="scroll-inner">
          <svg ref="svgRef" class="tree-svg"></svg>
        </div>
        
        <!-- 图例 -->
        <div class="tree-legend">
          <div class="legend-item male">
            <span class="legend-color"></span>
            <span>男性</span>
          </div>
          <div class="legend-item female">
            <span class="legend-color"></span>
            <span>女性</span>
          </div>
        </div>
        
        <!-- 统计信息 -->
        <div class="tree-stats">
          共 {{ treeData.total_members }} 人 · {{ treeData.total_generations }} 代
        </div>
      </div>
      
      <!-- 空状态 -->
      <div class="empty-state" v-else>
        <div class="empty-icon">🌳</div>
        <h3>选择家族和成员</h3>
        <p>请从上方选择家族和起始成员来查看族谱树</p>
      </div>
    </div>
    
    <!-- 操作提示 -->
    <div class="tree-tips" v-if="treeData">
      <span>💡 提示：可拖拽缩放，点击节点查看详情</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { familyApi } from '@/api/family'
import { personApi } from '@/api/person'
import type { Family, Person, FamilyTree, TreeNode } from '@/types'
import * as d3 from 'd3'

const router = useRouter()
const families = ref<Family[]>([])
const persons = ref<Person[]>([])
const selectedFamily = ref<number | null>(null)
const selectedPerson = ref<number | null>(null)
const treeData = ref<FamilyTree | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)
const svgRef = ref<SVGSVGElement | null>(null)

interface D3TreeNode {
  id: number
  name: string
  gender?: string
  birth_date?: string
  death_date?: string
  generation_number?: number
  children?: D3TreeNode[]
}

const transformTreeData = (node: TreeNode): D3TreeNode => {
  const result: D3TreeNode = {
    id: node.id,
    name: node.name,
    gender: node.gender,
    birth_date: node.birth_date,
    death_date: node.death_date,
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
  
  const containerWidth = containerRef.value.clientWidth - 40
  
  // 计算树的深度来动态调整高度
  const root = d3.hierarchy<D3TreeNode>(transformTreeData(treeData.value.root))
  const treeLayout = d3.tree<D3TreeNode>()
  
  // 先计算布局以获取深度信息
  treeLayout.nodeSize([150, 100])(root)
  
  const maxDepth = root.height || 0
  const containerHeight = Math.max(600, (maxDepth + 1) * 120 + 100)
  
  const margin = { top: 60, right: 60, bottom: 60, left: 60 }
  const width = Math.max(containerWidth - margin.left - margin.right, 600)
  const height = containerHeight - margin.top - margin.bottom
  
  svg.attr('width', width + margin.left + margin.right)
     .attr('height', height + margin.top + margin.bottom)
  
  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  
  // 使用垂直布局
  treeLayout.size([width, height])
  treeLayout(root)
  
  const zoom = d3.zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      g.attr('transform', event.transform)
    })
  
  svg.call(zoom)
  
  // 连接线 - 垂直方向
  g.selectAll('.link')
    .data(root.links())
    .enter()
    .append('path')
    .attr('class', 'link')
    .attr('fill', 'none')
    .attr('stroke', '#d4b896')
    .attr('stroke-width', 2)
    .attr('d', d3.linkVertical<any, any>()
      .x((d: any) => d.x)
      .y((d: any) => d.y))
  
  // 节点
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
    .attr('x', -50)
    .attr('y', -18)
    .attr('width', 100)
    .attr('height', 36)
    .attr('rx', 4)
    .attr('fill', (d: any) => {
      const gender = d.data.gender
      if (gender === 'male') return '#f0f7ff'
      if (gender === 'female') return '#fff0f5'
      return '#faf8f5'
    })
    .attr('stroke', (d: any) => {
      const gender = d.data.gender
      if (gender === 'male') return '#2c4a6e'
      if (gender === 'female') return '#c41e3a'
      return '#b5b5b5'
    })
    .attr('stroke-width', 1.5)
  
  // 节点文字
  nodes.append('text')
    .attr('dy', 5)
    .attr('text-anchor', 'middle')
    .attr('font-family', 'var(--font-title)')
    .attr('font-size', '14px')
    .attr('fill', '#1a1a1a')
    .text((d: any) => {
      const name = d.data.name
      return name.length > 6 ? name.substring(0, 6) + '...' : name
    })
  
  // 提示
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
}

const fetchFamilies = async () => {
  try {
    const res = await familyApi.getFamilies()
    families.value = res.items
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
  
  try {
    const res = await personApi.getFamilyTree(selectedPerson.value)
    treeData.value = res
    await nextTick()
    renderTree()
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchFamilies()
})
</script>

<style scoped>
.tree-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
  flex-wrap: wrap;
  gap: var(--space-4);
}

.page-title {
  font-family: var(--font-title);
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.family-select,
.person-select {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  min-width: 160px;
}

.family-select:focus,
.person-select:focus {
  outline: none;
  border-color: var(--cinnabar);
}

/* 族谱容器 */
.tree-container {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-xl);
  overflow: hidden;
  min-height: 600px;
  position: relative;
}

.scroll-frame {
  padding: var(--space-4);
  background: 
    linear-gradient(90deg, var(--paper-aged) 0%, var(--paper-cream) 3%, var(--paper-cream) 97%, var(--paper-aged) 100%);
  border-left: 6px solid var(--ink-dark);
  border-right: 6px solid var(--ink-dark);
  margin: var(--space-4);
  border-radius: var(--radius-md);
  min-height: 560px;
}

.scroll-inner {
  overflow: auto;
}

.tree-svg {
  display: block;
  min-width: 100%;
}

/* 图例 */
.tree-legend {
  position: absolute;
  top: var(--space-4);
  left: var(--space-4);
  display: flex;
  gap: var(--space-4);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: var(--radius-sm);
  border: 1.5px solid;
}

.legend-item.male .legend-color {
  background: #f0f7ff;
  border-color: #2c4a6e;
}

.legend-item.female .legend-color {
  background: #fff0f5;
  border-color: #c41e3a;
}

/* 统计 */
.tree-stats {
  position: absolute;
  bottom: var(--space-4);
  right: var(--space-4);
  padding: var(--space-2) var(--space-3);
  background: var(--cinnabar-pale);
  color: var(--cinnabar);
  font-size: var(--text-sm);
  border-radius: var(--radius-md);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  color: var(--text-tertiary);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: var(--space-4);
}

.empty-state h3 {
  font-family: var(--font-title);
  font-size: var(--text-xl);
  color: var(--text-secondary);
  margin: 0 0 var(--space-2);
}

.empty-state p {
  font-size: var(--text-sm);
  margin: 0;
}

/* 提示 */
.tree-tips {
  margin-top: var(--space-4);
  text-align: center;
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

/* 节点悬停效果 */
:deep(.node rect) {
  transition: all 0.2s ease;
}

:deep(.node:hover rect) {
  filter: brightness(0.95);
}

:deep(.node text) {
  user-select: none;
  pointer-events: none;
}

@media (max-width: 768px) {
  .scroll-frame { margin: var(--space-2); padding: var(--space-2); }
}
</style>