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
</script>

<template>
  <div class="chat-container">
    <h1>聊天</h1>
    
    <div class="card flex-1 mb-lg">
      <div class="messages-container" ref="messagesContainer">
        <div v-for="message in chatStore.messages" :key="message.id" class="message">
          <div class="message-header">
            <span class="message-username">{{ message.user?.username || '未知用户' }}</span>
            <span class="message-time">{{ new Date(message.created_at).toLocaleString() }}</span>
          </div>
          <div class="message-content">{{ message.content }}</div>
        </div>
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <h3>暂无消息</h3>
          <p>发送您的第一条消息</p>
        </div>
      </div>
    </div>
    
    <div class="flex gap-md">
      <input 
        type="text" 
        v-model="messageInput" 
        @keyup.enter="handleSendMessage" 
        placeholder="输入消息..." 
        class="form-input flex-1"
      />
      <button 
        @click="handleSendMessage" 
        :disabled="chatStore.loading" 
        class="btn btn-primary"
      >
        {{ chatStore.loading ? '发送中...' : '发送' }}
      </button>
    </div>
    
    <div v-if="error" class="error-message mt-md">
      {{ error }}
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  height: 80vh;
  display: flex;
  flex-direction: column;
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.message {
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-md);
  background-color: var(--background);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.message-username {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--text-light);
}

.message-content {
  font-size: var(--font-size-base);
  color: var(--text-primary);
  line-height: 1.5;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--background-light);
  border-radius: var(--radius-sm);
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--background-dark);
  border-radius: var(--radius-sm);
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--text-light);
}
</style>