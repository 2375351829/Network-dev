<template>
  <div class="notification-container">
    <h1>通知中心</h1>
    
    <!-- 操作栏 -->
    <div class="flex justify-end gap-md mb-lg">
      <button @click="markAllAsRead" class="btn btn-primary" :disabled="unreadCount === 0">
        标记所有为已读 ({{ unreadCount }})
      </button>
      <button @click="deleteAll" class="btn btn-danger">
        删除所有通知
      </button>
    </div>
    
    <!-- 通知列表 -->
    <div class="space-y-md">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="notifications.length === 0" class="empty-state">
        <h3>暂无通知</h3>
        <p>当有新的系统消息时会显示在这里</p>
      </div>
      <div v-else>
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="card transition-all hover:shadow-lg"
          :class="{ 'unread': !notification.is_read }"
        >
          <div class="notification-header flex justify-between items-start mb-md">
            <h3 class="text-lg font-semibold">{{ notification.title }}</h3>
            <div class="notification-meta flex flex-col items-end gap-xs">
              <span class="tag tag-secondary">{{ getTypeLabel(notification.notification_type) }}</span>
              <span class="text-light text-sm">{{ formatDateTime(notification.created_at) }}</span>
            </div>
          </div>
          <div class="notification-content mb-md text-secondary">
            {{ notification.content }}
          </div>
          <div class="flex justify-end gap-sm">
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
}

.notification-item.unread {
  border-left: 4px solid var(--secondary);
  background-color: rgba(33, 150, 243, 0.05);
}

.space-y-md > * + * {
  margin-top: var(--spacing-md);
}

.gap-xs {
  gap: var(--spacing-xs);
}

.text-lg {
  font-size: var(--font-size-lg);
}

.font-semibold {
  font-weight: 600;
}

.transition-all {
  transition: all var(--transition-normal);
}

.hover\:shadow-lg:hover {
  box-shadow: var(--shadow-lg);
}
</style>