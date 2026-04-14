<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'

const router = useRouter()
const users = ref([])
const loading = ref(true)
const error = ref('')

// 获取用户列表
async function fetchUsers() {
  try {
    loading.value = true
    const response = await api.get('/users')
    users.value = response.data
  } catch (err) {
    error.value = '获取用户列表失败'
    console.error('获取用户列表失败:', err)
  } finally {
    loading.value = false
  }
}

// 删除用户
async function deleteUser(userId) {
  if (!confirm('确定要删除这个用户吗？')) return
  
  try {
    await api.delete(`/users/${userId}`)
    users.value = users.value.filter(user => user.id !== userId)
  } catch (err) {
    error.value = '删除用户失败'
    console.error('删除用户失败:', err)
  }
}

// 页面加载时获取用户列表
onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="users-container">
    <h1>用户管理</h1>
    
    <div class="card">
      <h2 class="mb-md">用户列表</h2>
      
      <div v-if="loading" class="loading">加载中...</div>
      
      <table v-else class="w-full">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ new Date(user.created_at).toLocaleString() }}</td>
            <td>
              <button @click="deleteUser(user.id)" class="btn btn-sm btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="users.length === 0 && !loading" class="empty-state">
        <h3>暂无用户</h3>
        <p>注册新用户开始管理</p>
      </div>
    </div>
    
    <div v-if="error" class="error-message mt-md">
      {{ error }}
    </div>
  </div>
</template>

<style scoped>
.users-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>