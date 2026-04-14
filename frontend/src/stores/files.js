import { defineStore } from 'pinia'
import api from '../utils/api'

export const useFilesStore = defineStore('files', {
  state: () => ({
    files: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async getFiles() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/files')
        this.files = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取文件列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async uploadFile(file) {
      this.loading = true
      this.error = null
      try {
        const formData = new FormData()
        formData.append('file', file)
        const response = await api.post('/files/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        this.files.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '上传文件失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteFile(fileId) {
      this.loading = true
      this.error = null
      try {
        await api.delete(`/files/${fileId}`)
        this.files = this.files.filter(file => file.id !== fileId)
      } catch (error) {
        this.error = error.response?.data?.detail || '删除文件失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async renameFile(fileId, newName) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/files/${fileId}`, {
          filename: newName
        })
        const index = this.files.findIndex(file => file.id === fileId)
        if (index !== -1) {
          this.files[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '重命名文件失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async downloadFile(fileId) {
      try {
        const response = await api.get(`/files/user/download/${fileId}`, {
          responseType: 'blob'
        })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', response.headers['content-disposition'].split('filename=')[1])
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        this.error = error.response?.data?.detail || '下载文件失败'
        throw error
      }
    },
    
    async editFile(fileId) {
      try {
        const response = await api.get(`/files/${fileId}/edit`)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取编辑配置失败'
        throw error
      }
    }
  }
})
