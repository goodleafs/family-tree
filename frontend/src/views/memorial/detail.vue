<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { memorialApi, type MemorialHall, type WorshipRecord } from '@/api/memorial'
import { ElMessage } from 'element-plus'
import { toLunarYearWithDate } from '@/utils/lunar'

const route = useRoute()
const router = useRouter()
const hallId = parseInt(route.params.id as string)

// 检查 hallId 是否有效
if (isNaN(hallId)) {
  console.error('Invalid hallId:', route.params.id)
  ElMessage.error('无效灵堂ID')
  router.push('/memorial')
}

const hall = ref<MemorialHall | null>(null)
const records = ref<WorshipRecord[]>([])
const loading = ref(false)
const worshipLoading = ref(false)
const message = ref('')

// 贡品选项
const offeringOptions = [
  { name: '鲜花', icon: '🌸' },
  { name: '水果', icon: '🍎' },
  { name: '糕点', icon: '🥮' },
  { name: '酒水', icon: '🍶' },
  { name: '香烛', icon: '🕯️' },
  { name: '纸钱', icon: '💴' }
]

const fetchHall = async () => {
  loading.value = true
  try {
    hall.value = await memorialApi.getMemorialHall(hallId)
    fetchRecords()
  } catch (error) {
    console.error(error)
    ElMessage.error('获取灵堂信息失败')
  } finally {
    loading.value = false
  }
}

const fetchRecords = async () => {
  try {
    const res = await memorialApi.getWorshipRecords(hallId, { limit: 10 })
    records.value = res
  } catch (error) {
    console.error(error)
  }
}

const handleWorship = async (type: 'kowtow' | 'incense' | 'offering') => {
  console.log('handleWorship called with type:', type)
  if (!hall.value?.is_active) {
    ElMessage.warning('该灵堂已停用')
    return
  }
  
  worshipLoading.value = true
  try {
    console.log('Calling memorialApi.worship with hallId:', hallId, 'type:', type)
    const res = await memorialApi.worship(hallId, {
      worship_type: type,
      message: type === 'offering' ? message.value : undefined
    })
    console.log('memorialApi.worship response:', res)
    
    if (hall.value) {
      hall.value.worship_count = res.worship_count
      if (type === 'incense') {
        hall.value.incense_count += 1
      }
    }
    
    ElMessage.success('祭拜成功')
    message.value = ''
    fetchRecords()
  } catch (error: any) {
    console.error('Worship error:', error)
    ElMessage.error(error?.response?.data?.detail || '祭拜失败')
  } finally {
    worshipLoading.value = false
  }
}

const getWorshipTypeText = (type: string) => {
  const map: Record<string, string> = {
    kowtow: '叩拜',
    incense: '上香',
    offering: '献贡'
  }
  return map[type] || type
}

const getWorshipTypeTag = (type: string) => {
  const map: Record<string, string> = {
    kowtow: 'success',
    incense: 'warning',
    offering: 'info'
  }
  return map[type] || 'info'
}

onMounted(() => {
  fetchHall()
})
</script>

<template>
  <div v-if="hall" class="memorial-hall">
    <el-page-header @back="$router.push('/memorial')">
      <template #content>
        <span class="page-title">{{ hall.person.name }}的灵堂</span>
      </template>
    </el-page-header>
    
    <div class="hall-content">
      <!-- 灵堂主体 -->
      <el-card class="altar-card">
        <div class="altar">
          <!-- 牌位 -->
          <div class="memorial-tablet">
            <div class="tablet-frame">
              <div class="tablet-content">
                <p class="tablet-title">故显考</p>
                <h2 class="tablet-name">{{ hall.person.name }}</h2>
                <p class="tablet-dates" v-if="hall.person.birth_date || hall.person.death_date">
                  {{ hall.person.birth_date || '?' }} ~ {{ hall.person.death_date || '?' }}
                </p>
                <p class="tablet-lunar-dates" v-if="hall.person.birth_date || hall.person.death_date">
                  农历: {{ hall.person.birth_date ? toLunarYearWithDate(hall.person.birth_date) : '?' }} ~ {{ hall.person.death_date ? toLunarYearWithDate(hall.person.death_date) : '?' }}
                </p>
                <p class="tablet-honor">英灵永存</p>
              </div>
            </div>
          </div>
          
          <!-- 贡品台 -->
          <div class="offering-table">
            <div 
              v-for="(offering, index) in hall.offerings" 
              :key="index"
              class="offering-item"
            >
              <span class="offering-icon">{{ offering.icon }}</span>
              <span class="offering-name">{{ offering.name }}</span>
            </div>
          </div>
          
          <!-- 香火 -->
          <div class="incense-burner">
            <div class="burner">
              <div class="incense-sticks">
                <div class="stick" v-for="n in Math.min(hall.incense_count, 5)" :key="n"></div>
              </div>
              <span class="incense-count">香火：{{ hall.incense_count }}</span>
            </div>
          </div>
          
          <!-- 统计 -->
          <div class="worship-stats">
            <el-tag type="info" size="large">
              <span class="stats-number">{{ hall.worship_count }}</span>
              <span class="stats-label">人祭拜</span>
            </el-tag>
          </div>
          
          <!-- 布置人 -->
          <div class="creator-info">
            <span>灵堂布置：{{ hall.creator.username }}</span>
            <el-tag v-if="!hall.is_active" type="info" size="small">已停用</el-tag>
          </div>
        </div>
      </el-card>
      
      <!-- 祭拜操作区 -->
      <el-card class="worship-actions">
        <template #header>
          <span>祭拜祈福</span>
        </template>
        
        <div class="action-buttons">
          <el-button 
            type="primary" 
            size="large"
            :loading="worshipLoading"
            :disabled="!hall.is_active"
            @click="handleWorship('kowtow')"
          >
            <span class="btn-icon">🙏</span>
            <span>叩拜</span>
          </el-button>
          
          <el-button 
            type="warning" 
            size="large"
            :loading="worshipLoading"
            :disabled="!hall.is_active"
            @click="handleWorship('incense')"
          >
            <span class="btn-icon">🕯️</span>
            <span>上香</span>
          </el-button>
        </div>
        
        <div class="offering-section">
          <p class="section-title">选择贡品</p>
          <div class="offering-options">
            <el-check-tag
              v-for="opt in offeringOptions"
              :key="opt.name"
              :checked="message.includes(opt.name)"
              @change="() => {
                if (message.includes(opt.name)) {
                  message = message.replace(opt.name, '').trim()
                } else {
                  message = message ? message + '、' + opt.name : opt.name
                }
              }"
            >
              {{ opt.icon }} {{ opt.name }}
            </el-check-tag>
          </div>
          
          <el-button 
            type="info" 
            size="large"
            :loading="worshipLoading"
            :disabled="!hall.is_active || !message"
            @click="handleWorship('offering')"
            style="margin-top: 15px; width: 100%"
          >
            <span class="btn-icon">🎁</span>
            <span>献贡</span>
          </el-button>
        </div>
      </el-card>
      
      <!-- 祭拜记录 -->
      <el-card class="records-card">
        <template #header>
          <span>祭拜记录</span>
        </template>
        
        <el-empty v-if="records.length === 0" description="暂无祭拜记录" />
        
        <el-timeline v-else>
          <el-timeline-item
            v-for="record in records"
            :key="record.id"
            :type="getWorshipTypeTag(record.worship_type)"
            :timestamp="new Date(record.created_at).toLocaleString('zh-CN')"
          >
            <el-tag :type="getWorshipTypeTag(record.worship_type)" size="small">
              {{ getWorshipTypeText(record.worship_type) }}
            </el-tag>
            <span v-if="record.username" class="record-user">
              {{ record.username }}
            </span>
            <p v-if="record.message" class="record-message">
              {{ record.message }}
            </p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
  
  <el-empty v-else-if="!loading" description="灵堂不存在" />
</template>

<style scoped>
.memorial-hall {
  padding: 20px 0;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
}

.hall-content {
  margin-top: 20px;
}

.altar-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  margin-bottom: 20px;
}

.altar {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  color: #fff;
}

/* 牌位样式 */
.memorial-tablet {
  margin-bottom: 30px;
}

.tablet-frame {
  background: linear-gradient(145deg, #8b4513, #a0522d);
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.tablet-content {
  background: #f5f5dc;
  color: #333;
  padding: 30px 50px;
  text-align: center;
  border-radius: 4px;
  min-width: 200px;
}

.tablet-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #666;
}

.tablet-name {
  margin: 0 0 15px 0;
  font-size: 32px;
  color: #333;
  letter-spacing: 8px;
}

.tablet-dates {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.tablet-lunar-dates {
  margin: 0 0 10px 0;
  font-size: 12px;
  color: #999;
}

.tablet-honor {
  margin: 0;
  font-size: 14px;
  color: #999;
}

/* 贡品台 */
.offering-table {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  justify-content: center;
}

.offering-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  min-width: 60px;
}

.offering-icon {
  font-size: 32px;
  margin-bottom: 5px;
}

.offering-name {
  font-size: 12px;
  color: #ccc;
}

/* 香火 */
.incense-burner {
  margin-bottom: 30px;
}

.burner {
  background: #2c2c2c;
  padding: 20px 40px;
  border-radius: 50%;
  text-align: center;
  border: 3px solid #8b4513;
}

.incense-sticks {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-bottom: 10px;
}

.stick {
  width: 4px;
  height: 40px;
  background: linear-gradient(to top, #8b4513, #ff6b6b);
  border-radius: 2px;
  position: relative;
}

.stick::before {
  content: '';
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 8px;
  height: 12px;
  background: #ff6b6b;
  border-radius: 50%;
  box-shadow: 0 0 10px #ff6b6b;
}

.incense-count {
  font-size: 14px;
  color: #ccc;
}

/* 统计 */
.worship-stats {
  margin-bottom: 20px;
}

.stats-number {
  font-size: 24px;
  font-weight: bold;
  margin-right: 5px;
}

.stats-label {
  font-size: 14px;
}

/* 布置人 */
.creator-info {
  font-size: 14px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 祭拜操作区 */
.worship-actions {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 20px;
}

.action-buttons .el-button {
  padding: 15px 30px;
}

.btn-icon {
  font-size: 24px;
  margin-right: 8px;
}

.offering-section {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.section-title {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #606266;
}

.offering-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.offering-options .el-check-tag {
  padding: 8px 15px;
}

/* 记录 */
.records-card {
  margin-bottom: 20px;
}

.record-user {
  margin-left: 10px;
  font-size: 13px;
  color: #606266;
}

.record-message {
  margin: 8px 0 0 0;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
}
</style>
