import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/books',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '数据看板', requireAdmin: true }
      },
      {
        path: 'books',
        name: 'Books',
        component: () => import('../views/Books.vue'),
        meta: { title: '图书查询' }
      },
      {
        path: 'borrow',
        name: 'Borrow',
        component: () => import('../views/Borrow.vue'),
        meta: { title: '借还书管理', requireAdmin: true }
      },
      {
        path: 'borrow-records',
        name: 'BorrowRecords',
        component: () => import('../views/BorrowRecords.vue'),
        meta: { title: '借阅记录' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理', requireAdmin: true }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('../views/Categories.vue'),
        meta: { title: '分类管理', requireAdmin: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const adminPages = ['/dashboard', '/borrow', '/users', '/categories']

router.beforeEach((to) => {
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null

  if (to.path !== '/login' && !user) {
    return '/login'
  }
  if (to.path === '/login' && user) {
    return '/books'
  }
  if (user && user.role !== 'admin' && adminPages.includes(to.path)) {
    return '/books'
  }
})

export default router