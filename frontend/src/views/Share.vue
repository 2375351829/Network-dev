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
</script>

<template>
  <div class="share-container">
    <h1>共享设置</h1>
    
    <div class="card mb-lg">
      <h2 class="mb-md">创建共享</h2>
      <div class="max-w-md">
        <div class="form-group mb-md">
          <label for="file-select" class="form-label">选择文件</label>
          <select 
            id="file-select" 
            v-model="selectedFileId" 
            class="form-input"
          >
            <option value="">请选择文件</option>
            <option v-for="file in filesStore.files" :key="file.id" :value="file.id">
              {{ file.filename }}
            </option>
          </select>
        </div>
        <div class="form-group mb-md">
          <label for="expires-at" class="form-label">过期时间</label>
          <input 
            type="datetime-local" 
            id="expires-at" 
            v-model="expiresAt" 
            class="form-input"
          />
        </div>
        <button 
          @click="handleCreateShare" 
          :disabled="shareStore.loading" 
          class="btn btn-primary"
        >
          {{ shareStore.loading ? '创建中...' : '创建共享' }}
        </button>
      </div>
    </div>
    
    <div class="card">
      <h2 class="mb-md">共享列表</h2>
      
      <div v-if="shareStore.loading" class="loading">
        加载中...
      </div>
      
      <table v-else class="w-full">
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
            <td class="flex items-center gap-sm">
              <span class="flex-1 text-sm break-all">{{ share.share_url }}</span>
              <button @click="copyLink(share.share_url)" class="btn btn-sm btn-secondary">复制</button>
            </td>
            <td>{{ new Date(share.expires_at).toLocaleString() }}</td>
            <td>
              <button @click="handleDeleteShare(share.id)" class="btn btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="shareStore.shares.length === 0 && !shareStore.loading" class="empty-state">
        <h3>暂无共享</h3>
        <p>创建您的第一个文件共享链接</p>
      </div>
    </div>
    
    <div v-if="error" class="error-message mt-md">
      {{ error }}
    </div>
  </div>
</template>

<style scoped>
.share-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>