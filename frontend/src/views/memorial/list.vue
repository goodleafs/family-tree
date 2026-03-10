<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { memorialApi, type MemorialHallListItem } from '@/api/memorial'
import { familyApi } from '@/api/family'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const halls = ref<MemorialHallListItem[]>([])
const loading = ref(false)
const families = ref<{id: number, name: string}[]>([])
const selectedFamily = ref<number | null>(null)

const fetchFamilies = async () => {
  try {
    const res = await familyApi.getFamilies()
    families.value = res.items
    if (families.value.length > 0 && !selectedFamily.value) {
      selectedFamily.value = families.value[0].id
      fetchHalls()
    }
  } catch (error) {
    console.error(error)
  }
}

const fetchHalls = async () => {
  if (!selectedFamily.value) return
  
  loading.value = true
  try {
    const res = await memorialApi.getMemorialHalls({ 
      family_id: selectedFamily.value 
    })
    halls.value = res.items
  } catch (error) {
    console.error(error)
    ElMessage.error('获取灵堂列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  if (!selectedFamily.value) {
    ElMessage.warning('请先选择家族')
    return
  }
  router.push(`/memorial/create?family_id=${selectedFamily.value}`)
}

const handleDelete = async (hall: MemorialHallListItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${hall.person.name} 的灵堂吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await memorialApi.deleteMemorialHall(hall.id)
    ElMessage.success('删除成功')
    fetchHalls()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('删除失败')
    }
  }
}

const viewHall = (hallId: number) => {
  router.push(`/memorial/${hallId}`)
}

onMounted(() => {
  fetchFamilies()
})
</script>

<template>
  <div class="memorial-list">
    <div class="page-header">
      <h2>祭拜管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon> 布置灵堂
      </el-button>
    </div>
    
    <div class="filter-bar">
      <el-select v-model="selectedFamily" placeholder="选择家族" @change="fetchHalls" style="width: 200px">
        <el-option
          v-for="family in families"
          :key="family.id"
          :label="family.name"
          :value="family.id"
        />
      </el-select>
    </div>
    
    <el-empty v-if="halls.length === 0 && !loading" description="暂无灵堂，请先布置" />
    
    <el-row v-else :gutter="20">
      <el-col 
        v-for="hall in halls" 
        :key="hall.id" 
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6"
        style="margin-bottom: 20px"
      >
        <el-card class="hall-card" :class="{ 'inactive': !hall.is_active }" shadow="hover">
          <div class="hall-header" @click="viewHall(hall.id)">
            <el-avatar 
              :size="80" 
              :src="hall.person.photo_url || '/default-avatar.png'"
              class="person-avatar"
            />
            <div class="person-info">
              <h3 class="person-name">{{ hall.person.name }}</h3>
              <p class="person-date" v-if="hall.person.death_date">
                逝世：{{ hall.person.death_date }}
              </p>
              <el-tag v-if="!hall.is_active" type="info" size="small">已停用</el-tag>
            </div>
          </div>
          
          <div class="hall-stats">
            <div class="stat-item">
              <span class="stat-icon">🙏</span>
              <span class="stat-value">{{ hall.worship_count }}</span>
              <span class="stat-label">祭拜人次</span>
            </div>
          </div>
          
          <div class="hall-footer">
            <span class="creator">布置人：{{ hall.creator.username }}</span>
            <el-button 
              v-if="hall.is_active"
              type="danger" 
              link 
              size="small"
              @click.stop="handleDelete(hall)"
            >
              删除
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.memorial-list {
  padding: 20px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.filter-bar {
  margin-bottom: 20px;
}

.hall-card {
  cursor: pointer;
  transition: all 0.3s;
}

.hall-card:hover {
  transform: translateY(-5px);
}

.hall-card.inactive {
  opacity: 0.6;
}

.hall-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
}

.person-avatar {
  margin-bottom: 15px;
  border: 3px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.person-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.person-date {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #909399;
}

.hall-stats {
  padding: 15px 0;
  text-align: center;
  border-bottom: 1px solid #ebeef5;
}

.stat-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
}

.stat-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.hall-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
}

.creator {
  font-size: 12px;
  color: #909399;
}
</style>
