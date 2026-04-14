<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'

// 状态管理
const activeTab = ref('music') // music, video, playlists
const musicFiles = ref([])
const videoFiles = ref([])
const playlists = ref([])
const selectedPlaylist = ref(null)
const currentPlaying = ref(null)
const currentVideo = ref(null)
const videoProgress = ref(0)
const showUploadModal = ref(false)
const showCreatePlaylistModal = ref(false)
const showAddToPlaylistModal = ref(false)
const selectedFileForPlaylist = ref(null)

// 表单数据
const uploadFile = ref(null)
const playlistName = ref('')
const playlistDescription = ref('')

// 初始化数据
onMounted(() => {
  fetchMediaFiles()
  fetchPlaylists()
})

// 获取媒体文件列表
async function fetchMediaFiles() {
  try {
    const musicResponse = await api.get('/multimedia/list?media_type=audio')
    musicFiles.value = musicResponse.data
    
    const videoResponse = await api.get('/multimedia/list?media_type=video')
    videoFiles.value = videoResponse.data
  } catch (error) {
    console.error('获取媒体文件失败:', error)
  }
}

// 获取歌单列表
async function fetchPlaylists() {
  try {
    const response = await api.get('/multimedia/playlists')
    playlists.value = response.data
  } catch (error) {
    console.error('获取歌单失败:', error)
  }
}

// 上传媒体文件
async function uploadMedia() {
  if (!uploadFile.value) return
  
  const formData = new FormData()
  formData.append('file', uploadFile.value)
  
  try {
    await api.post('/multimedia/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // 重新获取文件列表
    fetchMediaFiles()
    showUploadModal.value = false
    uploadFile.value = null
  } catch (error) {
    console.error('上传失败:', error)
  }
}

// 创建歌单
async function createPlaylist() {
  if (!playlistName.value) return
  
  try {
    await api.post('/multimedia/playlists', {
      name: playlistName.value,
      description: playlistDescription.value
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    // 重新获取歌单列表
    fetchPlaylists()
    showCreatePlaylistModal.value = false
    playlistName.value = ''
    playlistDescription.value = ''
  } catch (error) {
    console.error('创建歌单失败:', error)
  }
}

// 查看歌单详情
async function viewPlaylist(playlist) {
  try {
    const response = await api.get(`/multimedia/playlists/${playlist.id}`)
    selectedPlaylist.value = response.data
  } catch (error) {
    console.error('获取歌单详情失败:', error)
  }
}

// 添加歌曲到歌单
async function addToPlaylist(playlistId, fileId) {
  try {
    await api.post(`/multimedia/playlists/${playlistId}/items`, {
      file_id: fileId
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    // 重新获取歌单详情
    if (selectedPlaylist.value && selectedPlaylist.value.id === playlistId) {
      viewPlaylist(selectedPlaylist.value)
    }
    showAddToPlaylistModal.value = false
  } catch (error) {
    console.error('添加到歌单失败:', error)
  }
}

// 从歌单中移除歌曲
async function removeFromPlaylist(playlistId, itemId) {
  try {
    await api.delete(`/multimedia/playlists/${playlistId}/items/${itemId}`)
    
    // 重新获取歌单详情
    if (selectedPlaylist.value && selectedPlaylist.value.id === playlistId) {
      viewPlaylist(selectedPlaylist.value)
    }
  } catch (error) {
    console.error('从歌单中移除失败:', error)
  }
}

// 播放音乐
function playMusic(file) {
  currentPlaying.value = file
  // 实际项目中可以使用音频播放器库
  console.log('播放音乐:', file.filename)
}

// 播放视频
async function playVideo(file) {
  currentVideo.value = file
  
  // 获取视频进度
  try {
    const response = await api.get(`/multimedia/video-progress/${file.id}`)
    videoProgress.value = response.data.progress
  } catch (error) {
    console.error('获取视频进度失败:', error)
  }
}

// 更新视频进度
async function updateVideoProgress() {
  if (!currentVideo.value) return
  
  try {
    await api.post(`/multimedia/video-progress/${currentVideo.value.id}`, {
      progress: videoProgress.value
    }, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  } catch (error) {
    console.error('更新视频进度失败:', error)
  }
}

// 打开添加到歌单模态框
function openAddToPlaylistModal(file) {
  selectedFileForPlaylist.value = file
  showAddToPlaylistModal.value = true
}
</script>

<template>
  <div class="multimedia-container">
    <h1>多媒体娱乐</h1>
    
    <!-- 标签页 -->
    <div class="tabs mb-lg">
      <button 
        :class="{ active: activeTab === 'music' }" 
        @click="activeTab = 'music'"
      >
        音乐
      </button>
      <button 
        :class="{ active: activeTab === 'video' }" 
        @click="activeTab = 'video'"
      >
        视频
      </button>
      <button 
        :class="{ active: activeTab === 'playlists' }" 
        @click="activeTab = 'playlists'"
      >
        歌单
      </button>
    </div>
    
    <!-- 操作按钮 -->
    <div class="flex gap-md mb-lg">
      <button @click="showUploadModal = true" class="btn btn-primary">
        上传媒体
      </button>
      <button v-if="activeTab === 'playlists'" @click="showCreatePlaylistModal = true" class="btn btn-secondary">
        创建歌单
      </button>
    </div>
    
    <!-- 音乐标签页 -->
    <div v-if="activeTab === 'music'">
      <h2 class="mb-md">音乐列表</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
        <div v-for="file in musicFiles" :key="file.id" class="card">
          <div class="file-info mb-md">
            <h3 class="mb-sm">{{ file.filename }}</h3>
            <p class="text-secondary">{{ (file.file_size).toFixed(2) }} MB</p>
          </div>
          <div class="flex gap-sm">
            <button @click="playMusic(file)" class="btn btn-sm" style="background-color: var(--secondary); color: white;">
              播放
            </button>
            <button @click="openAddToPlaylistModal(file)" class="btn btn-sm" style="background-color: var(--accent); color: white;">
              添加到歌单
            </button>
          </div>
        </div>
      </div>
      
      <!-- 当前播放 -->
      <div v-if="currentPlaying" class="card mt-lg">
        <h3>当前播放: {{ currentPlaying.filename }}</h3>
        <!-- 实际项目中可以添加音频播放器控件 -->
      </div>
    </div>
    
    <!-- 视频标签页 -->
    <div v-if="activeTab === 'video'">
      <h2 class="mb-md">视频列表</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
        <div v-for="file in videoFiles" :key="file.id" class="card">
          <div class="file-info mb-md">
            <h3 class="mb-sm">{{ file.filename }}</h3>
            <p class="text-secondary">{{ (file.file_size).toFixed(2) }} MB</p>
          </div>
          <div class="flex gap-sm">
            <button @click="playVideo(file)" class="btn btn-sm" style="background-color: var(--secondary); color: white;">
              播放
            </button>
            <button @click="openAddToPlaylistModal(file)" class="btn btn-sm" style="background-color: var(--accent); color: white;">
              添加到歌单
            </button>
          </div>
        </div>
      </div>
      
      <!-- 视频播放器 -->
      <div v-if="currentVideo" class="card mt-lg p-lg">
        <h3 class="mb-md">{{ currentVideo.filename }}</h3>
        <video 
          controls 
          @timeupdate="videoProgress = $event.target.currentTime" 
          @ended="updateVideoProgress"
          :src="`/api/files/download/${currentVideo.id}`"
          :currentTime="videoProgress"
          style="width: 100%; max-width: 800px; border-radius: var(--radius-md);"
        ></video>
        <div class="flex justify-between items-center mt-md">
          <p class="text-secondary">当前进度: {{ videoProgress.toFixed(2) }} 秒</p>
          <button @click="updateVideoProgress" class="btn btn-sm btn-secondary">
            保存进度
          </button>
        </div>
      </div>
    </div>
    
    <!-- 歌单标签页 -->
    <div v-if="activeTab === 'playlists'">
      <h2 class="mb-md">歌单列表</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
        <div v-for="playlist in playlists" :key="playlist.id" class="card cursor-pointer hover:shadow-lg transition-shadow" @click="viewPlaylist(playlist)">
          <h3 class="mb-sm">{{ playlist.name }}</h3>
          <p class="text-secondary mb-sm">{{ playlist.description || '无描述' }}</p>
          <p class="text-light text-sm">{{ playlist.created_at }}</p>
        </div>
      </div>
      
      <!-- 歌单详情 -->
      <div v-if="selectedPlaylist" class="card mt-lg">
        <h3 class="mb-sm">{{ selectedPlaylist.name }}</h3>
        <p class="text-secondary mb-md">{{ selectedPlaylist.description || '无描述' }}</p>
        <h4 class="mb-md">歌单内容</h4>
        <ul class="space-y-sm">
          <li v-for="item in selectedPlaylist.items" :key="item.id" class="flex justify-between items-center p-sm border-b border-border">
            {{ item.filename }}
            <button @click="removeFromPlaylist(selectedPlaylist.id, item.id)" class="btn btn-sm btn-danger">
              移除
            </button>
          </li>
        </ul>
      </div>
    </div>
    
    <!-- 上传模态框 -->
    <div v-if="showUploadModal" class="modal">
      <div class="modal-content">
        <h3 class="mb-md">上传媒体文件</h3>
        <input type="file" @change="uploadFile = $event.target.files[0]" accept="audio/*,video/*" class="form-input mb-md">
        <div class="flex justify-end gap-md">
          <button @click="uploadMedia" class="btn btn-primary">
            上传
          </button>
          <button @click="showUploadModal = false" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 创建歌单模态框 -->
    <div v-if="showCreatePlaylistModal" class="modal">
      <div class="modal-content">
        <h3 class="mb-md">创建歌单</h3>
        <input type="text" v-model="playlistName" placeholder="歌单名称" class="form-input mb-md">
        <textarea v-model="playlistDescription" placeholder="歌单描述" class="form-input mb-md"></textarea>
        <div class="flex justify-end gap-md">
          <button @click="createPlaylist" class="btn btn-primary">
            创建
          </button>
          <button @click="showCreatePlaylistModal = false" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加到歌单模态框 -->
    <div v-if="showAddToPlaylistModal" class="modal">
      <div class="modal-content">
        <h3 class="mb-md">添加到歌单</h3>
        <p class="mb-md">选择要添加到的歌单:</p>
        <div class="space-y-sm mb-md">
          <button 
            v-for="playlist in playlists" 
            :key="playlist.id" 
            @click="addToPlaylist(playlist.id, selectedFileForPlaylist.id)" 
            class="btn btn-secondary w-full text-left"
          >
            {{ playlist.name }}
          </button>
        </div>
        <div class="flex justify-end">
          <button @click="showAddToPlaylistModal = false" class="btn btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.multimedia-container {
  max-width: 1200px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
}

.tabs button {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  background: none;
  cursor: pointer;
  font-size: var(--font-size-base);
  border-bottom: 3px solid transparent;
  transition: all var(--transition-fast);
}

.tabs button.active {
  border-bottom-color: var(--primary);
  color: var(--primary);
  font-weight: 500;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, 1fr);
}

@media (min-width: 768px) {
  .md\:grid-cols-2 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-3 {
    grid-template-columns: repeat(3, 1fr);
  }
}

.space-y-sm > * + * {
  margin-top: var(--spacing-sm);
}

.cursor-pointer {
  cursor: pointer;
}

.hover\:shadow-lg:hover {
  box-shadow: var(--shadow-lg);
}

.transition-shadow {
  transition: box-shadow var(--transition-normal);
}
</style>