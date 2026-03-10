<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { familyApi } from '@/api/family'
import type { Family } from '@/types'

const families = ref<Family[]>([])
const loading = ref(false)
const searchQuery = ref('')

const fetchFamilies = async () => {
  loading.value = true
  try {
    const res = await familyApi.getFamilies({ search: searchQuery.value || undefined })
    families.value = res.items
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchFamilies()
})
</script>

<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <span>欢迎使用寻根家谱管理系统</span>
            </div>
          </template>
          <p>这是一个基于 FastAPI + Vue3 的多家族寻根家谱管理系统。您可以：</p>
          <ul>
            <li>创建和管理多个家族</li>
            <li>添加家族成员和亲属关系</li>
            <li>可视化展示家谱树</li>
            <li>导出 PDF 家谱图</li>
            <li>批量导入 Excel 数据</li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的家族</span>
              <el-button type="primary" @click="$router.push('/families')">查看全部</el-button>
            </div>
          </template>
          
          <el-empty v-if="families.length === 0" description="暂无家族，快去创建吧" />
          
          <el-row v-else :gutter="20">
            <el-col 
              v-for="family in families.slice(0, 6)" 
              :key="family.id" 
              :xs="24" 
              :sm="12" 
              :md="8" 
              :lg="6"
              style="margin-bottom: 20px"
            >
              <el-card 
                class="family-card" 
                shadow="hover"
                @click="$router.push(`/families/${family.id}`)"
              >
                <template #header>
                  <div class="family-header">
                    <span class="family-name">{{ family.name }}</span>
                    <el-tag v-if="family.surname" size="small">{{ family.surname }}氏</el-tag>
                  </div>
                </template>
                
                <p v-if="family.description" class="family-desc">
                  {{ family.description.slice(0, 100) }}{{ family.description.length > 100 ? '...' : '' }}
                </p>
                <p v-else class="family-desc text-gray">暂无简介</p>
                
                <div class="family-stats">
                  <span><el-icon><User /></el-icon> {{ family.person_count || 0 }} 成员</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-card ul {
  padding-left: 20px;
  color: #606266;
  line-height: 2;
}

.family-card {
  cursor: pointer;
  transition: all 0.3s;
}

.family-card:hover {
  transform: translateY(-5px);
}

.family-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.family-name {
  font-weight: bold;
  font-size: 16px;
}

.family-desc {
  color: #606266;
  font-size: 14px;
  margin: 10px 0;
  min-height: 40px;
}

.text-gray {
  color: #909399;
}

.family-stats {
  color: #909399;
  font-size: 13px;
  margin-top: 10px;
}

.family-stats .el-icon {
  margin-right: 4px;
}
</style>
