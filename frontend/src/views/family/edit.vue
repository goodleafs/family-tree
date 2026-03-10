<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { familyApi } from '@/api/family'
import type { Family } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const familyId = parseInt(route.params.id as string)

// 分别处理字辈顺序字符串，然后在提交时处理转换
const formData = ref<Partial<Family>>({
  name: '',
  surname: '',
  description: '',
  history: '',
  family_motto: '',
  generation_names: [],
  is_public: false
})
const generationNamesStr = ref('')

const loading = ref(false)
const submitting = ref(false)

// 将 generation_names 数组转换为字符串显示在文本框
const generationNamesText = computed({
  get: () => {
    return formData.value.generation_names ? formData.value.generation_names.join('\n') : ''
  },
  set: (value) => {
    // 当用户输入时临时存储到辅助变量，但不改变原结构
    const lines = value.split('\n').filter(line => line.trim() !== '')
    generationNamesStr.value = value
    if (formData.value.generation_names) { // 确保数组已存在
      // 直接保存到对象中 - 这样可以在提交时正确处理
      formData.value.generation_names = lines
    }
  }
})

const fetchFamily = async () => {
  loading.value = true
  try {
    const data = await familyApi.getFamily(familyId)
    formData.value = { ...data }
    
    // 确保 generation_names 是数组
    if (!formData.value.generation_names) {
      formData.value.generation_names = []
    }
    // 如果当前是数组但为空字符串则替换为[]，如果是一个字符串则处理为数组
    if (Array.isArray(formData.value.generation_names) && 
        formData.value.generation_names.length === 1 && 
        formData.value.generation_names[0] === '') {
      formData.value.generation_names = []
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取家族信息失败')
    router.push('/families')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formData.value.name) {
    ElMessage.warning('请输入家族名称')
    return
  }
  
  submitting.value = true
  try {
    // 在提交前确保 generation_names 是数组
    if (typeof formData.value.generation_names === 'string') {
      formData.value.generation_names = formData.value.generation_names.split('\n').filter(item => item.trim() !== '')
    }
    
    await familyApi.updateFamily(familyId, formData.value as Family)
    ElMessage.success('更新家族信息成功')
    router.push(`/families/${familyId}`)
  } catch (error) {
    console.error(error)
    ElMessage.error('更新家族信息失败')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  ElMessageBox.confirm('确定要放弃编辑吗？未保存的更改将丢失。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    router.go(-1)
  })
}

onMounted(() => {
  fetchFamily()
})
</script>

<template>
  <div class="family-edit">
    <el-page-header title="编辑家族信息" @back="handleCancel" />
    
    <el-card v-loading="loading" style="margin-top: 20px;">
      <el-form :model="formData" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="家族名称" required>
              <el-input 
                v-model="formData.name" 
                placeholder="请输入家族名称" 
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="姓氏">
              <el-input 
                v-model="formData.surname" 
                placeholder="请输入姓氏" 
                maxlength="20"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="家族简介">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入家族简介"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="家族史">
          <el-input
            v-model="formData.history"
            type="textarea"
            :rows="4"
            placeholder="请输入家族历史"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="家训">
          <el-input
            v-model="formData.family_motto"
            type="textarea"
            :rows="2"
            placeholder="请输入家训"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="字辈顺序">
          <el-input
            v-model="generationNamesText"
            type="textarea"
            :rows="3"
            placeholder="请输入字辈顺序，每行一个字辈，例如：&#10;德厚 &#10;传家 &#10;永昌"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="是否公开">
          <el-switch 
            v-model="formData.is_public" 
            inline-prompt
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="footer-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button 
            type="primary" 
            :loading="submitting"
            @click="handleSubmit"
          >
            保存修改
          </el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.family-edit {
  padding: 20px 0;
}

.form-item {
  margin-bottom: 20px;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>