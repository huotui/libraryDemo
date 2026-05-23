<template>
  <div class="borrow-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="never" class="borrow-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="24"><Right /></el-icon>
              <span>借书</span>
            </div>
          </template>
          <el-form :model="borrowForm" label-width="100px">
            <el-form-item label="用户ID">
              <el-input v-model="borrowForm.user_id" placeholder="请输入用户ID" @blur="fetchUserInfo">
                <template #append>
                  <el-button @click="fetchUserInfo">查询</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="用户信息" v-if="borrowUserInfo">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="姓名">{{ borrowUserInfo.name }}</el-descriptions-item>
                <el-descriptions-item label="电话">{{ borrowUserInfo.phone || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-form-item>
            <el-form-item label="图书ID">
              <el-input v-model="borrowForm.book_id" placeholder="请输入图书ID" @blur="fetchBookInfo">
                <template #append>
                  <el-button @click="fetchBookInfo">查询</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="图书信息" v-if="borrowBookInfo">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="书名">{{ borrowBookInfo.title }}</el-descriptions-item>
                <el-descriptions-item label="作者">{{ borrowBookInfo.author }}</el-descriptions-item>
                <el-descriptions-item label="可借">{{ borrowBookInfo.available_copies }} / {{ borrowBookInfo.total_copies }}</el-descriptions-item>
              </el-descriptions>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" @click="handleBorrow" :loading="borrowLoading" style="width: 100%;">确认借书</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never" class="return-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="24"><Back /></el-icon>
              <span>还书</span>
            </div>
          </template>
          <el-form :model="returnForm" label-width="100px">
            <el-form-item label="图书ID">
              <el-input v-model="returnForm.book_id" placeholder="请输入图书ID" @blur="fetchReturnBookInfo">
                <template #append>
                  <el-button @click="fetchReturnBookInfo">查询</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="图书信息" v-if="returnBookInfo">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="书名">{{ returnBookInfo.title }}</el-descriptions-item>
                <el-descriptions-item label="借阅人">{{ returnBookInfo.borrower || '-' }}</el-descriptions-item>
                <el-descriptions-item label="到期日">{{ returnBookInfo.due_date || '-' }}</el-descriptions-item>
              </el-descriptions>
            </el-form-item>
            <el-form-item>
              <el-button type="success" size="large" @click="handleReturn" :loading="returnLoading" style="width: 100%;">确认还书</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Right, Back } from '@element-plus/icons-vue'
import { borrowBookApi, returnBookApi, getBookApi, getUsersApi } from '../api/library'

const borrowForm = reactive({ user_id: '', book_id: '' })
const returnForm = reactive({ book_id: '' })

const borrowUserInfo = ref(null)
const borrowBookInfo = ref(null)
const returnBookInfo = ref(null)
const borrowLoading = ref(false)
const returnLoading = ref(false)

const fetchUserInfo = async () => {
  if (!borrowForm.user_id) return
  try {
    const res = await getUsersApi({})
    if (res.code === 200) {
      const user = res.data.items.find(u => u.id == borrowForm.user_id)
      if (user) {
        borrowUserInfo.value = user
      } else {
        ElMessage.warning('用户不存在')
        borrowUserInfo.value = null
      }
    }
  } catch (e) {}
}

const fetchBookInfo = async () => {
  if (!borrowForm.book_id) return
  try {
    const res = await getBookApi(borrowForm.book_id)
    if (res.code === 200) {
      borrowBookInfo.value = res.data
    } else {
      ElMessage.warning('图书不存在')
      borrowBookInfo.value = null
    }
  } catch (e) {
    borrowBookInfo.value = null
  }
}

const fetchReturnBookInfo = async () => {
  if (!returnForm.book_id) return
  try {
    const res = await getBookApi(returnForm.book_id)
    if (res.code === 200) {
      returnBookInfo.value = { ...res.data, borrower: '待查询', due_date: '待查询' }
    } else {
      ElMessage.warning('图书不存在')
      returnBookInfo.value = null
    }
  } catch (e) {
    returnBookInfo.value = null
  }
}

const handleBorrow = async () => {
  if (!borrowForm.user_id || !borrowForm.book_id) {
    ElMessage.warning('请填写用户ID和图书ID')
    return
  }
  borrowLoading.value = true
  try {
    const res = await borrowBookApi({
      user_id: parseInt(borrowForm.user_id),
      book_id: parseInt(borrowForm.book_id)
    })
    if (res.code === 200) {
      ElMessage.success('借书成功')
      borrowForm.book_id = ''
      borrowBookInfo.value = null
    }
  } catch (e) {} finally {
    borrowLoading.value = false
  }
}

const handleReturn = async () => {
  if (!returnForm.book_id) {
    ElMessage.warning('请填写图书ID')
    return
  }
  returnLoading.value = true
  try {
    const res = await returnBookApi({ book_id: parseInt(returnForm.book_id) })
    if (res.code === 200) {
      ElMessage.success('还书成功')
      if (res.data.fine > 0) {
        ElMessage.warning(`逾期罚款：¥${res.data.fine.toFixed(2)}`)
      }
      returnForm.book_id = ''
      returnBookInfo.value = null
    }
  } catch (e) {} finally {
    returnLoading.value = false
  }
}
</script>

<style scoped>
.borrow-page {
  min-height: calc(100vh - 140px);
}

.borrow-card, .return-card {
  border-radius: 12px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1a365d;
}

.borrow-card .card-header { color: #1a365d; }
.return-card .card-header { color: #67c23a; }
</style>
