<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>SyncAI</h1>
          <span>互動問答平台</span>
        </div>
        <div class="nav-actions">
          <button class="btn btn-outline" @click="openModal('join')">加入會議</button>
          <button class="btn btn-primary" @click="openModal('create')">建立會議室</button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <section class="hero">
        <div class="hero-content">
          <h2>讓每個聲音都被聽見</h2>
          <p>建立互動會議室，讓參與者匿名提問、投票，讓會議更有參與感</p>
          <div class="hero-actions">
            <button class="btn btn-primary btn-large" @click="openModal('create')">
              <span>➕</span>
              建立新會議室
            </button>
          </div>
        </div>
      </section>
      <section class="features">
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">❓</div>
            <h3>匿名提問</h3>
            <p>參與者可以匿名提出問題，消除發言障礙</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">👍</div>
            <h3>即時投票</h3>
            <p>對問題進行投票，熱門問題自動排序</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>AI即時統整</h3>
            <p>本地AI及時統整大家意見並給出建議</p>
          </div>
        </div>
      </section>
    </main>

    <!-- 建立會議室 Modal -->
    <div class="modal" :class="{ active: showCreateModal }" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>建立新會議室</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="createRoom">
          <div class="form-group">
            <label for="roomTitle">會議室名稱</label>
            <input type="text" id="roomTitle" v-model="createForm.title" required placeholder="輸入會議室名稱" />
          </div>
          <div class="form-group">
            <label for="hostName">主持人姓名</label>
            <input type="text" id="hostName" v-model="createForm.host" required placeholder="輸入您的姓名" />
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
            <button type="submit" class="btn btn-primary">建立會議室</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 加入會議室 Modal -->
    <div class="modal" :class="{ active: showJoinModal }" @click.self="closeModal">
      <div class="modal-content modal-large">
        <div class="modal-header">
          <h3>加入會議室</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        
        <!-- 會議室列表 -->
        <div class="room-list-container">
          <!-- 狀態篩選器 -->
          <div class="filter-section">
            <label>篩選會議室狀態：</label>
            <div class="filter-buttons">
              <button 
                type="button" 
                :class="['filter-btn', { active: selectedFilter === 'all' }]"
                @click="selectedFilter = 'all'"
              >
                全部
              </button>
              <button 
                type="button" 
                :class="['filter-btn', { active: selectedFilter === 'Stop' }]"
                @click="selectedFilter = 'Stop'"
              >
                休息中
              </button>
              <button 
                type="button" 
                :class="['filter-btn', { active: selectedFilter === 'Discussion' }]"
                @click="selectedFilter = 'Discussion'"
              >
                討論中
              </button>
              <button 
                type="button" 
                :class="['filter-btn', { active: selectedFilter === 'End' }]"
                @click="selectedFilter = 'End'"
              >
                已結束
              </button>
            </div>
          </div>

          <!-- 會議室列表 -->
          <div class="room-list">
            <div class="room-list-header">
              <span>會議室標題</span>
              <span>主持人</span>
              <span>狀態</span>
              <span>建立時間</span>
            </div>
            <div 
              v-for="room in filteredRooms" 
              :key="room.code"
              class="room-item-container"
            >
              <div 
                class="room-item"
                :class="{ 'selected': selectedRoom?.code === room.code }"
                @click="selectRoom(room)"
              >
                <span class="room-title">{{ room.title }}</span>
                <span class="room-host">{{ room.host }}</span>
                <span :class="['room-status', `status-${room.status}`]">
                  {{ getStatusText(room.status) }}
                </span>
                <span class="room-time">{{ formatTime(room.created_at) }}</span>
              </div>
              
              <!-- 展開的輸入代碼表單 -->
              <div 
                v-if="selectedRoom?.code === room.code" 
                class="room-join-form"
              >
                <div class="join-form-content">
                  <h4>
                    <i class="fas fa-sign-in-alt"></i>
                    加入會議室：{{ selectedRoom.title }}
                  </h4>
                  <form @submit.prevent="joinSelectedRoom" class="inline-join-form">
                    <div class="form-row">
                      <div class="form-group">
                        <label for="roomCode">請輸入會議室代碼確認加入</label>
                        <input
                          type="text"
                          id="roomCode"
                          v-model="joinCode"
                          required
                          placeholder="輸入 6 位數代碼"
                          maxlength="6"
                          class="join-input"
                          ref="joinCodeInput"
                        />
                      </div>
                      <div class="form-actions">
                        <button type="button" class="btn btn-outline btn-sm" @click="selectedRoom = null">
                          <i class="fas fa-times"></i>
                          取消
                        </button>
                        <button type="submit" class="btn btn-primary btn-sm">
                          <i class="fas fa-sign-in-alt"></i>
                          確認加入
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
            </div>
            <div v-if="filteredRooms.length === 0" class="no-rooms">
              沒有找到符合條件的會議室
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 通知訊息 -->
    <TransitionGroup name="fade">
      <div
        v-for="(msg, i) in notifications"
        :key="i"
        :class="['notification', `notification-${msg.type}`]"
        style="position: fixed; top: 20px; right: 20px; z-index: 2000; margin-bottom: 12px;"
      >
        <span>{{ msg.text }}</span>
        <button @click="removeNotification(i)">&times;</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- 只保留這個 API_BASE ---
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

// --- Modal 狀態 ---
const showCreateModal = ref(false)
const showJoinModal = ref(false)
const createForm = reactive({ title: '', host: '' })
const joinCode = ref('')

// --- 會議室列表相關 ---
const rooms = ref([])
const selectedFilter = ref('all')
const selectedRoom = ref(null)

// --- 通知 ---
const notifications = ref([])

// --- 計算過濾後的會議室 ---
const filteredRooms = computed(() => {
  if (selectedFilter.value === 'all') {
    return rooms.value
  }
  return rooms.value.filter(room => room.status === selectedFilter.value)
})

// --- Modal 開關 ---
async function openModal(type) {
  if (type === 'create') {
    showCreateModal.value = true
    setTimeout(() => document.getElementById('roomTitle')?.focus(), 200)
  }
  if (type === 'join') {
    await loadRooms() // 載入會議室列表
    showJoinModal.value = true
  }
}

function closeModal() {
  showCreateModal.value = false
  showJoinModal.value = false
  selectedRoom.value = null
  joinCode.value = ''
}

// --- 載入會議室列表 ---
async function loadRooms() {
  try {
    const resp = await fetch(`${API_BASE}/api/rooms`)
    if (!resp.ok) throw new Error('無法載入會議室列表')
    const data = await resp.json()
    rooms.value = data.rooms || []
  } catch (err) {
    showNotification('載入會議室列表失敗', 'error')
  }
}

// --- 選擇會議室 ---
function selectRoom(room) {
  // 如果點擊的是已選中的會議室，則取消選擇
  if (selectedRoom.value?.code === room.code) {
    selectedRoom.value = null
    joinCode.value = ''
    return
  }
  
  selectedRoom.value = room
  joinCode.value = ''
  
  // 在下一個 DOM 更新後聚焦到輸入框
  setTimeout(() => {
    const input = document.getElementById('roomCode')
    if (input) {
      input.focus()
    }
  }, 100)
}

// --- 建立會議室 ---
async function createRoom() {
  if (!createForm.title.trim() || !createForm.host.trim()) {
    showNotification('請填寫所有必填欄位', 'error')
    return
  }
  try {
    const resp = await fetch(`${API_BASE}/api/create_room`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: createForm.title.trim(),
        host: createForm.host.trim()
      })
    })
    if (!resp.ok) throw new Error("建立失敗")
    const data = await resp.json()
    closeModal()
    createForm.title = ''
    createForm.host = ''
    showNotification(`會議室建立成功！代碼：${data.code || data.room_code}`, 'success')
    setTimeout(() => {
      router.push(`/host?room=${data.code || data.room_code}`)
    }, 1000)
  } catch (err) {
    showNotification('建立會議室失敗，請稍後再試', 'error')
  }
}

// --- 加入會議室 ---
async function joinSelectedRoom() {
  const code = joinCode.value.trim().toUpperCase()
  
  // 驗證代碼是否與選擇的會議室匹配
  if (code !== selectedRoom.value.code) {
    showNotification('輸入的代碼與選擇的會議室不符', 'error')
    return
  }
  
  if (!code || code.length !== 6) {
    showNotification('請輸入有效的 6 位數會議室代碼', 'error')
    return
  }
  
  try {
    const resp = await fetch(`${API_BASE}/api/room_status?room=${code}`)
    const data = await resp.json()
    const room_status = data["status"]

    console.log("Room status:", room_status)
    if (room_status === "NotFound") {
      showNotification('找不到該會議室，請檢查代碼是否正確', 'error')
      return
    }
    if (room_status === "End") {
      showNotification('該會議室已結束', 'error')
      return
    }
    closeModal()
    showNotification('正在加入會議室...', 'success')
    setTimeout(() => {
      router.push(`/participant?room=${code}`)
    }, 1000)
  } catch (e) {
    showNotification('加入會議室失敗，請稍後再試', 'error')
  }
}

// --- 格式化時間 ---
function formatTime(timeString) {
  const date = new Date(timeString*1000)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// --- 獲取狀態文字 ---
function getStatusText(status) {
  const statusMap = {
    'Stop': '休息中',
    'Discussion': '討論中',
    'End': '已結束',
    'NotFound': '未找到'
  }
  return statusMap[status] || status
}

// --- 通知 ---
function showNotification(text, type = 'info') {
  notifications.value.push({ text, type })
  setTimeout(() => notifications.value.shift(), 4000)
}
function removeNotification(i) {
  notifications.value.splice(i, 1)
}
</script>

<style scoped>
@import url('../assets/styles.css');

.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 大型 Modal - 使用更高優先級 */
.modal-content.modal-large {
  max-width: 900px !important;
  max-height: 85vh;
  overflow-y: auto;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: none;
}

/* 會議室列表容器 */
.room-list-container {
  margin: 0 20px 20px 20px;
  padding: 0 10px;
}

/* 篩選器區域 */
.filter-section {
  margin-bottom: 25px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.filter-section label {
  display: block;
  margin-bottom: 15px;
  font-weight: 600;
  color: #495057;
  text-align: center;
  font-size: 16px;
}

.filter-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.filter-btn {
  padding: 12px 20px;
  border: 2px solid #dee2e6;
  background: white;
  color: #6c757d;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-btn:hover {
  border-color: #007bff;
  color: #007bff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,123,255,0.2);
}

.filter-btn.active {
  background: linear-gradient(135deg, #007bff, #0056b3);
  border-color: #007bff;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,123,255,0.3);
}

/* 會議室列表 */
.room-list {
  border: 1px solid #dee2e6;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  background: white;
  margin: 0 10px;
}

.room-item-container {
  border-bottom: 1px solid #f1f3f4;
}

.room-item-container:last-child {
  border-bottom: none;
}

.room-list-header {
  display: grid;
  grid-template-columns: 2.5fr 1.5fr 1fr 1.5fr;
  gap: 20px;
  padding: 20px 25px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  font-weight: 700;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  text-align: center;
}

.room-list-header span:first-child {
  text-align: left;
}

.room-item {
  display: grid;
  grid-template-columns: 2.5fr 1.5fr 1fr 1.5fr;
  gap: 20px;
  padding: 20px 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  align-items: center;
}

.room-item:hover {
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.room-item.selected {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border-left: 4px solid #2196f3;
}

/* 內嵌加入表單 */
.room-join-form {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-top: 1px solid #dee2e6;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    max-height: 0;
    opacity: 0;
  }
  to {
    max-height: 200px;
    opacity: 1;
  }
}

.join-form-content {
  padding: 20px 25px;
}

.join-form-content h4 {
  margin-bottom: 15px;
  color: #495057;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.join-form-content h4 i {
  color: #2196f3;
}

.inline-join-form {
  margin: 0;
}

.form-row {
  display: flex;
  align-items: end;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

.form-row .form-group label {
  font-size: 14px;
  margin-bottom: 8px;
  color: #6c757d;
}

.join-input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  background: white;
}

.join-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.form-row .form-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 0;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-sm i {
  font-size: 12px;
}

.room-title {
  font-weight: 600;
  color: #212529;
  text-align: left;
  font-size: 16px;
}

.room-host {
  color: #6c757d;
  text-align: center;
  font-weight: 500;
}

.room-status {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 80px;
  margin: 0 auto;
}

.status-Stop {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  color: #856404;
  border: 1px solid #ffeaa7;
}

.status-Discussion {
  background: linear-gradient(135deg, #d1ecf1, #74b9ff);
  color: #0c5460;
  border: 1px solid #74b9ff;
}

.status-End {
  background: linear-gradient(135deg, #f8d7da, #fd79a8);
  color: #721c24;
  border: 1px solid #fd79a8;
}

.room-time {
  color: #6c757d;
  font-size: 14px;
  text-align: center;
  font-weight: 500;
}

.no-rooms {
  padding: 60px 40px;
  text-align: center;
  color: #6c757d;
  font-style: italic;
  font-size: 16px;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .modal-content.modal-large {
    max-width: 95% !important;
    margin: 20px auto;
    max-height: 90vh;
  }
  
  .room-list-container {
    margin: 0 10px 15px 10px;
    padding: 0;
  }
  
  .room-list {
    margin: 0;
    border-radius: 8px;
  }
  
  /* 改為卡片式佈局 */
  .room-list-header {
    display: none; /* 隱藏表頭 */
  }
  
  .room-item {
    display: block;
    padding: 20px;
    border-bottom: 1px solid #f1f3f4;
    text-align: left;
  }
  
  .room-item:hover {
    transform: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  }
  
  .room-item.selected {
    border-left: 4px solid #2196f3;
    background: linear-gradient(135deg, #f0f7ff, #e3f2fd);
  }
  
  /* 卡片式內容佈局 */
  .room-title {
    display: block;
    font-size: 16px;
    font-weight: 600;
    color: #212529;
    margin-bottom: 12px;
    text-align: left !important;
  }
  
  .room-title::before {
    content: "📋 ";
    color: #007bff;
  }
  
  .room-host {
    display: block;
    margin-bottom: 8px;
    color: #6c757d;
    font-size: 14px;
    text-align: left;
  }
  
  .room-host::before {
    content: "👤 主持人：";
    color: #28a745;
    font-weight: 500;
  }
  
  .room-status {
    display: inline-block;
    margin-bottom: 8px;
    margin-right: 15px;
    padding: 6px 12px;
    font-size: 11px;
    min-width: auto;
  }
  
  .room-time {
    display: block;
    color: #6c757d;
    font-size: 13px;
    text-align: left;
  }
  
  .room-time::before {
    content: "🕒 建立時間：";
    color: #ffc107;
    font-weight: 500;
  }
  
  /* 篩選器優化 */
  .filter-section {
    margin-bottom: 20px;
    padding: 15px;
  }
  
  .filter-section label {
    font-size: 15px;
    margin-bottom: 12px;
  }
  
  .filter-buttons {
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  .filter-btn {
    padding: 8px 14px;
    font-size: 12px;
    min-width: 70px;
  }
  
  /* 手機版內嵌表單優化 - 修復被遮蓋問題 */
  .room-join-form {
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    margin: 15px 0 -20px 0; /* 修改左右邊距為0 */
    border-radius: 0 0 8px 8px;
  }
  
  .join-form-content {
    padding: 20px 15px; /* 調整左右padding */
  }
  
  .join-form-content h4 {
    font-size: 15px;
    margin-bottom: 15px;
    text-align: center;
  }
  
  .form-row {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .form-row .form-group label {
    font-size: 13px;
    text-align: center;
    display: block;
    margin-bottom: 8px;
  }
  
  .join-input {
    padding: 12px 15px;
    font-size: 16px; /* 防止iOS縮放 */
    text-align: center;
    letter-spacing: 2px;
    border-radius: 8px;
    width: 100%;
    box-sizing: border-box;
  }
  
  .form-row .form-actions {
    justify-content: center;
    gap: 12px;
  }
  
  .btn-sm {
    padding: 10px 20px;
    font-size: 14px;
    border-radius: 6px;
  }
  
  /* 空狀態優化 */
  .no-rooms {
    padding: 40px 20px;
    font-size: 15px;
    line-height: 1.5;
  }
}

@media (max-width: 480px) {
  .modal-content.modal-large {
    max-width: 98% !important;
    margin: 10px auto;
    max-height: 95vh;
  }
  
  .room-list-container {
    margin: 0 5px 10px 5px; /* 調整左右邊距 */
  }
  
  .filter-section {
    padding: 12px;
  }
  
  .filter-buttons {
    gap: 6px;
  }
  
  .filter-btn {
    padding: 6px 10px;
    font-size: 11px;
    min-width: 60px;
  }
  
  .room-item {
    padding: 15px;
  }
  
  .room-title {
    font-size: 15px;
    margin-bottom: 10px;
  }
  
  /* 修復小螢幕輸入表單 */
  .room-join-form {
    margin: 15px 0 -15px 0; /* 確保左右沒有負邊距 */
  }
  
  .join-form-content {
    padding: 15px 10px; /* 減少左右padding */
  }
  
  .form-row .form-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .btn-sm {
    width: 100%;
    justify-content: center;
  }
  
  /* 導覽列響應式 */
  .nav-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .nav-actions .btn {
    font-size: 12px;
    padding: 8px 12px;
  }
}
</style>
