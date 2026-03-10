<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { personApi } from '@/api/person'
import type { Person, FamilyTree } from '@/types'
import { ElMessage } from 'element-plus'

const persons = ref<Person[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedFamily = ref<number | null>(null)

const fetchPersons = async () => {
  if (!selectedFamily.value) return
  
  loading.value = true
  try {
    const res = await personApi.getFamilyPersons(selectedFamily.value, {
      search: searchQuery.value || undefined
    })
    persons.value = res.items
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const viewPersonDetail = (id: number) => {
  // 跳转到成员详情
  window.open(`#/persons/${id}`, '_blank')
}

onMounted(() => {
  // 这里应该从路由参数或全局状态获取家族ID
  // 暂时显示提示
  ElMessage.info('请先选择一个家族')
})
</script>

<template>
  <div class="person-list">
    <div class="page-header">
      <h2>成员管理</h2>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>请先选择要查看的家族</span>
          <el-button type="primary" @click="$router.push('/families')">
            选择家族
          </el-button>
        </div>
      </template>
      
      <p class="hint-text">
        成员管理需要在家族详情页面中进行。请先选择一个家族，然后在该家族的"成员列表"标签页中管理成员。
      </p>
      
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/families')">
          <el-icon><Pointer /></el-icon> 前往家族列表
        </el-button>
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

.hint-text {
  color: #606266;
  line-height: 1.8;
  font-size: 14px;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}
</style>
