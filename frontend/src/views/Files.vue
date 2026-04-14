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
</script>

<template>
  <div class="files-container">
    <h1>文件管理</h1>
    
    <div class="card mb-lg">
      <h2 class="mb-md">上传文件</h2>
      <div class="flex gap-md">
        <input 
          type="file" 
          ref="fileInput" 
          class="form-input"
        />
        <button 
          @click="handleUpload" 
          :disabled="filesStore.loading" 
          class="btn btn-primary"
        >
          {{ filesStore.loading ? '上传中...' : '上传' }}
        </button>
      </div>
    </div>
    
    <div class="card">
      <h2 class="mb-md">文件列表</h2>
      
      <div v-if="filesStore.loading" class="loading">
        加载中...
      </div>
      
      <table v-else class="w-full">
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
              <div v-if="renameFileId === file.id" class="flex items-center gap-sm">
                <input 
                  type="text" 
                  v-model="newFileName" 
                  class="form-input"
                  @keyup.enter="handleRename"
                  @keyup.esc="cancelRename"
                  style="width: 200px"
                />
                <button @click="handleRename" class="btn btn-sm btn-primary">确定</button>
                <button @click="cancelRename" class="btn btn-sm btn-secondary">取消</button>
              </div>
              <span v-else>{{ file.filename }}</span>
            </td>
            <td>{{ file.size }} bytes</td>
            <td>{{ new Date(file.created_at).toLocaleString() }}</td>
            <td class="flex gap-sm">
              <button @click="handleDownload(file.id)" class="btn btn-sm btn-secondary">下载</button>
              <button v-if="['word', 'excel', 'powerpoint'].includes(file.file_type)" @click="handleEdit(file)" class="btn btn-sm" style="background-color: var(--accent); color: white;">编辑</button>
              <button @click="startRename(file)" class="btn btn-sm" style="background-color: var(--secondary); color: white;" :disabled="renameFileId !== null">重命名</button>
              <button @click="handleDelete(file.id)" class="btn btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="filesStore.files.length === 0 && !filesStore.loading" class="empty-state">
        <h3>暂无文件</h3>
        <p>上传您的第一个文件开始使用</p>
      </div>
    </div>
    
    <div v-if="error" class="error-message mt-md">
      {{ error }}
    </div>
  </div>
</template>

<style scoped>
.files-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>