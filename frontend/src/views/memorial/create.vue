<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { memorialApi, type OfferingItem } from '@/api/memorial'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const familyId = parseInt(route.query.family_id as string)

const eligiblePersons = ref<{id: number, name: string, death_date: string}[]>([])
const selectedPerson = ref<number | null>(null)
const loading = ref(false)
const submitting = ref(false)

// 贡品选择
const availableOfferings = <OfferingItem[]>[
  { name: '鲜花', icon: '🌸' },
  { name: '水果', icon: '🍎' },
  { name: '糕点', icon: '🥮' },
  { name: '酒水', icon: '🍶' },
  { name: '香烛', icon: '🕯️' },
  { name: '纸钱', icon: '💴' },
  { name: '菜肴', icon: '🍲' },
  { name: '茶点', icon: '🍵' }
]

const selectedOfferings = ref<OfferingItem[]>([
  { name: '鲜花', icon: '🌸' },
  { name: '水果', icon: '🍎' },
  { name: '糕点', icon: '🥮' }
])

const fetchEligiblePersons = async () => {
  if (!familyId) return
  
  loading.value = true
  try {
    const res = await memorialApi.getEligiblePersons(familyId)
    eligiblePersons.value = res
  } catch (error) {
    console.error(error)
    ElMessage.error('获取可布置灵堂的逝者列表失败')
  } finally {
    loading.value = false
  }
}

const toggleOffering = (offering: OfferingItem) => {
  const index = selectedOfferings.value.findIndex(o => o.name === offering.name)
  if (index > -1) {
    selectedOfferings.value.splice(index, 1)
  } else {
    selectedOfferings.value.push(offering)
  }
}

const handleSubmit = async () => {
  if (!selectedPerson.value) {
    ElMessage.warning('请选择逝者')
    return
  }
  
  if (selectedOfferings.value.length === 0) {
    ElMessage.warning('请至少选择一种贡品')
    return
  }
  
  submitting.value = true
  try {
    await memorialApi.createMemorialHall({
      person_id: selectedPerson.value,
      offerings: selectedOfferings.value
    })
    
    ElMessage.success('灵堂布置成功')
    router.push('/memorial')
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '布置失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!familyId) {
    ElMessage.warning('请先选择家族')
    router.push('/memorial')
    return
  }
  fetchEligiblePersons()
})
</script>

<template>
  <div class="create-memorial">
    <el-page-header @back="$router.push('/memorial')" title="布置灵堂" />
    
    <el-card class="form-card">
      <template #header>
        <span>布置灵堂</span>
      </template>
      
      <el-form v-loading="loading" label-position="top">
        <!-- 选择逝者 -->
        <el-form-item label="选择逝者" required>
          <el-select 
            v-model="selectedPerson" 
            placeholder="请选择要布置灵堂的逝者"
            style="width: 100%"
          >
            <el-option
              v-for="person in eligiblePersons"
              :key="person.id"
              :label="person.name + (person.death_date ? ' (逝世：' + person.death_date + ')' : '')"
              :value="person.id"
            />
          </el-select>
          
          <el-alert 
            v-if="eligiblePersons.length === 0 && !loading" 
            type="warning" 
            :closable="false"
            style="margin-top: 10px"
          >
            该家族暂无可布置灵堂的逝者（需要有逝世日期且尚未布置灵堂）
          </el-alert>
        </el-form-item>
        
        <!-- 选择贡品 -->
        <el-form-item label="选择贡品" required>
          <p class="form-hint">点击选择要供奉的贡品</p>
          
          <div class="offerings-grid">
            <div
              v-for="offering in availableOfferings"
              :key="offering.name"
              class="offering-card"
              :class="{ 'selected': selectedOfferings.some(o => o.name === offering.name) }"
              @click="toggleOffering(offering)"
            >
              <span class="offering-icon">{{ offering.icon }}</span>
              <span class="offering-name">{{ offering.name }}</span>
              <el-icon v-if="selectedOfferings.some(o => o.name === offering.name)" class="check-icon"><Check /></el-icon>
            </div>
          </div>
          
          <div class="selected-preview">
            <span class="preview-label">已选择：</span>
            <span v-if="selectedOfferings.length === 0" class="preview-empty">未选择贡品</span>
            <span v-else class="preview-items">
              <span 
                v-for="(item, index) in selectedOfferings" 
                :key="item.name"
                class="preview-item"
              >
                {{ item.icon }} {{ item.name }}{{ index < selectedOfferings.length - 1 ? '、' : '' }}
              </span>
            </span>
          </div>
        </el-form-item>
        
        <!-- 预览 -->
        <el-form-item label="灵堂预览">
          <div class="preview-hall">
            <div class="preview-altar">
              <div class="preview-tablet">
                <span class="preview-title">故显考</span>
                <span class="preview-name">{{ eligiblePersons.find(p => p.id === selectedPerson)?.name || '逝者姓名' }}</span>
              </div>
              
              <div class="preview-offerings">
                <span 
                  v-for="item in selectedOfferings" 
                  :key="item.name"
                  class="preview-offering"
                >
                  {{ item.icon }}
                </span>
              </div>
            </div>
          </div>
        </el-form-item>
        
        <!-- 提交按钮 -->
        <el-form-item>
          <el-button 
            type="primary" 
            size="large"
            :loading="submitting"
            :disabled="!selectedPerson || selectedOfferings.length === 0"
            @click="handleSubmit"
            style="width: 100%"
          >
            布置灵堂
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.create-memorial {
  padding: 20px 0;
}

.form-card {
  max-width: 600px;
  margin: 20px auto;
}

.form-hint {
  margin: 0 0 15px 0;
  font-size: 13px;
  color: #909399;
}

.offerings-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.offering-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.offering-card:hover {
  border-color: #409eff;
}

.offering-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.offering-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.offering-name {
  font-size: 13px;
  color: #606266;
}

.check-icon {
  position: absolute;
  top: 5px;
  right: 5px;
  color: #409eff;
  font-size: 16px;
}

.selected-preview {
  margin-top: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.preview-label {
  font-size: 13px;
  color: #909399;
  margin-right: 10px;
}

.preview-empty {
  font-size: 13px;
  color: #c0c4cc;
}

.preview-items {
  font-size: 13px;
  color: #606266;
}

.preview-item {
  margin-right: 5px;
}

.preview-hall {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 30px;
  border-radius: 8px;
}

.preview-altar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.preview-tablet {
  background: linear-gradient(145deg, #8b4513, #a0522d);
  padding: 6px;
  border-radius: 6px;
  text-align: center;
  min-width: 150px;
}

.preview-tablet::before {
  content: '';
  display: block;
  background: #f5f5dc;
  padding: 20px 30px;
  border-radius: 3px;
}

.preview-title {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.preview-name {
  display: block;
  font-size: 20px;
  color: #333;
  font-weight: bold;
}

.preview-offerings {
  display: flex;
  gap: 10px;
}

.preview-offering {
  font-size: 24px;
}
</style>
