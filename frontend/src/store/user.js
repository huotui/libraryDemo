import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  
  const setUser = (user) => {
    currentUser.value = user
    localStorage.setItem('user', JSON.stringify(user))
  }
  
  const logout = () => {
    currentUser.value = null
    localStorage.removeItem('user')
  }
  
  const initUser = () => {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      currentUser.value = JSON.parse(userStr)
    }
  }
  
  return { currentUser, setUser, logout, initUser }
})
