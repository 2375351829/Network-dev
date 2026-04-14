import { defineStore } from 'pinia'
import api from '../utils/api'

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
        const response = await api.get('/shares')
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
        const response = await api.post('/shares', {
          file_id: fileId,
          expires_at: expiresAt
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
        await api.delete(`/shares/${shareId}`)
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
