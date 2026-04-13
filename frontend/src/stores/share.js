import { defineStore } from 'pinia'
import axios from 'axios'

export const useShareStore = defineStore('share', {
  state: () => ({
    shares: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async getShares() {
      this.loading = true
      this.error = null
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/shares', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        this.shares = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取共享列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async createShare(fileId, expiresAt) {
      this.loading = true
      this.error = null
      try {
        const token = localStorage.getItem('token')
        const response = await axios.post('http://localhost:8000/api/shares', {
          file_id: fileId,
          expires_at: expiresAt
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        this.shares.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '创建共享失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteShare(shareId) {
      this.loading = true
      this.error = null
      try {
        const token = localStorage.getItem('token')
        await axios.delete(`http://localhost:8000/api/shares/${shareId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        this.shares = this.shares.filter(share => share.id !== shareId)
      } catch (error) {
        this.error = error.response?.data?.detail || '删除共享失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})