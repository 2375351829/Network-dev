<template>
  <div class="backup-container">
    <h1>备份管理</h1>
    
    <!-- 备份状态 -->
    <div class="backup-status">
      <h2>备份状态</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else class="status-info">
        <p>状态: {{ backupStatus.status }}</p>
        <p v-if="backupStatus.last_backup">最后备份: {{ formatDateTime(backupStatus.last_backup) }}</p>
        <p v-if="backupStatus.next_backup">下次备份: {{ formatDateTime(backupStatus.next_backup) }}</p>
      </div>
    </div>
    
    <!-- 备份配置 -->
    <div class="backup-config">
      <h2>备份配置</h2>
      <form @submit.prevent="updateConfig">
        <div class="form-group">
          <label>
            <input type="checkbox" v-model="config.enabled">
            启用自动备份
          </label>
        </div>
        <div class="form-group">
          <label>备份间隔</label>
          <select v-model="config.interval">
            <option value="daily">每天</option>
            <option value="weekly">每周</option>
            <option value="monthly">每月</option>
          </select>
        </div>
        <div class="form-group">
          <label>备份路径</label>
          <input type="text" v-model="config.backup_path" placeholder="备份文件存储路径">
        </div>
        <div class="form-group">
          <label>
            <input type="checkbox" v-model="config.include_all_users">
            包含所有用户文件
          </label>
        </div>
        <button type="submit" class="btn btn-primary">保存配置</button>
      </form>
    </div>
    
    <!-- 手动备份 -->
    <div class="manual-backup">
      <h2>手动备份</h2>
      <button @click="runBackup" class="btn btn-success" :disabled="backupStatus.status === 'running'">
        {{ backupStatus.status === 'running' ? '备份中...' : '立即备份' }}
      </button>
    </div>
    
    <!-- 备份历史 -->
    <div class="backup-history">
      <h2>备份历史</h2>
      <div v-if="backups.length === 0" class="no-data">暂无备份记录</div>
      <table v-else class="backup-table">
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
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

h2 {
  margin-top: 30px;
  margin-bottom: 15px;
  color: #555;
  border-bottom: 1px solid #ddd;
  padding-bottom: 5px;
}

.backup-status, .backup-config, .manual-backup, .backup-history {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.status-info p {
  margin: 10px 0;
  font-size: 16px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #218838;
}

.btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.backup-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.backup-table th,
.backup-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.backup-table th {
  background-color: #f2f2f2;
  font-weight: 600;
}

.backup-table tr:hover {
  background-color: #f5f5f5;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #999;
  font-style: italic;
}
</style>