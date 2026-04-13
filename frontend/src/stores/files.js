import { defineStore } from 'pinia'
import axios from 'axios'

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
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/files', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
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
        const token = localStorage.getItem('token')
        const formData = new FormData()
        formData.append('file', file)
        const response = await axios.post('http://localhost:8000/api/files/upload', formData, {
          headers: {
            Authorization: `Bearer ${token}`,
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
        const token = localStorage.getItem('token')
        await axios.delete(`http://localhost:8000/api/files/${fileId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
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
        const token = localStorage.getItem('token')
        const response = await axios.put(`http://localhost:8000/api/files/${fileId}`, {
          filename: newName
        }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
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
        const token = localStorage.getItem('token')
        const response = await axios.get(`http://localhost:8000/api/files/user/download/${fileId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          },
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
        const token = localStorage.getItem('token')
        const response = await axios.get(`http://localhost:8000/api/files/${fileId}/edit`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || '获取编辑配置失败'
        throw error
      }
    }
  }
})