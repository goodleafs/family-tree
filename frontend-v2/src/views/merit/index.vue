<template>
  <div class="merit-page">
    <div class="page-header">
      <button class="back-btn" @click="$router.push(`/families/${familyId}`)">
        <svg viewBox="0 0 16 16" fill="none"><path d="M10 4L6 8l4 4" stroke="currentColor" stroke-width="1.5"/></svg>
        返回
      </button>
      <h1 class="page-title">功德榜</h1>
      <button class="add-btn" @click="openAddDialog">
        <svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.5"/></svg>
        添加记录
      </button>
    </div>

    <!-- 统计 -->
    <div class="stats-row">
      <div class="stat-card"><span class="stat-val">{{ listData.total }}</span><span class="stat-lbl">捐款人次</span></div>
      <div class="stat-card"><span class="stat-val">{{ formatAmount(listData.total_amount) }}</span><span class="stat-lbl">捐款总额（元）</span></div>
    </div>

    <!-- 列表 -->
    <div v-if="listData.items.length === 0" class="empty-hint">
      <div class="empty-icon">🏆</div>
      <p>暂无捐款记录，点击上方按钮添加</p>
    </div>

    <div v-else class="merit-board">
      <div class="board-header">
        <div class="col-rank">排名</div>
        <div class="col-name">捐款人</div>
        <div class="col-amount">金额（元）</div>
        <div class="col-date">日期</div>
        <div class="col-remark">备注</div>
        <div class="col-actions">操作</div>
      </div>
      <div class="board-body">
        <div v-for="(donor, idx) in listData.items" :key="donor.id" class="board-row" :class="{ 'top-three': idx < 3 }">
          <div class="col-rank">
            <span v-if="idx === 0" class="medal gold">🥇</span>
            <span v-else-if="idx === 1" class="medal silver">🥈</span>
            <span v-else-if="idx === 2" class="medal bronze">🥉</span>
            <span v-else class="rank-num">{{ idx + 1 }}</span>
          </div>
          <div class="col-name"><span class="donor-name">{{ donor.donor_name }}</span></div>
          <div class="col-amount"><span class="amount">{{ formatAmount(donor.amount) }}</span></div>
          <div class="col-date">{{ donor.donation_date || '-' }}</div>
          <div class="col-remark">{{ donor.remarks || '-' }}</div>
          <div class="col-actions">
            <button class="action-btn" @click="openEditDialog(donor)">编辑</button>
            <button class="action-btn danger" @click="handleDelete(donor)">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <div class="dialog-overlay" v-if="showDialog" @click="showDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>{{ isEdit ? '编辑捐款记录' : '添加捐款记录' }}</h2>
          <button class="close-btn" @click="showDialog = false">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>捐款人姓名 <span class="required">*</span></label>
            <input v-model="form.donor_name" placeholder="请输入姓名" />
          </div>
          <div class="form-group">
            <label>捐款金额（元） <span class="required">*</span></label>
            <input type="number" v-model.number="form.amount" placeholder="请输入金额" min="0.01" step="0.01" />
          </div>
          <div class="form-group">
            <label>捐款日期</label>
            <input type="date" v-model="form.donation_date" />
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="form.remarks" rows="2" placeholder="可选"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showDialog = false">取消</button>
          <button class="btn-submit" :disabled="saving" @click="handleSave">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { meritApi } from '@/api/merit'
import type { MeritDonor } from '@/types'

const route = useRoute()
const familyId = parseInt(route.params.id as string)

const listData = reactive({ total: 0, total_amount: 0, items: [] as MeritDonor[] })

const showDialog = ref(false)
const isEdit = ref(false)
const editingId = ref(0)
const saving = ref(false)
const form = reactive({ donor_name: '', amount: 0, donation_date: '', remarks: '' })

const fetchData = async () => {
  const res = await meritApi.getDonors(familyId)
  listData.total = res.total
  listData.total_amount = res.total_amount
  listData.items = res.items
}

const openAddDialog = () => {
  isEdit.value = false
  editingId.value = 0
  form.donor_name = ''
  form.amount = 0
  form.donation_date = ''
  form.remarks = ''
  showDialog.value = true
}

const openEditDialog = (donor: MeritDonor) => {
  isEdit.value = true
  editingId.value = donor.id
  form.donor_name = donor.donor_name
  form.amount = donor.amount
  form.donation_date = donor.donation_date || ''
  form.remarks = donor.remarks || ''
  showDialog.value = true
}

const handleSave = async () => {
  if (!form.donor_name || !form.amount || form.amount <= 0) return
  saving.value = true
  try {
    const data = {
      donor_name: form.donor_name,
      amount: form.amount,
      donation_date: form.donation_date || undefined,
      remarks: form.remarks || undefined
    }
    if (isEdit.value) {
      await meritApi.updateDonor(editingId.value, data)
    } else {
      await meritApi.createDonor({ family_id: familyId, ...data })
    }
    showDialog.value = false
    fetchData()
  } finally {
    saving.value = false
  }
}

const handleDelete = async (donor: MeritDonor) => {
  if (!confirm(`确定删除 ${donor.donor_name} 的捐款记录吗？`)) return
  await meritApi.deleteDonor(donor.id)
  fetchData()
}

const formatAmount = (val: number) => val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

onMounted(fetchData)
</script>

<style scoped>
.merit-page { max-width: 960px; }
.page-header { display: flex; align-items: center; gap: var(--space-4); margin-bottom: var(--space-6); }
.back-btn { display: flex; align-items: center; gap: var(--space-1); padding: var(--space-2) var(--space-3); background: none; border: 1px solid var(--border-primary); border-radius: var(--radius-md); color: var(--text-secondary); font-size: var(--text-sm); cursor: pointer; }
.back-btn svg { width: 14px; height: 14px; }
.page-title { flex: 1; font-family: var(--font-title); font-size: var(--text-2xl); margin: 0; }
.add-btn { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); font-size: var(--text-sm); cursor: pointer; }
.add-btn svg { width: 14px; height: 14px; }

.stats-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4); margin-bottom: var(--space-6); }
.stat-card { background: var(--bg-primary); border: 1px solid var(--border-primary); border-radius: var(--radius-lg); padding: var(--space-5); text-align: center; }
.stat-val { display: block; font-size: var(--text-2xl); font-weight: var(--font-bold); color: var(--cinnabar); }
.stat-lbl { font-size: var(--text-sm); color: var(--text-tertiary); margin-top: var(--space-1); }

.merit-board { border: 1px solid var(--border-primary); border-radius: var(--radius-lg); overflow: hidden; }
.board-header { display: flex; background: var(--bg-secondary); font-size: var(--text-xs); color: var(--text-tertiary); padding: var(--space-3) var(--space-4); font-weight: var(--font-medium); }
.board-row { display: flex; padding: var(--space-3) var(--space-4); border-top: 1px solid var(--border-primary); align-items: center; font-size: var(--text-sm); transition: background var(--transition-fast); }
.board-row:hover { background: var(--bg-secondary); }
.board-row.top-three { background: var(--cinnabar-pale); }

.col-rank { width: 60px; flex-shrink: 0; text-align: center; }
.col-name { flex: 1; }
.col-amount { width: 140px; text-align: right; }
.col-date { width: 120px; }
.col-remark { flex: 1; color: var(--text-tertiary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-actions { width: 120px; display: flex; gap: var(--space-2); justify-content: center; }

.medal { font-size: 20px; }
.rank-num { font-size: var(--text-base); font-weight: var(--font-semibold); color: var(--text-secondary); }
.donor-name { font-weight: var(--font-medium); }
.amount { font-weight: var(--font-semibold); color: var(--cinnabar); }

.action-btn { background: none; border: none; font-size: var(--text-xs); color: var(--text-secondary); cursor: pointer; padding: 0; }
.action-btn:hover { color: var(--cinnabar); }
.action-btn.danger { color: var(--cinnabar); }

.empty-hint { text-align: center; padding: var(--space-10); color: var(--text-tertiary); }
.empty-icon { font-size: 48px; margin-bottom: var(--space-4); }

/* Dialog */
.dialog-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-primary); border-radius: var(--radius-lg); width: 480px; max-width: 90vw; box-shadow: var(--shadow-lg); }
.dialog-header { display: flex; justify-content: space-between; align-items: center; padding: var(--space-5); border-bottom: 1px solid var(--border-primary); }
.dialog-header h2 { margin: 0; font-size: var(--text-lg); }
.close-btn { background: none; border: none; font-size: 24px; color: var(--text-secondary); cursor: pointer; }
.dialog-body { padding: var(--space-5); }
.dialog-footer { display: flex; justify-content: flex-end; gap: var(--space-3); padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border-primary); }
.form-group { margin-bottom: var(--space-4); }
.form-group label { display: block; font-size: var(--text-sm); margin-bottom: var(--space-2); }
.form-group input, .form-group textarea { width: 100%; padding: var(--space-3); border: 1px solid var(--border-primary); border-radius: var(--radius-md); font-size: var(--text-base); font-family: var(--font-body); background: var(--bg-primary); box-sizing: border-box; }
.form-group input:focus, .form-group textarea:focus { outline: none; border-color: var(--cinnabar); }
.required { color: var(--cinnabar); }
.btn-cancel { padding: var(--space-2) var(--space-5); background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-md); cursor: pointer; }
.btn-submit { padding: var(--space-2) var(--space-5); background: var(--cinnabar); color: white; border: none; border-radius: var(--radius-md); cursor: pointer; }
.btn-submit:disabled { opacity: 0.6; }
</style>
