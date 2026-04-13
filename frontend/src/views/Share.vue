<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useShareStore } from '../stores/share'
import { useFilesStore } from '../stores/files'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const shareStore = useShareStore()
const filesStore = useFilesStore()
const authStore = useAuthStore()

const selectedFileId = ref('')
const expiresAt = ref('')
const error = ref('')

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await Promise.all([
    filesStore.getFiles(),
    shareStore.getShares()
  ])
})

async function handleCreateShare() {
  if (!selectedFileId.value || !expiresAt.value) {
    error.value = '请选择文件并设置过期时间'
    return
  }
  
  try {
    await shareStore.createShare(selectedFileId.value, expiresAt.value)
    selectedFileId.value = ''
    expiresAt.value = ''
    error.value = ''
  } catch (err) {
    error.value = shareStore.error || '创建共享失败'
  }
}

async function handleDeleteShare(shareId) {
  if (!confirm('确定要删除这个共享吗？')) return
  
  try {
    await shareStore.deleteShare(shareId)
  } catch (err) {
    error.value = shareStore.error || '删除共享失败'
  }
}

function copyLink(link) {
  navigator.clipboard.writeText(link)
    .then(() => {
      alert('链接已复制到剪贴板')
    })
    .catch(err => {
      console.error('复制失败:', err)
    })
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="share-container">
    <header class="share-header">
      <h1>共享设置</h1>
      <div class="header-actions">
        <router-link to="/files" class="nav-link">文件管理</router-link>
        <router-link to="/chat" class="nav-link">聊天</router-link>
        <button @click="logout" class="logout-button">退出登录</button>
      </div>
    </header>
    
    <div class="create-share-section">
      <h2>创建共享</h2>
      <div class="create-share-form">
        <div class="form-group">
          <label for="file-select">选择文件</label>
          <select 
            id="file-select" 
            v-model="selectedFileId" 
            class="file-select"
          >
            <option value="">请选择文件</option>
            <option v-for="file in filesStore.files" :key="file.id" :value="file.id">
              {{ file.filename }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label for="expires-at">过期时间</label>
          <input 
            type="datetime-local" 
            id="expires-at" 
            v-model="expiresAt" 
            class="expires-input"
          />
        </div>
        <button 
          @click="handleCreateShare" 
          :disabled="shareStore.loading" 
          class="create-share-button"
        >
          {{ shareStore.loading ? '创建中...' : '创建共享' }}
        </button>
      </div>
    </div>
    
    <div class="shares-list">
      <h2>共享列表</h2>
      <table class="shares-table">
        <thead>
          <tr>
            <th>文件名</th>
            <th>共享链接</th>
            <th>过期时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="share in shareStore.shares" :key="share.id">
            <td>{{ share.file.filename }}</td>
            <td>
              <div class="share-link">
                <span>{{ share.share_url }}</span>
                <button @click="copyLink(share.share_url)" class="copy-button">复制</button>
              </div>
            </td>
            <td>{{ new Date(share.expires_at).toLocaleString() }}</td>
            <td class="share-actions">
              <button @click="handleDeleteShare(share.id)" class="action-button delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="shareStore.shares.length === 0" class="empty-message">暂无共享</p>
    </div>
    
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<style scoped>
.share-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.share-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}

.share-header h1 {
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.nav-link {
  color: #42b883;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #35495e;
}

.logout-button {
  padding: 8px 16px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #c0392b;
}

.create-share-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.create-share-section h2 {
  color: #333;
  margin-bottom: 15px;
  font-size: 18px;
}

.create-share-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 600px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.file-select,
.expires-input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.file-select:focus,
.expires-input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.create-share-button {
  padding: 12px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  align-self: flex-start;
}

.create-share-button:hover {
  background-color: #35495e;
}

.create-share-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.shares-list {
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.shares-list h2 {
  color: #333;
  margin-bottom: 15px;
  font-size: 18px;
}

.shares-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.shares-table th,
.shares-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.shares-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #555;
}

.shares-table tr:hover {
  background-color: #f9f9f9;
}

.share-link {
  display: flex;
  align-items: center;
  gap: 10px;
}

.share-link span {
  flex: 1;
  font-size: 14px;
  color: #333;
  word-break: break-all;
}

.copy-button {
  padding: 4px 8px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.copy-button:hover {
  background-color: #2980b9;
}

.share-actions {
  display: flex;
  gap: 8px;
}

.action-button.delete {
  padding: 6px 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.action-button.delete:hover {
  background-color: #c0392b;
}

.empty-message {
  text-align: center;
  color: #7f8c8d;
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  margin-top: 20px;
  padding: 10px;
  background-color: #fadbd8;
  border-radius: 4px;
}
</style>