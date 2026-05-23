<template>
  <div class="borrow-records-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>{{ isAdmin ? '借阅记录' : '我的借阅记录' }}</span>
          <el-form :inline="true" :model="searchForm" v-if="isAdmin">
            <el-form-item label="关键词">
              <el-input v-model="searchForm.keyword" placeholder="用户/图书" clearable />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
                <el-option label="借阅中" value="borrowed" />
                <el-option label="已归还" value="returned" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="fetchRecords">搜索</el-button>
            </el-form-item>
          </el-form>
        </div>
      </template>
      <el-table :data="records" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column v-if="isAdmin" prop="user_name" label="借阅人" width="120" />
        <el-table-column prop="book_title" label="图书名称" min-width="180" />
        <el-table-column prop="borrow_date" label="借阅时间" width="170" />
        <el-table-column prop="due_date" label="到期时间" width="170" />
        <el-table-column prop="return_date" label="归还时间" width="170" />
        <el-table-column prop="fine" label="罚款(元)" width="100">
          <template #default="{ row }">
            <span v-if="row.fine > 0" style="color: #f56c6c;">¥{{ row.fine.toFixed(2) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'returned' ? 'success' : row.status === 'borrowed' ? 'primary' : 'danger'" size="small">
              {{ row.status === 'borrowed' ? '借阅中' : row.status === 'returned' ? '已归还' : '已逾期' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'borrowed'" type="success" size="small" @click="handleReturn(row)">还书</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.per_page" :total="pagination.total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="fetchRecords" @current-change="fetchRecords" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getBorrowRecordsApi, returnBookApi } from '../api/library'
import { useUserStore } from '../store/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.currentUser?.role === 'admin')

const records = ref([])
const loading = ref(false)

const searchForm = reactive({ keyword: '', status: '' })
const pagination = reactive({ page: 1, per_page: 10, total: 0 })

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = { ...searchForm, ...pagination }
    if (!isAdmin) {
      params.user_id = userStore.currentUser.id
    }
    const res = await getBorrowRecordsApi(params)
    if (res.code === 200) {
      records.value = res.data.items
      pagination.total = res.data.total
    }
  } finally { loading.value = false }
}

const handleReturn = async (row) => {
  try {
    const res = await returnBookApi({ record_id: row.id })
    if (res.code === 200) {
      ElMessage.success('还书成功')
      if (res.data.fine > 0) {
        ElMessage.warning(`逾期罚款：¥${res.data.fine.toFixed(2)}`)
      }
      fetchRecords()
    }
  } catch (e) { console.error(e) }
}

onMounted(fetchRecords)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>