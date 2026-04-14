<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  error.value = ''
  try {
    await authStore.login(username.value, password.value)
    router.push('/files')
  } catch (err) {
    error.value = authStore.error || '登录失败'
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/files')
  }
})
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">登录</h1>
      
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            class="form-input"
            required 
            placeholder="请输入用户名"
          />
        </div>
        
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            class="form-input"
            required 
            placeholder="请输入密码"
          />
        </div>
        
        <button type="submit" :disabled="authStore.loading" class="btn btn-primary w-full">
          {{ authStore.loading ? '登录中...' : '登录' }}
        </button>
        
        <p class="auth-link">
          还没有账号？ <router-link to="/register">立即注册</router-link>
        </p>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>
