<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const users = ref([])
const loading = ref(true)
const error = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const selectedUser = ref(null)
const selectedUsers = ref([])
const showUserDetail = ref(false)

// 表单数据
const newUser = ref({
  username: '',
  email: '',
  password: '',
  nickname: ''
})

const editUser = ref({
  id: '',
  username: '',
  email: '',
  nickname: '',
  is_admin: false,
  is_active: true
})

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

// 添加用户
async function addUser() {
  if (!newUser.value.username || !newUser.value.email || !newUser.value.password) {
    error.value = '请填写完整信息'
    return
  }
  
  try {
    // 使用注册功能添加用户
    await authStore.register(newUser.value.username, newUser.value.password, newUser.value.email, newUser.value.nickname)
    await fetchUsers()
    showAddModal.value = false
    newUser.value = { username: '', email: '', password: '', nickname: '' }
    error.value = ''
  } catch (err) {
    error.value = '添加用户失败'
    console.error('添加用户失败:', err)
  }
}

// 编辑用户
async function updateUser() {
  if (!editUser.value.username || !editUser.value.email) {
    error.value = '请填写完整信息'
    return
  }
  
  try {
    await api.put(`/users/${editUser.value.id}`, editUser.value)
    await fetchUsers()
    showEditModal.value = false
    editUser.value = { id: '', username: '', email: '', nickname: '', is_admin: false, is_active: true }
    error.value = ''
  } catch (err) {
    error.value = '更新用户失败'
    console.error('更新用户失败:', err)
  }
}

// 打开编辑模态框
function openEditModal(user) {
  editUser.value = { 
    ...user,
    nickname: user.nickname || user.username,
    is_admin: user.is_admin || false,
    is_active: user.is_active !== undefined ? user.is_active : true
  }
  showEditModal.value = true
}

// 打开用户详情
function openUserDetail(user) {
  selectedUser.value = user
  showUserDetail.value = true
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

// 批量删除用户
async function deleteSelectedUsers() {
  if (selectedUsers.value.length === 0) {
    alert('请选择要删除的用户')
    return
  }
  
  if (!confirm(`确定要删除选中的 ${selectedUsers.value.length} 个用户吗？`)) return
  
  try {
    await Promise.all(selectedUsers.value.map(userId => api.delete(`/users/${userId}`)))
    await fetchUsers()
    selectedUsers.value = []
  } catch (err) {
    error.value = '批量删除用户失败'
    console.error('批量删除用户失败:', err)
  }
}

// 导出用户信息
function exportUsers() {
  const csvContent = users.value.map(user => 
    `${user.id},${user.username},${user.nickname || user.username},${user.email},${user.is_admin ? '管理员' : '普通用户'},${user.created_at}`
  ).join('\n')
  
  const header = 'ID,用户名,昵称,邮箱,角色,创建时间\n'
  const blob = new Blob([header + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.setAttribute('href', url)
  link.setAttribute('download', 'users.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 切换用户选择
function toggleUserSelection(userId) {
  const index = selectedUsers.value.indexOf(userId)
  if (index === -1) {
    selectedUsers.value.push(userId)
  } else {
    selectedUsers.value.splice(index, 1)
  }
}

// 全选/取消全选
function toggleSelectAll() {
  if (selectedUsers.value.length === users.value.length) {
    selectedUsers.value = []
  } else {
    selectedUsers.value = users.value.map(user => user.id)
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
    
    <div class="card mb-lg">
      <div class="flex justify-between items-center mb-md">
        <h2>用户列表</h2>
        <div class="flex gap-sm">
          <button @click="showAddModal = true" class="btn btn-primary">
            新增用户
          </button>
          <button v-if="selectedUsers.length > 0" @click="deleteSelectedUsers" class="btn btn-danger">
            批量删除 ({{ selectedUsers.length }})
          </button>
          <button @click="exportUsers" class="btn btn-secondary">
            导出用户
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">加载中...</div>
      
      <table v-else class="w-full">
        <thead>
          <tr>
            <th>
              <input 
                type="checkbox" 
                :checked="selectedUsers.length === users.length && users.length > 0"
                @change="toggleSelectAll"
              />
            </th>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>
              <input 
                type="checkbox" 
                :checked="selectedUsers.includes(user.id)"
                @change="toggleUserSelection(user.id)"
              />
            </td>
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.nickname || user.username }}</td>
            <td>{{ user.email }}</td>
            <td>
              <span class="tag" :class="user.is_admin ? 'tag-primary' : 'tag-secondary'">
                {{ user.is_admin ? '管理员' : '普通用户' }}
              </span>
            </td>
            <td>{{ new Date(user.created_at).toLocaleString() }}</td>
            <td class="flex gap-sm">
              <button @click="openUserDetail(user)" class="btn btn-sm" style="background-color: var(--secondary); color: white;">
                查看
              </button>
              <button @click="openEditModal(user)" class="btn btn-sm btn-secondary">
                编辑
              </button>
              <button @click="deleteUser(user.id)" class="btn btn-sm btn-danger">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="users.length === 0 && !loading" class="empty-state">
        <h3>暂无用户</h3>
        <p>新增用户开始管理</p>
      </div>
    </div>
    
    <!-- 新增用户模态框 -->
    <div v-if="showAddModal" class="modal">
      <div class="modal-content">
        <h3 class="mb-md">新增用户</h3>
        <div class="form-group mb-md">
          <label for="new-username" class="form-label">用户名</label>
          <input id="new-username" v-model="newUser.username" type="text" class="form-input" placeholder="请输入用户名" />
        </div>
        <div class="form-group mb-md">
          <label for="new-nickname" class="form-label">昵称</label>
          <input id="new-nickname" v-model="newUser.nickname" type="text" class="form-input" placeholder="请输入昵称（可选）" />
        </div>
        <div class="form-group mb-md">
          <label for="new-email" class="form-label">邮箱</label>
          <input id="new-email" v-model="newUser.email" type="email" class="form-input" placeholder="请输入邮箱" />
        </div>
        <div class="form-group mb-md">
          <label for="new-password" class="form-label">密码</label>
          <input id="new-password" v-model="newUser.password" type="password" class="form-input" placeholder="请输入密码" />
        </div>
        <div class="flex justify-end gap-md">
          <button @click="addUser" class="btn btn-primary">
            保存
          </button>
          <button @click="showAddModal = false" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 编辑用户模态框 -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <h3 class="mb-md">编辑用户</h3>
        <div class="form-group mb-md">
          <label for="edit-username" class="form-label">用户名</label>
          <input id="edit-username" v-model="editUser.username" type="text" class="form-input" placeholder="请输入用户名" />
        </div>
        <div class="form-group mb-md">
          <label for="edit-nickname" class="form-label">昵称</label>
          <input id="edit-nickname" v-model="editUser.nickname" type="text" class="form-input" placeholder="请输入昵称" />
        </div>
        <div class="form-group mb-md">
          <label for="edit-email" class="form-label">邮箱</label>
          <input id="edit-email" v-model="editUser.email" type="email" class="form-input" placeholder="请输入邮箱" />
        </div>
        <div class="form-group mb-md">
          <label for="edit-role" class="form-label">用户角色</label>
          <select id="edit-role" v-model="editUser.is_admin" class="form-input">
            <option :value="false">普通用户</option>
            <option :value="true">管理员</option>
          </select>
        </div>
        <div class="form-group mb-md">
          <label for="edit-active" class="form-label">账户状态</label>
          <select id="edit-active" v-model="editUser.is_active" class="form-input">
            <option :value="true">激活</option>
            <option :value="false">禁用</option>
          </select>
        </div>
        <div class="flex justify-end gap-md">
          <button @click="updateUser" class="btn btn-primary">
            保存
          </button>
          <button @click="showEditModal = false" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 用户详情模态框 -->
    <div v-if="showUserDetail && selectedUser" class="modal">
      <div class="modal-content">
        <h3 class="mb-md">用户详情</h3>
        <div class="mb-md">
          <p class="mb-sm"><strong>ID:</strong> {{ selectedUser.id }}</p>
          <p class="mb-sm"><strong>用户名:</strong> {{ selectedUser.username }}</p>
          <p class="mb-sm"><strong>昵称:</strong> {{ selectedUser.nickname || selectedUser.username }}</p>
          <p class="mb-sm"><strong>邮箱:</strong> {{ selectedUser.email }}</p>
          <p class="mb-sm"><strong>角色:</strong> 
            <span class="tag" :class="selectedUser.is_admin ? 'tag-primary' : 'tag-secondary'">
              {{ selectedUser.is_admin ? '管理员' : '普通用户' }}
            </span>
          </p>
          <p class="mb-sm"><strong>账户状态:</strong> 
            <span class="tag" :class="selectedUser.is_active ? 'tag-primary' : 'tag-danger'">
              {{ selectedUser.is_active ? '激活' : '禁用' }}
            </span>
          </p>
          <p class="mb-sm"><strong>创建时间:</strong> {{ new Date(selectedUser.created_at).toLocaleString() }}</p>
        </div>
        <div class="flex justify-end">
          <button @click="showUserDetail = false" class="btn btn-secondary">
            关闭
          </button>
        </div>
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