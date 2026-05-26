<template>
  <div class="books-page">
    <el-card class="search-card" shadow="never">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="书名/作者/ISBN" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category_id" placeholder="全部分类" clearable>
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchBooks">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card" shadow="never" style="margin-top: 16px;">
      <template #header>
        <div class="card-header">
          <span>图书列表</span>
          <el-button v-if="isAdmin" type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>添加图书
          </el-button>
        </div>
      </template>
      <el-table :data="books" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="封面" width="80">
          <template #default="{ row }">
            <el-image v-if="row.image_base64" :src="row.image_base64" fit="cover" style="width: 50px; height: 50px; border-radius: 4px;" :preview-src-list="[row.image_base64]" />
            <span v-else style="color: #999;">无</span>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="书名" min-width="150" />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="isbn" label="ISBN" width="150" />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="publisher" label="出版社" width="140" />
        <el-table-column label="库存" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.available_copies === 0 ? '#f56c6c' : '' }">{{ row.available_copies }} / {{ row.total_copies }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!isAdmin" type="primary" size="small" @click="handleBorrow(row)" :disabled="row.available_copies === 0">借书</el-button>
            <el-button v-if="isAdmin" type="primary" size="small" text @click="showEditDialog(row)">编辑</el-button>
            <el-button v-if="row.image_base64" type="success" size="small" text @click="handleDownloadImage(row)">下载</el-button>
            <el-popconfirm v-if="isAdmin" title="确定删除该书？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.per_page" :total="pagination.total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next" @size-change="fetchBooks" @current-change="fetchBooks" />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑图书' : '添加图书'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="封面图片">
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            :before-upload="beforeImageUpload"
            :http-request="handleImageUpload"
            accept="image/*"
          >
            <img v-if="form.image_base64" :src="form.image_base64" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <el-button v-if="form.image_base64" type="danger" text size="small" @click="removeImage" style="margin-left: 10px;">移除图片</el-button>
        </el-form-item>
        <el-form-item label="书名" prop="title">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="作者" prop="author">
          <el-input v-model="form.author" />
        </el-form-item>
        <el-form-item label="ISBN" prop="isbn">
          <el-input v-model="form.isbn" />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%;">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="出版社">
          <el-input v-model="form.publisher" />
        </el-form-item>
        <el-form-item label="出版日期">
          <el-date-picker v-model="form.publish_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="库存数量" prop="total_copies">
          <el-input-number v-model="form.total_copies" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getBooksApi, createBookApi, updateBookApi, deleteBookApi, getCategoriesApi, borrowBookApi, downloadBookImageApi } from '../api/library'
import { useUserStore } from '../store/user'

const userStore = useUserStore()
const isAdmin = computed(() => userStore.currentUser?.role === 'admin')

const books = ref([])
const categories = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const searchForm = reactive({ keyword: '', category_id: '' })
const pagination = reactive({ page: 1, per_page: 10, total: 0 })
const form = reactive({ title: '', author: '', isbn: '', category_id: '', publisher: '', publish_date: '', total_copies: 999, image_base64: '' })

const rules = {
  title: [{ required: true, message: '请输入书名', trigger: 'blur' }],
  author: [{ required: true, message: '请输入作者', trigger: 'blur' }],
  isbn: [{ required: true, message: '请输入ISBN', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  total_copies: [{ required: true, message: '请输入库存数量', trigger: 'blur' }]
}

const fetchBooks = async () => {
  loading.value = true
  try {
    const res = await getBooksApi({ ...searchForm, ...pagination })
    if (res.code === 200) {
      books.value = res.data.items
      pagination.total = res.data.total
    }
  } finally { loading.value = false }
}

const fetchCategories = async () => {
  try {
    const res = await getCategoriesApi()
    if (res.code === 200) categories.value = res.data.flat
  } catch (e) { console.error(e) }
}

const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.category_id = ''
  pagination.page = 1
  fetchBooks()
}

const handleBorrow = async (row) => {
  try {
    const res = await borrowBookApi({
      user_id: userStore.currentUser.id,
      book_id: row.id
    })
    if (res.code === 200) {
      ElMessage.success('借书成功')
      fetchBooks()
    }
  } catch (e) { console.error(e) }
}

const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, { title: row.title, author: row.author, isbn: row.isbn, category_id: row.category_id, publisher: row.publisher, publish_date: row.publish_date, total_copies: row.total_copies, image_base64: row.image_base64 || '' })
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, { title: '', author: '', isbn: '', category_id: '', publisher: '', publish_date: '', total_copies: 999, image_base64: '' })
  editId.value = null
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const api = isEdit.value ? updateBookApi(editId.value, form) : createBookApi(form)
    const res = await api
    if (res.code === 200 || res.code === 201) {
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      dialogVisible.value = false
      fetchBooks()
    }
  } finally { submitLoading.value = false }
}

const handleDelete = async (id) => {
  try {
    const res = await deleteBookApi(id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchBooks()
    }
  } catch (e) { console.error(e) }
}

const beforeImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleImageUpload = (options) => {
  const { file } = options
  const reader = new FileReader()
  reader.onload = (e) => {
    form.image_base64 = e.target.result
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  form.image_base64 = ''
}

const handleDownloadImage = async (row) => {
  try {
    const res = await downloadBookImageApi(row.id)
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `book_${row.id}.jpg`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    ElMessage.success('下载成功')
  } catch (e) {
    ElMessage.error('下载失败')
    console.error(e)
  }
}

onMounted(() => { fetchBooks(); fetchCategories() })
</script>

<style scoped>
.search-card { border-radius: 12px; }
.table-card { border-radius: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination-wrapper { display: flex; justify-content: flex-end; margin-top: 16px; }

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  display: block;
  border-radius: 8px;
  object-fit: cover;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
}

.avatar-uploader-icon:hover {
  border-color: #409eff;
  color: #409eff;
}
</style>