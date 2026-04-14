<template>
  <div class="notification-container">
    <h1>通知中心</h1>
    
    <!-- 操作栏 -->
    <div class="action-bar">
      <button @click="markAllAsRead" class="btn btn-primary" :disabled="unreadCount === 0">
        标记所有为已读 ({{ unreadCount }})
      </button>
      <button @click="deleteAll" class="btn btn-danger">
        删除所有通知
      </button>
    </div>
    
    <!-- 通知列表 -->
    <div class="notification-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="notifications.length === 0" class="no-data">暂无通知</div>
      <div v-else>
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ 'unread': !notification.is_read }"
        >
          <div class="notification-header">
            <h3>{{ notification.title }}</h3>
            <div class="notification-meta">
              <span class="notification-type">{{ getTypeLabel(notification.notification_type) }}</span>
              <span class="notification-time">{{ formatDateTime(notification.created_at) }}</span>
            </div>
          </div>
          <div class="notification-content">
            {{ notification.content }}
          </div>
          <div class="notification-actions">
            <button 
              v-if="!notification.is_read"
              @click="markAsRead(notification.id)"
              class="btn btn-sm btn-primary"
            >
              标记为已读
            </button>
            <button 
              @click="deleteNotification(notification.id)"
              class="btn btn-sm btn-danger"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../utils/api'

const notifications = ref([])
const loading = ref(true)

// 计算未读通知数量
const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.is_read).length
})

// 格式化日期时间
const formatDateTime = (dateTime) => {
  const date = new Date(dateTime)
  return date.toLocaleString()
}

// 获取通知类型标签
const getTypeLabel = (type) => {
  const typeMap = {
    'system': '系统',
    'file': '文件',
    'share': '共享',
    'chat': '聊天',
    'backup': '备份'
  }
  return typeMap[type] || type
}

// 获取通知列表
const getNotifications = async () => {
  try {
    loading.value = true
    const response = await api.get('/notification/')
    notifications.value = response.data
  } catch (error) {
    console.error('获取通知失败:', error)
  } finally {
    loading.value = false
  }
}

// 标记为已读
const markAsRead = async (id) => {
  try {
    await api.put(`/notification/${id}`, { is_read: true })
    // 更新本地状态
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.is_read = true
    }
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

// 标记所有为已读
const markAllAsRead = async () => {
  try {
    await api.put('/notification/read-all')
    // 更新本地状态
    notifications.value.forEach(n => {
      n.is_read = true
    })
  } catch (error) {
    console.error('标记所有已读失败:', error)
  }
}

// 删除通知
const deleteNotification = async (id) => {
  if (!confirm('确定要删除这条通知吗？')) return
  
  try {
    await api.delete(`/notification/${id}`)
    // 更新本地状态
    notifications.value = notifications.value.filter(n => n.id !== id)
  } catch (error) {
    console.error('删除通知失败:', error)
  }
}

// 删除所有通知
const deleteAll = async () => {
  if (!confirm('确定要删除所有通知吗？')) return
  
  try {
    await api.delete('/notification/delete-all')
    // 清空本地状态
    notifications.value = []
  } catch (error) {
    console.error('删除所有通知失败:', error)
  }
}

// 页面加载时获取数据
onMounted(() => {
  getNotifications()
})
</script>

<style scoped>
.notification-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.action-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  justify-content: flex-end;
}

.notification-list {
  margin-top: 20px;
}

.notification-item {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.notification-item.unread {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.notification-item:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.notification-header h3 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.notification-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.notification-type {
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: #666;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.notification-content {
  margin-bottom: 15px;
  color: #555;
  line-height: 1.4;
}

.notification-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0069d9;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
  font-style: italic;
}
</style>