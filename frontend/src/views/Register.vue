<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const email = ref('')
const nickname = ref('')
const error = ref('')

async function handleRegister() {
  error.value = ''
  try {
    await authStore.register(username.value, password.value, email.value, nickname.value)
    router.push('/login')
  } catch (err) {
    error.value = authStore.error || '注册失败'
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1 class="auth-title">注册</h1>
      
      <form @submit.prevent="handleRegister" class="auth-form">
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
          <label for="nickname" class="form-label">昵称</label>
          <input 
            type="text" 
            id="nickname" 
            v-model="nickname" 
            class="form-input"
            placeholder="请输入昵称（可选）"
          />
        </div>
        
        <div class="form-group">
          <label for="email" class="form-label">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            class="form-input"
            required 
            placeholder="请输入邮箱"
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
          {{ authStore.loading ? '注册中...' : '注册' }}
        </button>
        
        <p class="auth-link">
          已有账号？ <router-link to="/login">立即登录</router-link>
        </p>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>