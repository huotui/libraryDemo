<template>
  <div class="categories-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>图书分类管理</span>
          <el-button type="primary" @click="showAddDialog(null)">
            <el-icon><Plus /></el-icon>添加分类
          </el-button>
        </div>
      </template>
      <el-table :data="categories" stripe v-loading="loading" style="width: 100%" row-key="id" default-expand-all>
        <el-table-column prop="name" label="分类名称" min-width="200">
          <template #default="{ row }">
            <span :style="{ paddingLeft: row.parent_id ? '24px' : '0' }">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="showAddDialog(row.id)">添加子分类</el-button>
            <el-button type="primary" size="small" text @click="showEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除该分类？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small" text>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '添加分类'" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="父分类" v-if="!isEdit">
          <el-select v-model="form.parent_id" placeholder="无（顶级分类）" clearable style="width: 100%;">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
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
import { Plus } from '@element-plus/icons-vue'
import { getCategoriesApi, createCategoryApi, updateCategoryApi, deleteCategoryApi } from '../api/library'

const categories = ref([])
const flatCategories = ref([])
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  parent_id: null
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await getCategoriesApi()
    if (res.code === 200) {
      categories.value = res.data.tree
      flatCategories.value = res.data.flat
    }
  } finally { loading.value = false }
}

const showAddDialog = (parentId) => {
  isEdit.value = false
  form.name = ''
  form.parent_id = parentId
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  isEdit.value = true
  editId.value = row.id
  form.name = row.name
  form.parent_id = row.parent_id
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const api = isEdit.value ? updateCategoryApi(editId.value, { name: form.name }) : createCategoryApi(form)
    const res = await api
    if (res.code === 200 || res.code === 201) {
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      dialogVisible.value = false
      fetchCategories()
    }
  } finally { submitLoading.value = false }
}

const handleDelete = async (id) => {
  try {
    const res = await deleteCategoryApi(id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchCategories()
    }
  } catch (e) {}
}

onMounted(fetchCategories)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
