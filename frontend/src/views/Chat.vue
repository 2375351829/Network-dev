<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../stores/chat'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const chatStore = useChatStore()
const authStore = useAuthStore()

const messageInput = ref('')
const messagesContainer = ref(null)
const error = ref('')

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  await chatStore.getMessages()
  scrollToBottom()
})

async function handleSendMessage() {
  if (!messageInput.value.trim()) return
  
  try {
    await chatStore.sendMessage(messageInput.value)
    messageInput.value = ''
    await nextTick()
    scrollToBottom()
  } catch (err) {
    error.value = chatStore.error || '发送消息失败'
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="chat-container">
    <header class="chat-header">
      <h1>聊天</h1>
      <div class="header-actions">
        <router-link to="/files" class="nav-link">文件管理</router-link>
        <router-link to="/share" class="nav-link">共享设置</router-link>
        <button @click="logout" class="logout-button">退出登录</button>
      </div>
    </header>
    
    <div class="messages-container" ref="messagesContainer">
      <div v-for="message in chatStore.messages" :key="message.id" class="message">
        <div class="message-header">
          <span class="message-username">{{ message.user.username }}</span>
          <span class="message-time">{{ new Date(message.created_at).toLocaleString() }}</span>
        </div>
        <div class="message-content">{{ message.content }}</div>
      </div>
      <div v-if="chatStore.messages.length === 0" class="empty-message">暂无消息</div>
    </div>
    
    <div class="message-input-section">
      <input 
        type="text" 
        v-model="messageInput" 
        @keyup.enter="handleSendMessage" 
        placeholder="输入消息..." 
        class="message-input"
      />
      <button 
        @click="handleSendMessage" 
        :disabled="chatStore.loading" 
        class="send-button"
      >
        {{ chatStore.loading ? '发送中...' : '发送' }}
      </button>
    </div>
    
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  height: 80vh;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}

.chat-header h1 {
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

.messages-container {
  flex: 1;
  overflow-y: auto;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message {
  margin-bottom: 15px;
  padding: 10px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.message-username {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: #7f8c8d;
}

.message-content {
  font-size: 16px;
  color: #333;
  line-height: 1.5;
}

.empty-message {
  text-align: center;
  color: #7f8c8d;
  padding: 40px;
  font-size: 16px;
}

.message-input-section {
  display: flex;
  gap: 10px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  resize: none;
}

.message-input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.send-button {
  padding: 12px 24px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.send-button:hover {
  background-color: #35495e;
}

.send-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
  padding: 10px;
  background-color: #fadbd8;
  border-radius: 4px;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>