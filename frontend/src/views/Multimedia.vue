<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

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
    const musicResponse = await axios.get('/api/multimedia/list?media_type=audio')
    musicFiles.value = musicResponse.data
    
    const videoResponse = await axios.get('/api/multimedia/list?media_type=video')
    videoFiles.value = videoResponse.data
  } catch (error) {
    console.error('获取媒体文件失败:', error)
  }
}

// 获取歌单列表
async function fetchPlaylists() {
  try {
    const response = await axios.get('/api/multimedia/playlists')
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
    await axios.post('/api/multimedia/upload', formData, {
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
    await axios.post('/api/multimedia/playlists', {
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
    const response = await axios.get(`/api/multimedia/playlists/${playlist.id}`)
    selectedPlaylist.value = response.data
  } catch (error) {
    console.error('获取歌单详情失败:', error)
  }
}

// 添加歌曲到歌单
async function addToPlaylist(playlistId, fileId) {
  try {
    await axios.post(`/api/multimedia/playlists/${playlistId}/items`, {
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
    await axios.delete(`/api/multimedia/playlists/${playlistId}/items/${itemId}`)
    
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
    const response = await axios.get(`/api/multimedia/video-progress/${file.id}`)
    videoProgress.value = response.data.progress
  } catch (error) {
    console.error('获取视频进度失败:', error)
  }
}

// 更新视频进度
async function updateVideoProgress() {
  if (!currentVideo.value) return
  
  try {
    await axios.post(`/api/multimedia/video-progress/${currentVideo.value.id}`, {
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
    <div class="tabs">
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
    <div class="action-buttons">
      <button @click="showUploadModal = true" class="btn-primary">
        上传媒体
      </button>
      <button v-if="activeTab === 'playlists'" @click="showCreatePlaylistModal = true" class="btn-secondary">
        创建歌单
      </button>
    </div>
    
    <!-- 音乐标签页 -->
    <div v-if="activeTab === 'music'" class="media-list">
      <h2>音乐列表</h2>
      <div class="file-grid">
        <div v-for="file in musicFiles" :key="file.id" class="file-card">
          <div class="file-info">
            <h3>{{ file.filename }}</h3>
            <p>{{ (file.file_size).toFixed(2) }} MB</p>
          </div>
          <div class="file-actions">
            <button @click="playMusic(file)" class="btn-play">
              播放
            </button>
            <button @click="openAddToPlaylistModal(file)" class="btn-add">
              添加到歌单
            </button>
          </div>
        </div>
      </div>
      
      <!-- 当前播放 -->
      <div v-if="currentPlaying" class="now-playing">
        <h3>当前播放: {{ currentPlaying.filename }}</h3>
        <!-- 实际项目中可以添加音频播放器控件 -->
      </div>
    </div>
    
    <!-- 视频标签页 -->
    <div v-if="activeTab === 'video'" class="media-list">
      <h2>视频列表</h2>
      <div class="file-grid">
        <div v-for="file in videoFiles" :key="file.id" class="file-card">
          <div class="file-info">
            <h3>{{ file.filename }}</h3>
            <p>{{ (file.file_size).toFixed(2) }} MB</p>
          </div>
          <div class="file-actions">
            <button @click="playVideo(file)" class="btn-play">
              播放
            </button>
            <button @click="openAddToPlaylistModal(file)" class="btn-add">
              添加到歌单
            </button>
          </div>
        </div>
      </div>
      
      <!-- 视频播放器 -->
      <div v-if="currentVideo" class="video-player">
        <h3>{{ currentVideo.filename }}</h3>
        <video 
          controls 
          @timeupdate="videoProgress = $event.target.currentTime" 
          @ended="updateVideoProgress"
          :src="`/api/files/download/${currentVideo.id}`"
          :currentTime="videoProgress"
          style="width: 100%; max-width: 800px;"
        ></video>
        <div class="progress-info">
          <p>当前进度: {{ videoProgress.toFixed(2) }} 秒</p>
          <button @click="updateVideoProgress" class="btn-secondary">
            保存进度
          </button>
        </div>
      </div>
    </div>
    
    <!-- 歌单标签页 -->
    <div v-if="activeTab === 'playlists'" class="playlists-container">
      <h2>歌单列表</h2>
      <div class="playlist-grid">
        <div v-for="playlist in playlists" :key="playlist.id" class="playlist-card">
          <h3 @click="viewPlaylist(playlist)">{{ playlist.name }}</h3>
          <p>{{ playlist.description || '无描述' }}</p>
          <p>{{ playlist.created_at }}</p>
        </div>
      </div>
      
      <!-- 歌单详情 -->
      <div v-if="selectedPlaylist" class="playlist-detail">
        <h3>{{ selectedPlaylist.name }}</h3>
        <p>{{ selectedPlaylist.description || '无描述' }}</p>
        <h4>歌单内容</h4>
        <ul class="playlist-items">
          <li v-for="item in selectedPlaylist.items" :key="item.id">
            {{ item.filename }}
            <button @click="removeFromPlaylist(selectedPlaylist.id, item.id)" class="btn-remove">
              移除
            </button>
          </li>
        </ul>
      </div>
    </div>
    
    <!-- 上传模态框 -->
    <div v-if="showUploadModal" class="modal">
      <div class="modal-content">
        <h3>上传媒体文件</h3>
        <input type="file" @change="uploadFile = $event.target.files[0]" accept="audio/*,video/*">
        <div class="modal-actions">
          <button @click="uploadMedia" class="btn-primary">
            上传
          </button>
          <button @click="showUploadModal = false" class="btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 创建歌单模态框 -->
    <div v-if="showCreatePlaylistModal" class="modal">
      <div class="modal-content">
        <h3>创建歌单</h3>
        <input type="text" v-model="playlistName" placeholder="歌单名称">
        <textarea v-model="playlistDescription" placeholder="歌单描述"></textarea>
        <div class="modal-actions">
          <button @click="createPlaylist" class="btn-primary">
            创建
          </button>
          <button @click="showCreatePlaylistModal = false" class="btn-secondary">
            取消
          </button>
        </div>
      </div>
    </div>
    
    <!-- 添加到歌单模态框 -->
    <div v-if="showAddToPlaylistModal" class="modal">
      <div class="modal-content">
        <h3>添加到歌单</h3>
        <p>选择要添加到的歌单:</p>
        <div class="playlist-selector">
          <div v-for="playlist in playlists" :key="playlist.id" class="playlist-option">
            <button @click="addToPlaylist(playlist.id, selectedFileForPlaylist.id)" class="btn-secondary">
              {{ playlist.name }}
            </button>
          </div>
        </div>
        <div class="modal-actions">
          <button @click="showAddToPlaylistModal = false" class="btn-secondary">
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
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 30px;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  border-bottom: 3px solid transparent;
}

.tabs button.active {
  border-bottom-color: #4CAF50;
  color: #4CAF50;
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary {
  background-color: #f1f1f1;
  color: #333;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-play {
  background-color: #2196F3;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
}

.btn-add {
  background-color: #ff9800;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-remove {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

.media-list {
  margin-top: 20px;
}

.file-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.file-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
}

.file-info {
  margin-bottom: 10px;
}

.file-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.file-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.file-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.now-playing {
  margin-top: 30px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f0f8ff;
}

.video-player {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.progress-info {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.playlists-container {
  margin-top: 20px;
}

.playlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.playlist-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  background-color: #f9f9f9;
  cursor: pointer;
}

.playlist-card:hover {
  background-color: #f0f0f0;
}

.playlist-detail {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.playlist-items {
  list-style: none;
  padding: 0;
  margin: 10px 0 0 0;
}

.playlist-items li {
  padding: 10px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
}

.modal-content input,
.modal-content textarea {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.playlist-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 10px 0;
}

.playlist-option button {
  width: 100%;
  text-align: left;
}
</style>