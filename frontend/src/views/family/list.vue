<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { familyApi } from '@/api/family'
import type { Family } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const families = ref<Family[]>([])
const loading = ref(false)
const searchQuery = ref('')
const dialogVisible = ref(false)

const form = reactive<Partial<Family>>({
  name: '',
  surname: '',
  description: '',
  is_public: false
})

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

const handleCreate = async () => {
  if (!form.name) {
    ElMessage.warning('请输入家族名称')
    return
  }
  
  try {
    await familyApi.createFamily(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchFamilies()
    // 重置表单
    form.name = ''
    form.surname = ''
    form.description = ''
    form.is_public = false
  } catch (error) {
    console.error(error)
  }
}

const handleDelete = async (family: Family) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除家族 "${family.name}" 吗？此操作不可恢复！`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await familyApi.deleteFamily(family.id)
    ElMessage.success('删除成功')
    fetchFamilies()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchFamilies()
})
</script>

<template>
  <div class="family-list">
    <div class="page-header">
      <h2>家族管理</h2>
      <el-button type="primary" @click="dialogVisible = true">
        <el-icon><Plus /></el-icon> 创建家族
      </el-button>
    </div>
    
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索家族名称或姓氏"
        clearable
        style="width: 300px"
        @keyup.enter="fetchFamilies"
      >
        <template #append>
          <el-button @click="fetchFamilies">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
    </div>
    
    <el-empty v-if="families.length === 0 && !loading" description="暂无家族" />
    
    <el-row v-else :gutter="20">
      <el-col 
        v-for="family in families" 
        :key="family.id" 
        :xs="24" 
        :sm="12" 
        :md="8" 
        :lg="6"
        style="margin-bottom: 20px"
      >
        <el-card class="family-card" shadow="hover">
          <template #header>
            <div class="family-header">
              <span class="family-name" @click="$router.push(`/families/${family.id}`)">
                {{ family.name }}
              </span>
              <div class="family-actions">
                <el-tag v-if="family.surname" size="small" effect="plain">
                  {{ family.surname }}氏
                </el-tag>
                <el-tag v-if="!family.is_public" size="small" type="warning">私密</el-tag>
              </div>
            </div>
          </template>
          
          <p v-if="family.description" class="family-desc">
            {{ family.description.slice(0, 150) }}{{ family.description.length > 150 ? '...' : '' }}
          </p>
          <p v-else class="family-desc text-gray">暂无简介</p>
          
          <div class="family-footer">
            <div class="family-stats">
              <span><el-icon><User /></el-icon> {{ family.person_count || 0 }} 成员</span>
            </div>
            <div class="family-actions">
              <el-button 
                type="primary" 
                link
                @click="$router.push(`/families/${family.id}`)"
              >
                查看详情
              </el-button>
              <el-button 
                type="danger" 
                link
                @click="handleDelete(family)"
              >
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 创建家族对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="创建家族"
      width="500px"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="家族名称" required>
          <el-input v-model="form.name" placeholder="请输入家族名称" />
        </el-form-item>
        
        <el-form-item label="家族姓氏">
          <el-input v-model="form.surname" placeholder="请输入家族姓氏" />
        </el-form-item>
        
        <el-form-item label="家族简介">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入家族简介"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="form.is_public">公开家族（所有人可见）</el-checkbox>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
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

.search-bar {
  margin-bottom: 20px;
}

.family-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.family-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.family-name {
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
  color: #303133;
}

.family-name:hover {
  color: #409EFF;
}

.family-actions {
  display: flex;
  gap: 8px;
}

.family-desc {
  color: #606266;
  font-size: 14px;
  margin: 10px 0;
  min-height: 60px;
  line-height: 1.6;
}

.text-gray {
  color: #909399;
}

.family-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.family-stats {
  color: #909399;
  font-size: 13px;
}

.family-stats .el-icon {
  margin-right: 4px;
}
</style>
