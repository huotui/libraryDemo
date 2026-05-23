import api from './index'

export const loginApi = (data) => api.post('/auth/login', data)

export const getDashboardApi = () => api.get('/dashboard')

export const getBooksApi = (params) => api.get('/books', { params })

export const getBookApi = (id) => api.get(`/books/${id}`)

export const createBookApi = (data) => api.post('/books', data)

export const updateBookApi = (id, data) => api.put(`/books/${id}`, data)

export const deleteBookApi = (id) => api.delete(`/books/${id}`)

export const borrowBookApi = (data) => api.post('/borrow', data)

export const returnBookApi = (data) => api.post('/return', data)

export const getBorrowRecordsApi = (params) => api.get('/records', { params })

export const getUsersApi = (params) => api.get('/users', { params })

export const getUserApi = (id) => api.get(`/users/${id}`)

export const updateUserApi = (id, data) => api.put(`/users/${id}`, data)

export const deleteUserApi = (id) => api.delete(`/users/${id}`)

export const createUserApi = (data) => api.post('/auth/users', data)

export const getCategoriesApi = () => api.get('/categories')

export const createCategoryApi = (data) => api.post('/categories', data)

export const updateCategoryApi = (id, data) => api.put(`/categories/${id}`, data)

export const deleteCategoryApi = (id) => api.delete(`/categories/${id}`)
