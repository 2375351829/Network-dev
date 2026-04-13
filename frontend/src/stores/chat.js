import { defineStore } from 'pinia'
import axios from 'axios'

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
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/chat/messages', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
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
        const token = localStorage.getItem('token')
        const response = await axios.post('http://localhost:8000/api/chat/messages', {
          content
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
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