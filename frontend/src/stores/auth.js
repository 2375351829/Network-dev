import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },
  
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post('http://localhost:8000/api/auth/login/json', {
          username,
          password
        })
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem('token', this.token)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '登录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async register(username, password, email) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post('http://localhost:8000/api/auth/register', {
          username,
          password,
          email
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },
    
    async getProfile() {
      if (!this.token) return
      this.loading = true
      try {
        const response = await axios.get('http://localhost:8000/api/auth/me', {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        this.user = response.data
      } catch (error) {
        this.logout()
      } finally {
        this.loading = false
      }
    }
  }
})