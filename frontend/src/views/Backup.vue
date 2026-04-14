<template>
  <div class="backup-container">
    <h1>备份管理</h1>
    
    <!-- 备份状态 -->
    <div class="card mb-lg">
      <h2 class="mb-md">备份状态</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else class="status-info">
        <p class="mb-sm">状态: {{ backupStatus.status }}</p>
        <p v-if="backupStatus.last_backup" class="mb-sm">最后备份: {{ formatDateTime(backupStatus.last_backup) }}</p>
        <p v-if="backupStatus.next_backup">下次备份: {{ formatDateTime(backupStatus.next_backup) }}</p>
      </div>
    </div>
    
    <!-- 备份配置 -->
    <div class="card mb-lg">
      <h2 class="mb-md">备份配置</h2>
      <form @submit.prevent="updateConfig">
        <div class="form-group mb-md">
          <label class="flex items-center gap-sm">
            <input type="checkbox" v-model="config.enabled" class="mr-sm">
            启用自动备份
          </label>
        </div>
        <div class="form-group mb-md">
          <label for="interval" class="form-label">备份间隔</label>
          <select id="interval" v-model="config.interval" class="form-input">
            <option value="daily">每天</option>
            <option value="weekly">每周</option>
            <option value="monthly">每月</option>
          </select>
        </div>
        <div class="form-group mb-md">
          <label for="backup_path" class="form-label">备份路径</label>
          <input type="text" id="backup_path" v-model="config.backup_path" placeholder="备份文件存储路径" class="form-input">
        </div>
        <div class="form-group mb-md">
          <label class="flex items-center gap-sm">
            <input type="checkbox" v-model="config.include_all_users" class="mr-sm">
            包含所有用户文件
          </label>
        </div>
        <button type="submit" class="btn btn-primary">保存配置</button>
      </form>
    </div>
    
    <!-- 手动备份 -->
    <div class="card mb-lg">
      <h2 class="mb-md">手动备份</h2>
      <button @click="runBackup" class="btn btn-success" :disabled="backupStatus.status === 'running'">
        {{ backupStatus.status === 'running' ? '备份中...' : '立即备份' }}
      </button>
    </div>
    
    <!-- 备份历史 -->
    <div class="card">
      <h2 class="mb-md">备份历史</h2>
      <div v-if="backups.length === 0" class="empty-state">
        <h3>暂无备份记录</h3>
        <p>运行第一次备份开始记录</p>
      </div>
      <table v-else class="w-full">
        <thead>
          <tr>
            <th>备份名称</th>
            <th>时间</th>
            <th>大小</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="backup in backups" :key="backup.name">
            <td>{{ backup.name }}</td>
            <td>{{ formatDateTime(backup.timestamp) }}</td>
            <td>{{ formatSize(backup.size) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

const backupStatus = ref({})
const config = ref({
  enabled: true,
  interval: 'daily',
  backup_path: './backups',
  include_all_users: false
})
const backups = ref([])
const loading = ref(true)

// 格式化日期时间
const formatDateTime = (dateTime) => {
  const date = new Date(dateTime)
  return date.toLocaleString()
}

// 格式化文件大小
const formatSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(2) + ' MB'
  return (size / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

// 获取备份状态
const getBackupStatus = async () => {
  try {
    const response = await api.get('/backup/status')
    backupStatus.value = response.data
  } catch (error) {
    console.error('获取备份状态失败:', error)
  }
}

// 获取备份配置
const getBackupConfig = async () => {
  try {
    const response = await api.get('/backup/config')
    config.value = response.data
  } catch (error) {
    console.error('获取备份配置失败:', error)
  }
}

// 获取备份历史
const getBackups = async () => {
  try {
    const response = await api.get('/backup/list')
    backups.value = response.data
  } catch (error) {
    console.error('获取备份历史失败:', error)
  }
}

// 更新备份配置
const updateConfig = async () => {
  try {
    await api.post('/backup/config', config.value)
    alert('配置更新成功')
  } catch (error) {
    console.error('更新备份配置失败:', error)
    alert('配置更新失败')
  }
}

// 手动执行备份
const runBackup = async () => {
  try {
    await api.post('/backup/run')
    alert('备份已开始')
    // 刷新状态
    setTimeout(getBackupStatus, 1000)
  } catch (error) {
    console.error('执行备份失败:', error)
    alert('备份失败')
  }
}

// 页面加载时获取数据
onMounted(async () => {
  loading.value = true
  await Promise.all([
    getBackupStatus(),
    getBackupConfig(),
    getBackups()
  ])
  loading.value = false
})
</script>

<style scoped>
.backup-container {
  max-width: 800px;
  margin: 0 auto;
}

.mr-sm {
  margin-right: var(--spacing-sm);
}
</style>