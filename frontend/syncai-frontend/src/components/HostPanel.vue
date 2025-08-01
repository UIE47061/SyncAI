<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>SyncAI</h1>
          <span>主持人面板</span>
        </div>
        <div class="nav-actions">
          <div class="room-info">
            <span class="room-code">會議代碼: <strong>{{ roomCode || '------' }}</strong></span>
            <span class="participant-count">參與人數: <strong>{{ room?.participants ?? 0 }}</strong></span>
          </div>
          <button class="btn btn-outline" @click="endRoom">結束會議</button>
        </div>
      </div>
    </nav>
    
    <main class="host-content">
      <div class="host-layout">
        <!-- 左側主題列表 -->
        <div class="topics-sidebar" :class="{ 'collapsed': isSidebarCollapsed, 'panel-style': !isSidebarCollapsed }">
          <!-- 折疊時只顯示按鈕 -->
          <div v-if="isSidebarCollapsed" class="sidebar-collapsed-toggle" @click="toggleSidebar">
            <i class="fa-solid fa-angles-right"></i>
          </div>
          
          <!-- 展開時顯示完整側邊欄 -->
          <template v-else>
            <div class="panel-header">
              <h2>主題列表</h2>
              <div class="panel-controls">
                <div class="sidebar-toggle" @click="toggleSidebar">
                  <i class="fa-solid fa-angles-left"></i>
                </div>
              </div>
            </div>
            <div class="topics-container">
              <div class="topic-item" v-for="(topic, index) in topics" :key="index" 
                  :class="{ 'active': selectedTopicIndex === index }" 
                  @click="selectTopic(index)">
                <i class="fa-solid fa-list topic-icon"></i>
                <div class="topic-text">{{ topic.title }}</div>
                <button class="topic-edit-btn" @click.stop="startEditTopic(index)" title="重命名主題">
                  <i class="fa-solid fa-pen-to-square"></i>
                </button>
              </div>
              
              <!-- 主題編輯模式 -->
              <div v-if="editingTopicIndex !== null" class="topic-edit-overlay">
                <div class="topic-edit-container">
                  <h3>編輯主題</h3>
                  <input 
                    ref="topicEditInput"
                    v-model="editingTopicName" 
                    @keyup.enter="saveTopicEdit" 
                    @keyup.esc="cancelTopicEdit"
                    class="topic-edit-input"
                    placeholder="輸入主題名稱"
                  />
                  <div class="topic-edit-actions">
                    <button @click="saveTopicEdit" class="btn btn-primary">
                      <i class="fa-solid fa-check"></i> 保存
                    </button>
                    <button @click="cancelTopicEdit" class="btn btn-outline">
                      <i class="fa-solid fa-xmark"></i> 取消
                    </button>
                  </div>
                </div>
              </div>
              
              <div class="topic-actions">
                <button class="btn btn-primary btn-sm" @click="addNewTopic">
                  <i class="fa-solid fa-plus"></i>
                  <span>新增主題</span>
                </button>
                <button class="btn btn-outline btn-sm" @click="exportAllTopics">
                  <i class="fa-solid fa-download"></i>
                  <span>匯出全部</span>
                </button>
              </div>
            </div>
          </template>
        </div>
        
        <!-- 問題列表 -->
        <div class="questions-panel">
          <div class="panel-header">
            <h2>問題列表</h2>
            <div class="panel-controls">
              <select v-model="sortBy" class="sort-options">
                <option value="votes">按票數排序</option>
                <option value="time">按時間排序</option>
              </select>
              <button class="btn btn-outline btn-sm" @click="clearAllQuestions">清空所有</button>
            </div>
          </div>
          <div class="questions-container">
            <template v-if="sortedQuestions.length === 0">
              <div class="empty-state">
                <div class="empty-icon">
                  <i class="fa-regular fa-comment-dots"></i>
                </div>
                <h3>等待參與者提問</h3>
                <p>分享會議室代碼讓參與者加入並開始提問</p>
              </div>
            </template>
            <template v-else>
              <div
                v-for="q in sortedQuestions"
                :key="q.id"
                class="question-item"
                :class="{ 'question-answered': q.answered }"
              >
                <div class="question-header">
                  <div class="question-text" v-html="escapeHtml(q.text)"></div>
                  <div class="question-actions">
                    <button class="btn-icon" @click="toggleAnswered(q.id)" :title="q.answered ? '標記為未回答' : '標記為已回答'">
                      <i v-if="q.answered" class="fa-solid fa-circle-check"></i>
                      <i v-else class="fa-regular fa-circle"></i>
                    </button>
                    <button class="btn-icon" @click="deleteQuestion(q.id)" title="刪除問題">
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </div>
                </div>
                <div class="question-meta">
                  <div class="question-votes">
                    <i class="fa-solid fa-thumbs-up"></i> {{ q.votes || 0 }}
                  </div>
                  <div class="question-time">
                    {{ formatTime(q.createdAt) }}
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
        <!-- 控制面板 -->
        <div class="control-panel">
          <div class="panel-header">
            <h2>會議室控制</h2>
            <div class="panel-controls">
              <button class="btn-qrcode" @click="showQRCode">
                開啟 QR Code
              </button>
            </div>
          </div>
          <div class="control-section">
            <h3>會議連結</h3>
            <div class="share-item">
                  <div class="code-display">
                    <span>{{ roomLink }}</span>
                    <button class="btn-icon" @click="copyRoomLink" title="複製連結">
                      <i class="fa-regular fa-clipboard"></i>
                    </button>
                  </div>
                </div>
          </div>
          <div class="control-section">
            <h3>計時器</h3>
            <div class="timer-display">
              <div class="timer-time">{{ formattedRemainingTime }}</div>
              <div class="timer-controls">
                <button class="btn-timer" :class="{ 'timer-active': timerRunning }" @click="toggleTimer">
                  <i :class="timerRunning ? 'fa-solid fa-pause' : 'fa-solid fa-play'"></i>
                </button>
                <button class="btn-timer" @click="showTimerSettings">
                  <i class="fa-solid fa-gear"></i>
                </button>
                <button class="btn-timer btn-terminate" @click="terminateTimer">
                  <i class="fa-solid fa-stop"></i>
                </button>
              </div>
            </div>
          </div>

          <div class="control-section">
            <h3>問答設定</h3>
            <div class="setting-item">
              <label class="switch">
                <input type="checkbox" v-model="settings.allowQuestions">
                <span class="slider"></span>
              </label>
              <span>允許新問題</span>
            </div>
            <div class="setting-item">
              <label class="switch">
                <input type="checkbox" v-model="settings.allowVoting">
                <span class="slider"></span>
              </label>
              <span>允許投票</span>
            </div>
          </div>
          <div class="control-section">
            <h3>統計資訊</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">{{ questions.length }}</div>
                <div class="stat-label">總問題數</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ totalVotes }}</div>
                <div class="stat-label">總投票數</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ room?.participants ?? 0 }}</div>
                <div class="stat-label">活躍參與者</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

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

    <!-- QR Code 彈窗 -->
    <div v-if="isQRCodeModalVisible" class="qrcode-modal-overlay" @click.self="hideQRCode">
      <div class="qrcode-modal">
        <div class="qrcode-modal-header">
          <h3>會議室 QR Code</h3>
          <button class="btn-close" @click="hideQRCode">&times;</button>
        </div>
        <div class="qrcode-modal-body">
          <div class="qrcode-large">
            <qrcode-vue :value="roomLink" :size="qrcodeSize" level="H" />
          </div>
          <div class="qrcode-modal-info">
            <div class="qrcode-room-code">會議室代碼：{{ roomCode }}</div>
            <div class="qrcode-link-text">{{ roomLink }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 計時器設定彈窗 -->
    <div v-if="isTimerSettingsVisible" class="timer-settings-overlay" @click.self="hideTimerSettings">
      <div class="timer-settings-modal">
        <div class="modal-header">
          <h3>設定計時器</h3>
          <button class="btn-close" @click="hideTimerSettings">&times;</button>
        </div>
        <div class="modal-body">
          <!-- 時間輸入區域 -->
          <div class="time-input-section">
            <div class="time-input-group">
              <div class="time-input-container">
                <input type="number" v-model="timerSettings.hours" min="0" max="23" class="time-input">
                <label class="time-label">時</label>
              </div>
              <div class="time-input-container">
                <input type="number" v-model="timerSettings.minutes" min="0" max="59" class="time-input">
                <label class="time-label">分</label>
              </div>
              <div class="time-input-container">
                <input type="number" v-model="timerSettings.seconds" min="0" max="59" class="time-input">
                <label class="time-label">秒</label>
              </div>
            </div>
          </div>
          
          <!-- 快捷選項 -->
          <div class="timer-presets">
            <button class="timer-preset-btn" @click="setPresetTime(1)">1 分鐘</button>
            <button class="timer-preset-btn" @click="setPresetTime(5)">5 分鐘</button>
            <button class="timer-preset-btn" @click="setPresetTime(10)">10 分鐘</button>
          </div>
          
          <!-- 設定完成按鈕 -->
          <div class="timer-settings-actions">
            <button class="btn btn-primary" @click="applyTimerSettings">
              <i class="fa-solid fa-check"></i> 確定
            </button>
            <button class="btn btn-outline" @click="hideTimerSettings">
              <i class="fa-solid fa-xmark"></i> 取消
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import QrcodeVue from 'qrcode.vue'

// 狀態
const room = ref(null)
const roomCode = ref('')
const questions = ref([])
const settings = reactive({ allowQuestions: true, allowVoting: true })
const sortBy = ref('votes')
const notifications = ref([])
const isQRCodeModalVisible = ref(false)
const qrcodeSize = ref(window.innerWidth < 768 ? 320 : 640)

// 計時器相關
const remainingTime = ref(0) // 剩餘時間（以秒為單位）
const initialTime = ref(0) // 初始設定的時間
const timerRunning = ref(false) // 計時器是否運行中
const timerInterval = ref(null) // 計時器間隔引用
const isTimerSettingsVisible = ref(false) // 計時器設定彈窗是否可見
const timerSettings = reactive({
  hours: 0,
  minutes: 5,
  seconds: 0
})

// 側邊欄與主題相關
const isSidebarCollapsed = ref(false)
const topics = ref([
  { title: '主題1', content: '', timestamp: new Date().toISOString() }
])
const selectedTopicIndex = ref(0)
const editingTopicIndex = ref(null)
const editingTopicName = ref('')

// 統計
const totalVotes = computed(() => questions.value.reduce((sum, q) => sum + (q.votes || 0), 0))

// 分享連結
const roomLink = computed(() => {
  return `${window.location.origin}/participant?room=${roomCode.value || ''}`
})

// participantUrl.value = `${window.location.protocol}//${window.location.hostname}:5173/participant?room=${roomCode.value}`

// 問題排序
const sortedQuestions = computed(() => {
  const arr = [...questions.value]
  if (sortBy.value === 'votes') {
    return arr.sort((a, b) => (b.votes || 0) - (a.votes || 0))
  }
  return arr.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

// 取得 Room 資訊
function loadRoom() {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('room')
  if (!code) {
    alert('無效的會議室代碼')
    window.location.href = 'index.html'
    return
  }
  roomCode.value = code

  // 從 localStorage 取得資料
  try {
    const roomsData = localStorage.getItem('Sync_AI_rooms')
    if (roomsData) {
      const rooms = new Map(JSON.parse(roomsData))
      const r = rooms.get(code)
      if (!r) {
        alert('找不到該會議室')
        window.location.href = 'index.html'
        return
      }
      room.value = r
      questions.value = r.questions || []
      Object.assign(settings, r.settings || { allowQuestions: true, allowVoting: true })
      
      // 如果房間數據中有主題，則載入它們
      if (r.topics && r.topics.length > 0) {
        topics.value = r.topics
      }
    }
  } catch (e) {
    alert('載入會議室失敗')
    window.location.href = 'index.html'
  }
}

// 寫回 localStorage
function saveRoom() {
  try {
    const roomsData = localStorage.getItem('Sync_AI_rooms')
    const rooms = new Map(roomsData ? JSON.parse(roomsData) : [])
    room.value.questions = questions.value
    room.value.updatedAt = new Date().toISOString()
    room.value.settings = { ...settings }
    room.value.topics = topics.value  // 將主題保存到房間數據中
    rooms.set(roomCode.value, room.value)
    localStorage.setItem('Sync_AI_rooms', JSON.stringify(Array.from(rooms.entries())))
  } catch (e) {
    console.error('保存房間資料失敗:', e)
  }
}

// 問題操作
function toggleAnswered(id) {
  const q = questions.value.find(q => q.id === id)
  if (q) {
    q.answered = !q.answered
    saveRoom()
  }
}
function deleteQuestion(id) {
  if (confirm('確定要刪除這個問題嗎？')) {
    questions.value = questions.value.filter(q => q.id !== id)
    room.value.questions = questions.value
    saveRoom()
  }
}
function clearAllQuestions() {
  if (confirm('確定要清空所有問題嗎？此操作無法復原。')) {
    questions.value = []
    room.value.questions = []
    saveRoom()
  }
}

// 會議控制
function endRoom() {
  if (confirm('確定要結束會議嗎？參與者將無法繼續提問和投票。')) {
    room.value.isActive = false
    room.value.endedAt = new Date().toISOString()
    saveRoom()
    showNotification('會議已結束', 'success')
    setTimeout(() => { window.location.href = 'index.html' }, 2000)
  }
}

// 通知
function showNotification(text, type = 'info') {
  notifications.value.push({ text, type })
  setTimeout(() => notifications.value.shift(), 4000)
}
function removeNotification(i) {
  notifications.value.splice(i, 1)
}

// 共享剪貼簿
const copyRoomCode = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(roomCode.value)
      showNotification('代碼已複製', 'success')
    } else {
      // Fallback: 建立暫時 input 執行複製
      const tmpInput = document.createElement('input')
      tmpInput.value = roomCode.value
      document.body.appendChild(tmpInput)
      tmpInput.select()
      document.execCommand('copy')
      document.body.removeChild(tmpInput)
      showNotification('代碼已複製', 'success')
    }
  } catch (e) {
    showNotification('複製失敗，請手動複製', 'error')
  }
}

const copyRoomLink = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(roomLink.value)
      showNotification('連結已複製', 'success')
    } else {
      // Fallback: 建立暫時 input 執行複製
      const tmpInput = document.createElement('input')
      tmpInput.value = roomLink.value
      document.body.appendChild(tmpInput)
      tmpInput.select()
      document.execCommand('copy')
      document.body.removeChild(tmpInput)
      showNotification('連結已複製', 'success')
    }
  } catch (e) {
    showNotification('複製失敗，請手動複製', 'error')
  }
}

// 工具
function formatTime(dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '剛剛'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分鐘前`
  return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}
function escapeHtml(text) {
  // Vue 自動 escape，不過保留此函式相容
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// QR Code 彈窗控制
function showQRCode() {
  // 顯示彈窗時更新 QR Code 尺寸
  updateQRCodeSize()
  isQRCodeModalVisible.value = true
}

function hideQRCode() {
  isQRCodeModalVisible.value = false
}

// 根據窗口寬度更新 QR Code 尺寸
function updateQRCodeSize() {
  qrcodeSize.value = window.innerWidth < 768 ? 320 : 640
}

// 監聽設定變化自動寫回
watch(settings, saveRoom, { deep: true })

// 側邊欄相關函數
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value.toString())
}

function selectTopic(index) {
  selectedTopicIndex.value = index
}

function startEditTopic(index) {
  editingTopicIndex.value = index
  editingTopicName.value = topics.value[index].title
  // 在下一個 DOM 更新循環後聚焦到輸入框
  setTimeout(() => {
    if (editingTopicIndex.value !== null && document.querySelector('.topic-edit-input')) {
      document.querySelector('.topic-edit-input').focus()
    }
  }, 50)
}

function saveTopicEdit() {
  if (editingTopicIndex.value !== null && editingTopicName.value.trim()) {
    topics.value[editingTopicIndex.value].title = editingTopicName.value.trim()
    saveTopics()
    editingTopicIndex.value = null
    editingTopicName.value = ''
  }
}

function cancelTopicEdit() {
  editingTopicIndex.value = null
  editingTopicName.value = ''
}

function addNewTopic() {
  topics.value.push({
    title: `主題 ${topics.value.length + 1}`,
    content: '',
    timestamp: new Date().toISOString()
  })
  // 選擇新添加的主題
  selectedTopicIndex.value = topics.value.length - 1
  saveTopics()
}

function exportAllTopics() {
  try {
    // 將主題資料轉換為 JSON 文字
    const topicsData = JSON.stringify(topics.value, null, 2)
    
    // 創建 Blob 和下載連結
    const blob = new Blob([topicsData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `會議主題_${roomCode.value}_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    }, 0)
    
    showNotification('主題資料已匯出', 'success')
  } catch (e) {
    showNotification('匯出失敗', 'error')
  }
}

function loadTopics() {
  try {
    const savedTopics = localStorage.getItem(`topics_${roomCode.value}`)
    if (savedTopics) {
      topics.value = JSON.parse(savedTopics)
    }
    
    // 讀取側邊欄折疊狀態
    const savedCollapsed = localStorage.getItem('sidebarCollapsed')
    if (savedCollapsed !== null) {
      isSidebarCollapsed.value = savedCollapsed === 'true'
    }
  } catch (e) {
    console.error('讀取主題失敗:', e)
  }
}

function saveTopics() {
  try {
    localStorage.setItem(`topics_${roomCode.value}`, JSON.stringify(topics.value))
  } catch (e) {
    console.error('儲存主題失敗:', e)
  }
}

// 監聽主題變化
watch(topics, saveTopics, { deep: true })

// 輪詢
// 計時器函數
function showTimerSettings() {
  // 載入保存的設置（如果有）
  const savedSettings = localStorage.getItem(`timer_settings_${roomCode.value}`)
  if (savedSettings) {
    Object.assign(timerSettings, JSON.parse(savedSettings))
  }
  isTimerSettingsVisible.value = true
}

function hideTimerSettings() {
  isTimerSettingsVisible.value = false
}

function setPresetTime(minutes) {
  timerSettings.hours = 0
  timerSettings.minutes = minutes
  timerSettings.seconds = 0
}

function applyTimerSettings() {
  // 計算總秒數
  const totalSeconds = 
    (timerSettings.hours * 3600) + 
    (timerSettings.minutes * 60) + 
    timerSettings.seconds
  
  // 保存設置
  localStorage.setItem(`timer_settings_${roomCode.value}`, JSON.stringify(timerSettings))
  
  // 設置計時器
  remainingTime.value = totalSeconds
  initialTime.value = totalSeconds
  
  // 關閉設定彈窗
  hideTimerSettings()
  
  // 如果時間已設置，自動開始計時
  if (totalSeconds > 0) {
    startTimer()
  }
}

function startTimer() {
  if (remainingTime.value <= 0) return
  
  timerRunning.value = true
  
  // 清除可能存在的舊計時器
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
  
  // 設置新計時器
  timerInterval.value = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
    } else {
      stopTimer()
      // 計時結束時發出通知
      showNotification('計時器時間到！', 'info')
    }
  }, 1000)
}

function stopTimer() {
  timerRunning.value = false
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
}

function toggleTimer() {
  if (remainingTime.value <= 0) {
    // 如果沒有設置時間，開啟設置面板
    showTimerSettings()
    return
  }
  
  if (timerRunning.value) {
    stopTimer()
  } else {
    startTimer()
  }
}

function terminateTimer() {
  // 停止計時器
  stopTimer()
  // 將剩餘時間設為0（時間到）
  remainingTime.value = 0
  // 顯示時間到的通知
  showNotification('計時已終止！', 'info')
}

// 格式化剩餘時間為 HH:MM:SS 格式
const formattedRemainingTime = computed(() => {
  if (remainingTime.value <= 0) return '00:00:00'
  
  const hours = Math.floor(remainingTime.value / 3600)
  const minutes = Math.floor((remainingTime.value % 3600) / 60)
  const seconds = remainingTime.value % 60
  
  return [hours, minutes, seconds]
    .map(v => v.toString().padStart(2, '0'))
    .join(':')
})

// 從本地存儲中載入計時器設置
function loadTimerSettings() {
  try {
    // 載入設置
    const savedSettings = localStorage.getItem(`timer_settings_${roomCode.value}`)
    if (savedSettings) {
      Object.assign(timerSettings, JSON.parse(savedSettings))
      
      // 計算總秒數
      initialTime.value = 
        (timerSettings.hours * 3600) + 
        (timerSettings.minutes * 60) + 
        timerSettings.seconds
      
      remainingTime.value = initialTime.value
    } else {
      // 預設值為 5 分鐘
      timerSettings.hours = 0
      timerSettings.minutes = 5
      timerSettings.seconds = 0
    }
    
    // 載入運行狀態
    const savedRunning = localStorage.getItem(`timer_running_${roomCode.value}`)
    if (savedRunning === 'true') {
      // 如果之前是在運行中，自動啟動
      const savedRemainingTime = localStorage.getItem(`timer_remaining_${roomCode.value}`)
      if (savedRemainingTime) {
        remainingTime.value = parseInt(savedRemainingTime, 10) || initialTime.value
        if (remainingTime.value > 0) {
          startTimer()
        }
      }
    }
  } catch (e) {
    console.error('載入計時器設置失敗:', e)
  }
}

// 保存計時器狀態
function saveTimerState() {
  try {
    localStorage.setItem(`timer_running_${roomCode.value}`, timerRunning.value)
    localStorage.setItem(`timer_remaining_${roomCode.value}`, remainingTime.value)
  } catch (e) {
    console.error('保存計時器狀態失敗:', e)
  }
}

// 監聽計時器狀態變化
watch([timerRunning, remainingTime], saveTimerState)

let poller
onMounted(() => {
  loadRoom()
  loadTopics()
  loadTimerSettings() // 載入計時器設置
  
  poller = setInterval(() => {
    loadRoom()
  }, 3000)
  
  // 添加窗口大小變化的監聽器
  window.addEventListener('resize', updateQRCodeSize)
})

onBeforeUnmount(() => {
  // 組件卸載時清理
  window.removeEventListener('resize', updateQRCodeSize)
  clearInterval(poller)
  
  // 停止計時器
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
})
</script>

<style scoped>
@import url('../assets/styles.css');
@import url('../assets/host.css');

/* 更新整體佈局 */
.host-layout {
  display: grid;
  grid-template-columns: auto 1fr 350px;
  gap: 1.5rem;
  height: calc(100vh - 200px);
}

/* 通用面板樣式 */
.panel-style {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  overflow: hidden;
}

/* 側邊欄樣式 */
.topics-sidebar {
  width: 280px;
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.topics-sidebar.collapsed {
  width: 40px;
  min-height: 60px;
  background: transparent;
  border: none;
  box-shadow: none;
}

.sidebar-collapsed-toggle {
  position: absolute;
  top: 15px;
  left: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--primary-color);
  font-size: 1.1rem;
  background: var(--surface);
  border-radius: 0 0.5rem 0.5rem 0;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.sidebar-collapsed-toggle:hover {
  background: var(--primary-color);
  color: white;
  transform: translateX(3px);
}

.sidebar-toggle {
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  background: var(--surface);
  color: var(--text-secondary);
  transition: all 0.2s;
}

.sidebar-toggle:hover {
  background: var(--border);
  color: var(--primary-color);
}

.topics-container {
  padding: 1rem;
  overflow-y: auto;
  height: calc(100% - 60px);
}

.topic-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--background);
  border: 1px solid var(--border);
}

.topic-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
}

.topic-item.active {
  background: var(--surface);
  border-left: 4px solid var(--primary-color);
}

.topic-icon {
  margin-right: 10px;
  font-size: 1rem;
  color: var(--primary-color);
  width: 20px;
  text-align: center;
}

.topic-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
  color: var(--text-primary);
}

.topic-edit-btn {
  opacity: 0;
  background: none;
  border: none;
  font-size: 0.9rem;
  padding: 5px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 4px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.topic-item:hover .topic-edit-btn {
  opacity: 0.7;
}

.topic-edit-btn:hover {
  opacity: 1 !important;
  background: var(--surface);
  color: var(--primary-color);
}

.topic-edit-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 0 16px;
  backdrop-filter: blur(4px);
}

.topic-edit-container {
  background: var(--background);
  border-radius: 1rem;
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideIn 0.3s ease;
}

.topic-edit-container h3 {
  margin-bottom: 1rem;
  font-size: 1.25rem;
  color: var(--text-primary);
  font-weight: 600;
}

.topic-edit-input {
  width: 100%;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border);
  font-size: 1rem;
  margin-bottom: 1.25rem;
  transition: all 0.2s;
}

.topic-edit-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.topic-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.topic-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.5rem;
  border-top: 1px solid var(--border);
  padding-top: 1rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-sm i {
  font-size: 0.875rem;
}

/* 媒體查詢適應小螢幕 */
@media (max-width: 1024px) {
  .host-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    height: auto;
  }
  
  .topics-sidebar {
    width: 100%;
    margin-bottom: 1rem;
  }
  
  .topics-sidebar.collapsed {
    width: 50px;
    height: auto;
    margin-bottom: 1rem;
    min-height: 300px;
  }
  
  .sidebar-collapsed-toggle {
    width: 50px;
    height: 50px;
    font-size: 1.2rem;
    top: 20px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  }
}

.share-row {
  display: flex;
  align-items: flex-start;
  gap: 28px;
}
.qrcode-side {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 4px;
}
.qrcode-caption {
  font-size: 0.95em;
  color: #aaa;
  margin-top: 6px;
}
.share-options {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.share-item span {
  font-size: 1.03em;
  color: #b8b8b8;
}
.code-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
/* 手機直排 */
@media (max-width: 600px) {
  .share-row {
    flex-direction: column;
    gap: 18px;
  }
  .qrcode-side {
    align-items: flex-start;
  }
}

/* 響應式 QR Code 樣式 */
@media (max-width: 767px) {
  .qrcode-modal {
    width: 95%;
    max-width: 360px;
  }
  
  .qrcode-large {
    padding: 0.75rem;
  }
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* QR Code 按鈕和彈窗樣式 */
.btn-qrcode {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}

.btn-qrcode:hover {
  background: var(--primary-hover);
  color: white;
}

.qrcode-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.3s ease;
}

.qrcode-modal {
  background: var(--background);
  border-radius: 1rem;
  width: 90%;
  max-width: calc(640px + 6rem); /* 640px QR Code + padding */
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: modalSlideUp 0.3s ease;
}

.qrcode-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.qrcode-modal-header h3 {
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0.2rem;
}

.qrcode-modal-body {
  padding: clamp(1rem, 5vw, 1.5rem);
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
  max-height: 80vh;
}

.qrcode-large {
  background: white;
  padding: clamp(1rem, 4%, 1.5rem);
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
  width: auto;
  max-width: 100%;
  overflow: hidden;
}

.qrcode-modal-info {
  width: 100%;
  text-align: center;
}

.qrcode-room-code {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.qrcode-link-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  word-break: break-all;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalSlideUp {
  from { 
    opacity: 0;
    transform: translateY(30px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes modalSlideIn {
  from { 
    opacity: 0;
    transform: translateX(30px);
  }
  to { 
    opacity: 1;
    transform: translateX(0);
  }
}

/* 計時器樣式 */
.timer-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--background);
  padding: 12px 16px;
  border-radius: 12px;
  margin-top: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border);
}

.timer-time {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
}

.timer-controls {
  display: flex;
  gap: 10px;
}

.btn-timer {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
}

.btn-timer:hover {
  background: var(--border);
  color: var(--primary-color);
}

/* 開始按鈕顯示綠色 */
.btn-timer:not(.timer-active) i.fa-play {
  color: #16a34a;
}

.btn-timer:not(.timer-active):hover i.fa-play {
  color: white;
}

.btn-timer:not(.timer-active):hover {
  background-color: #16a34a;
  border-color: #16a34a;
}

/* 設定按鈕顯示紫色 */
.btn-timer i.fa-gear {
  color: #8b5cf6;
}

.btn-timer:hover i.fa-gear {
  color: white;
}

.btn-timer:has(i.fa-gear):hover {
  background-color: #8b5cf6;
  border-color: #8b5cf6;
}

/* 暫停按鈕顯示黃色 */
.btn-timer.timer-active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

/* 終止按鈕顯示紅色 */
.btn-timer.btn-terminate {
  color: #dc2626;
}

.btn-timer.btn-terminate:hover {
  background: #dc2626; /* 紅色背景 */
  color: white;
  border-color: #dc2626;
}

/* 計時器設定彈窗 */
.timer-settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.timer-settings-modal {
  background: var(--background);
  border-radius: 1rem;
  width: 90%;
  max-width: 480px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideUp 0.3s ease;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.time-input-section {
  margin-bottom: 1.5rem;
}

.time-input-group {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.time-input-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time-input {
  width: 80px;
  height: 80px;
  text-align: center;
  font-size: 2rem;
  border-radius: 12px;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  padding: 0;
  transition: all 0.2s;
}

.time-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.time-label {
  margin-top: 8px;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.timer-presets {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.timer-preset-btn {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 100px;
  padding: 8px 16px;
  font-size: 0.9rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.timer-preset-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.timer-settings-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* 按鈕樣式 */
.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: 1px solid transparent;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-outline {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
}
</style>
