# 图书馆管理系统 - 接口地址文档

## 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:9999 | Vue 3 + Element Plus 管理后台 |
| 后端 API | http://localhost:8888 | Flask REST API |
| API 代理 | http://localhost:9999/api | 开发环境通过 Vite 代理转发到后端 |

## 测试账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | admin | admin | 全部权限 |
| 普通用户 | test | test | 基础权限 |

## 通用说明

- 请求格式: `application/json`
- 响应格式: `{ code: number, message: string, data: any }`
- 成功状态码: `200` 或 `201`
- 错误状态码: `400`, `401`, `403`, `404`

---

## API 接口列表

### 1. 用户认证 `/api/auth`

#### 1.1 登录
- **URL**: `POST /api/auth/login`
- **请求体**:
  ```json
  { "username": "admin", "password": "admin" }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": { "id": 1, "username": "admin", "name": "系统管理员", "role": "admin", ... }
  }
  ```

#### 1.2 创建用户
- **URL**: `POST /api/auth/users`
- **请求体**:
  ```json
  { "username": "newuser", "password": "123456", "name": "新用户", "phone": "13800138000", "role": "user" }
  ```

---

### 2. 图书管理 `/api/books`

#### 2.1 获取图书列表
- **URL**: `GET /api/books?page=1&per_page=10&keyword=&category_id=`
- **参数**: `page`(页码), `per_page`(每页数量), `keyword`(搜索关键词), `category_id`(分类ID)
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "items": [...],
      "total": 100,
      "page": 1,
      "per_page": 10,
      "pages": 10
    }
  }
  ```

#### 2.2 获取图书详情
- **URL**: `GET /api/books/:id`

#### 2.3 添加图书
- **URL**: `POST /api/books`
- **请求体**:
  ```json
  { "title": "新书", "author": "作者", "isbn": "9787111111111", "category_id": 1, "publisher": "出版社", "publish_date": "2024-01-01", "total_copies": 5 }
  ```

#### 2.4 更新图书
- **URL**: `PUT /api/books/:id`

#### 2.5 删除图书
- **URL**: `DELETE /api/books/:id`

---

### 3. 借还书管理 `/api`

#### 3.1 借书
- **URL**: `POST /api/borrow`
- **请求体**:
  ```json
  { "user_id": 1, "book_id": 1 }
  ```

#### 3.2 还书
- **URL**: `POST /api/return`
- **请求体** (通过记录ID还书，推荐):
  ```json
  { "record_id": 1 }
  ```
- **请求体** (通过图书ID还书，管理员用):
  ```json
  { "book_id": 1 }
  ```
- **响应** (含逾期罚款):
  ```json
  { "code": 200, "message": "还书成功", "data": { "fine": 5.00, ... } }
  ```

#### 3.3 获取借阅记录
- **URL**: `GET /api/records?page=1&per_page=10&keyword=&status=&user_id=`
- **参数**: `status` 可选值: `borrowed`(借阅中), `returned`(已归还)

#### 3.4 获取数据看板
- **URL**: `GET /api/dashboard`
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "today_borrows": 5,
      "current_borrows": 20,
      "overdue_count": 3,
      "recent_records": [...]
    }
  }
  ```

---

### 4. 用户管理 `/api/users`

#### 4.1 获取用户列表
- **URL**: `GET /api/users?page=1&per_page=10&keyword=&role=`
- **参数**: `role` 可选值: `admin`, `user`

#### 4.2 获取用户详情
- **URL**: `GET /api/users/:id`

#### 4.3 更新用户
- **URL**: `PUT /api/users/:id`
- **请求体**:
  ```json
  { "name": "新名字", "phone": "13900139000", "email": "test@example.com", "role": "user", "status": "active" }
  ```

#### 4.4 删除用户
- **URL**: `DELETE /api/users/:id`
- **注意**: 不能删除管理员账户，不能删除有未归还图书的用户

---

### 5. 分类管理 `/api/categories`

#### 5.1 获取分类列表
- **URL**: `GET /api/categories`
- **响应**:
  ```json
  {
    "code": 200,
    "data": {
      "tree": [{ "id": 1, "name": "文学", "parent_id": null, "children": [...] }],
      "flat": [{ "id": 1, "name": "文学", "parent_id": null }]
    }
  }
  ```

#### 5.2 添加分类
- **URL**: `POST /api/categories`
- **请求体**:
  ```json
  { "name": "子分类", "parent_id": 1 }
  ```

#### 5.3 更新分类
- **URL**: `PUT /api/categories/:id`

#### 5.4 删除分类
- **URL**: `DELETE /api/categories/:id`
- **注意**: 不能删除有图书或子分类的分类

---

## 前端路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/login` | 登录页 | 用户认证 |
| `/` | 首页 | 重定向到数据看板 |
| `/dashboard` | 数据看板 | 统计概览 |
| `/books` | 图书管理 | 图书CRUD |
| `/borrow` | 借还书管理 | 借书/还书操作 |
| `/borrow-records` | 借阅记录 | 借阅历史 |
| `/users` | 用户管理 | 用户CRUD |
| `/categories` | 分类管理 | 分类树管理 |
