<template>
  <div class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
      <div class="sidebar-header">
        <el-icon :size="32" color="#d4a574"><Reading /></el-icon>
        <span v-show="!isCollapse" class="sidebar-title">图书馆管理</span>
      </div>
      <el-menu :default-active="activeMenu" :collapse="isCollapse" router background-color="#1a365d" text-color="#b8c5d6" active-text-color="#d4a574" class="sidebar-menu">
        <el-menu-item v-if="isAdmin" index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>数据看板</template>
        </el-menu-item>
        <el-menu-item index="/books">
          <el-icon><Notebook /></el-icon>
          <template #title>图书查询</template>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/borrow">
          <el-icon><Switch /></el-icon>
          <template #title>借还书管理</template>
        </el-menu-item>
        <el-menu-item index="/borrow-records">
          <el-icon><Document /></el-icon>
          <template #title>{{ isAdmin ? '借阅记录' : '我的借阅' }}</template>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/users">
          <el-icon><UserFilled /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item v-if="isAdmin" index="/categories">
          <el-icon><Grid /></el-icon>
          <template #title>分类管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="main-container">
      <el-header class="header">
        <el-icon class="collapse-btn" @click="isCollapse = !isCollapse"><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
        <div class="header-right">
          <span class="welcome-text">欢迎，{{ userStore.currentUser?.name }}（{{ isAdmin ? '管理员' : '用户' }}）</span>
          <el-button type="danger" size="small" @click="handleLogout" plain>退出登录</el-button>
        </div>
      </el-header>
      <el-main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Reading, Odometer, Notebook, Switch, Document, UserFilled, Grid, Fold, Expand } from '@element-plus/icons-vue'
import { useUserStore } from '../store/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isCollapse = ref(false)

const isAdmin = computed(() => userStore.currentUser?.role === 'admin')
const activeMenu = computed(() => route.path)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
}

.sidebar {
  background: #1a365d;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-title {
  color: #d4a574;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px;
  border-radius: 8px;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-menu-item.is-active) {
  background: rgba(212, 165, 116, 0.15) !important;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f7f5f2;
}

.header {
  height: 64px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.collapse-btn {
  font-size: 24px;
  cursor: pointer;
  color: #1a365d;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background: #f0f0f0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-text {
  color: #666;
  font-size: 14px;
}

.content {
  padding: 24px;
  background: #f7f5f2;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>