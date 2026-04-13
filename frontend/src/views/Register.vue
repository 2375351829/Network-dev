<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const email = ref('')
const error = ref('')

async function handleRegister() {
  error.value = ''
  try {
    await authStore.register(username.value, password.value, email.value)
    router.push('/login')
  } catch (err) {
    error.value = authStore.error || '注册失败'
  }
}
</script>

<template>
  <div class="register-container">
    <h1>注册</h1>
    <form @submit.prevent="handleRegister" class="register-form">
      <div class="form-group">
        <label for="username">用户名</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          required 
          placeholder="请输入用户名"
        />
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          required 
          placeholder="请输入邮箱"
        />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          required 
          placeholder="请输入密码"
        />
      </div>
      <button type="submit" :disabled="authStore.loading" class="register-button">
        {{ authStore.loading ? '注册中...' : '注册' }}
      </button>
      <p class="login-link">
        已有账号？ <router-link to="/login">立即登录</router-link>
      </p>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
  </div>
</template>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

input:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.register-button {
  padding: 12px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-button:hover {
  background-color: #35495e;
}

.register-button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  font-size: 14px;
  margin-top: 10px;
}

.login-link a {
  color: #42b883;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
}
</style>