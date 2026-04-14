import { defineStore } from 'pinia'
import api from '../utils/api'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async getMessages() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/chat/messages')
        this.messages = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取消息列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async sendMessage(content) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/chat/messages', {
          content
        })
        this.messages.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '发送消息失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
