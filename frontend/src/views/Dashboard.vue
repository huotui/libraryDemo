<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
            <el-icon :size="32"><Calendar /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ dashboard.today_borrows }}</div>
            <div class="stat-label">今日借出</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb, #f5576c);">
            <el-icon :size="32"><Notebook /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ dashboard.current_borrows }}</div>
            <div class="stat-label">在借图书</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a, #fee140);">
            <el-icon :size="32"><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value" style="color: #e6a23c;">{{ dashboard.overdue_count }}</div>
            <div class="stat-label">逾期未还</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card quick-actions" shadow="hover">
          <div class="quick-actions-grid">
            <el-button type="primary" @click="$router.push('/borrow')">快速借书</el-button>
            <el-button type="success" @click="$router.push('/borrow')">快速还书</el-button>
            <el-button type="warning" @click="$router.push('/books')">添加图书</el-button>
            <el-button type="info" @click="$router.push('/users')">添加用户</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="recent-records" style="margin-top: 24px;">
      <template #header>
        <div class="card-header">
          <span>最近借阅记录</span>
          <el-button type="primary" text @click="$router.push('/borrow-records')">查看全部</el-button>
        </div>
      </template>
      <el-table :data="dashboard.recent_records" stripe style="width: 100%">
        <el-table-column prop="user_name" label="借阅人" width="120" />
        <el-table-column prop="book_title" label="图书名称" min-width="200" />
        <el-table-column prop="borrow_date" label="借阅时间" width="180" />
        <el-table-column prop="due_date" label="到期时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'returned' ? 'success' : row.status === 'borrowed' ? 'primary' : 'danger'" size="small">
              {{ row.status === 'borrowed' ? '借阅中' : row.status === 'returned' ? '已归还' : '已逾期' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Calendar, Notebook, Warning } from '@element-plus/icons-vue'
import { getDashboardApi } from '../api/library'

const dashboard = ref({
  today_borrows: 0,
  current_borrows: 0,
  overdue_count: 0,
  recent_records: []
})

const fetchDashboard = async () => {
  try {
    const res = await getDashboardApi()
    if (res.code === 200) {
      dashboard.value = res.data
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(fetchDashboard)
</script>

<style scoped>
.stat-cards {
  margin-bottom: 0;
}

.stat-card {
  padding: 20px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1a365d;
  line-height: 1.2;
}

.stat-label {
  color: #888;
  font-size: 14px;
  margin-top: 4px;
}

.quick-actions :deep(.el-card__body) {
  display: block;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-actions-grid .el-button {
  height: 48px;
  border-radius: 10px;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-records {
  border-radius: 12px;
}
</style>
