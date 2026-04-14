<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

const navLinks = [
  { name: '文件管理', path: '/files', icon: '📁' },
  { name: '文件共享', path: '/share', icon: '🔗' },
  { name: '聊天', path: '/chat', icon: '💬' },
  { name: '多媒体', path: '/multimedia', icon: '🎵' },
  { name: '备份', path: '/backup', icon: '💾' },
  { name: '通知', path: '/notification', icon: '🔔' }
]

const currentRoute = computed(() => route.path)

const logout = async () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar">
    <div class="navbar-container">
      <a href="/" class="navbar-brand">
        <span>📁</span>
        <span>LanFileHub</span>
      </a>
      
      <div v-if="isAuthenticated" class="navbar-menu">
        <a 
          v-for="link in navLinks" 
          :key="link.path"
          :href="link.path"
          class="navbar-link"
          :class="{ active: currentRoute === link.path }"
        >
          <span>{{ link.icon }}</span>
          <span>{{ link.name }}</span>
        </a>
        
        <button @click="logout" class="btn btn-secondary btn-sm">
          退出登录
        </button>
      </div>
    </div>
  </nav>
</template>
