<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFilesStore } from '../stores/files'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const filesStore = useFilesStore()
const authStore = useAuthStore()

const fileInput = ref(null)
const renameFileId = ref(null)
const newFileName = ref('')
const error = ref('')

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await filesStore.getFiles()
})

async function handleUpload() {
  const file = fileInput.value.files[0]
  if (!file) return
  
  try {
    await filesStore.uploadFile(file)
    fileInput.value.value = ''
  } catch (err) {
    error.value = filesStore.error || '上传失败'
  }
}

async function handleDownload(fileId) {
  try {
    await filesStore.downloadFile(fileId)
  } catch (err) {
    error.value = filesStore.error || '下载失败'
  }
}

async function handleEdit(file) {
  try {
    const editConfig = await filesStore.editFile(file.id)
    // 打开编辑窗口
    const editorUrl = `${editConfig.onlyoffice_url}?config=${encodeURIComponent(JSON.stringify(editConfig.config))}`
    window.open(editorUrl, '_blank', 'width=1200,height=800')
  } catch (err) {
    error.value = filesStore.error || '编辑失败'
  }
}

async function handleDelete(fileId) {
  if (!confirm('确定要删除这个文件吗？')) return
  
  try {
    await filesStore.deleteFile(fileId)
  } catch (err) {
    error.value = filesStore.error || '删除失败'
  }
}

function startRename(file) {
  renameFileId.value = file.id
  newFileName.value = file.filename
}

async function handleRename() {
  if (!newFileName.value) return
  
  try {
    await filesStore.renameFile(renameFileId.value, newFileName.value)
    renameFileId.value = null
    newFileName.value = ''
  } catch (err) {
    error.value = filesStore.error || '重命名失败'
  }
}

function cancelRename() {
  renameFileId.value = null
  newFileName.value = ''
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="files-container">
    <header class="files-header">
      <h1>文件管理</h1>
      <div class="header-actions">
        <router-link to="/share" class="nav-link">共享设置</router-link>
        <router-link to="/chat" class="nav-link">聊天</router-link>
        <router-link to="/multimedia" class="nav-link">多媒体</router-link>
        <router-link to="/backup" class="nav-link">备份管理</router-link>
        <router-link to="/notification" class="nav-link">通知中心</router-link>
        <button @click="logout" class="logout-button">退出登录</button>
      </div>
    </header>
    
    <div class="upload-section">
      <h2>上传文件</h2>
      <div class="upload-form">
        <input 
          type="file" 
          ref="fileInput" 
          class="file-input"
        />
        <button 
          @click="handleUpload" 
          :disabled="filesStore.loading" 
          class="upload-button"
        >
          {{ filesStore.loading ? '上传中...' : '上传' }}
        </button>
      </div>
    </div>
    
    <div class="files-list">
      <h2>文件列表</h2>
      <table class="files-table">
        <thead>
          <tr>
            <th>文件名</th>
            <th>大小</th>
            <th>上传时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in filesStore.files" :key="file.id">
            <td>
              <div v-if="renameFileId === file.id">
                <input 
                  type="text" 
                  v-model="newFileName" 
                  class="rename-input"
                  @keyup.enter="handleRename"
                  @keyup.esc="cancelRename"
                  ref="renameInput"
                />
                <button @click="handleRename" class="rename-confirm">确定</button>
                <button @click="cancelRename" class="rename-cancel">取消</button>
              </div>
              <span v-else>{{ file.filename }}</span>
            </td>
            <td>{{ file.size }} bytes</td>
            <td>{{ new Date(file.created_at).toLocaleString() }}</td>
            <td class="file-actions">
              <button @click="handleDownload(file.id)" class="action-button download">下载</button>
              <button v-if="['word', 'excel', 'powerpoint'].includes(file.file_type)" @click="handleEdit(file)" class="action-button edit">编辑</button>
              <button @click="startRename(file)" class="action-button rename" :disabled="renameFileId !== null">重命名</button>
              <button @click="handleDelete(file.id)" class="action-button delete">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="filesStore.files.length === 0" class="empty-message">暂无文件</p>
    </div>
    
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<style scoped>
.files-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}

.files-header h1 {
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

.upload-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.upload-section h2 {
  color: #333;
  margin-bottom: 15px;
  font-size: 18px;
}

.upload-form {
  display: flex;
  gap: 10px;
  align-items: center;
}

.file-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.upload-button {
  padding: 10px 20px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.upload-button:hover {
  background-color: #35495e;
}

.upload-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.files-list {
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: 20px;
}

.files-list h2 {
  color: #333;
  margin-bottom: 15px;
  font-size: 18px;
}

.files-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.files-table th,
.files-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.files-table th {
  background-color: #f5f5f5;
  font-weight: 600;
  color: #555;
}

.files-table tr:hover {
  background-color: #f9f9f9;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.action-button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.action-button.download {
  background-color: #3498db;
  color: white;
}

.action-button.download:hover {
  background-color: #2980b9;
}

.action-button.rename {
  background-color: #f39c12;
  color: white;
}

.action-button.rename:hover {
  background-color: #e67e22;
}

.action-button.rename:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.action-button.delete {
  background-color: #e74c3c;
  color: white;
}

.action-button.delete:hover {
  background-color: #c0392b;
}

.action-button.edit {
  background-color: #9b59b6;
  color: white;
}

.action-button.edit:hover {
  background-color: #8e44ad;
}

.rename-input {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-right: 8px;
  width: 200px;
}

.rename-confirm {
  padding: 4px 8px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  margin-right: 8px;
}

.rename-confirm:hover {
  background-color: #35495e;
}

.rename-cancel {
  padding: 4px 8px;
  background-color: #95a5a6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.rename-cancel:hover {
  background-color: #7f8c8d;
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