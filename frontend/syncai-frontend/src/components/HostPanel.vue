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
            <span class="room-status" :class="'status-' + roomStatus.toLowerCase()">
              狀態: <strong>{{ roomStatusText }}</strong>
            </span>
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
        
        <!-- 意見列表 -->
        <div class="questions-panel">
          <div class="panel-header">
            <h2>意見列表 - {{ topics[selectedTopicIndex]?.title || '未選擇主題' }}</h2>
            <div class="panel-controls">
              <select v-model="sortBy" class="sort-options">
                <option value="votes">按票數排序</option>
                <option value="time">按時間排序</option>
              </select>
              <button class="btn-red btn-qrcode" @click="clearAllQuestions" :title="`清空主題「${topics[selectedTopicIndex]?.title || ''}」的所有評論`">
                <i class="fa-solid fa-trash-can"></i>
                清空評論
              </button>
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
              >
                <div class="question-header">
                  <div class="question-text" v-html="escapeHtml(q.content)"></div>
                  <div class="question-actions">
                    <button class="btn-icon" @click="deleteQuestion(q.id)" title="刪除意見">
                      <i class="fa-solid fa-trash-can"></i>
                    </button>
                  </div>
                </div>
                <div class="question-meta">
                  <div class="question-votes">
                    <span class="vote-item">
                      <i class="fa-solid fa-thumbs-up"></i> {{ q.vote_good || 0 }}
                    </span>
                    <span class="vote-item">
                      <i class="fa-solid fa-thumbs-down"></i> {{ q.vote_bad || 0 }}
                    </span>
                  </div>
                  <div class="question-info">
                    <div class="question-nickname" v-if="q.nickname">
                      <i class="fa-regular fa-user"></i> {{ q.nickname }}
                    </div>
                    <div class="question-time">
                      {{ formatTime(q.ts) }}
                    </div>
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
            <!-- <h3>分享會議室</h3> -->
            <div class="share-item">
                  <span>會議連結</span>
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
              <span>允許新意見</span>
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
                <div class="stat-label">總意見數</div>
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
import { useRouter } from 'vue-router'

// API 基礎 URL 設定
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`  // 根據實際後端服務的地址和端口進行調整

// 狀態
const room = ref(null)
const roomCode = ref('')
const questions = ref([])
const roomStatus = ref('NotFound') // 房間狀態：NotFound, Stop, Discussion
const settings = reactive({ allowQuestions: true, allowVoting: true })
const sortBy = ref('votes')
const notifications = ref([])
const isQRCodeModalVisible = ref(false)
const qrcodeSize = ref(window.innerWidth < 768 ? 320 : 640)
const router = useRouter()

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
  { title: '主題 1', content: '', timestamp: new Date().toISOString() }
])
const selectedTopicIndex = ref(0)
const editingTopicIndex = ref(null)
const editingTopicName = ref('')

// 統計
const totalVotes = computed(() => questions.value.reduce((sum, q) => sum + (q.vote_good || 0) + (q.vote_bad || 0), 0))

// 分享連結
const roomLink = computed(() => {
  return `${window.location.origin}/participant?room=${roomCode.value || ''}`
})

// 房間狀態顯示文字
const roomStatusText = computed(() => {
  switch(roomStatus.value) {
    case 'NotFound': return '未啟動';
    case 'Stop': return '休息中';
    case 'Discussion': return '討論中';
    case 'End': return '已結束';
    default: return '未知';
  }
})

// participantUrl.value = `${window.location.protocol}//${window.location.hostname}:5173/participant?room=${roomCode.value}`

// 意見排序
const sortedQuestions = computed(() => {
  const arr = [...questions.value]
  if (sortBy.value === 'votes') {
    return arr.sort((a, b) => {
      const aGood = a.vote_good || 0
      const bGood = b.vote_good || 0
      const aBad = a.vote_bad || 0
      const bBad = b.vote_bad || 0
      
      // 先按讚數由大到小排序
      if (bGood !== aGood) {
        return bGood - aGood
      }
      
      // 讚數相同時，按倒讚數由小到大排序
      return aBad - bBad
    })
  }
  return arr.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
})

// 取得 Room 資訊
function loadRoom() {
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('room')
  if (!code) {
    showNotification('無效的會議室代碼', 'error')
    setTimeout(() => {
      router.push('/')
    }, 2000)
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
        showNotification('本地找不到該會議室，將檢查服務器狀態', 'info')
        // 不在這裡直接返回，讓後續的 API 檢查來決定
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
    console.error('載入會議室失敗:', e)
    showNotification('載入會議室失敗', 'error')
    // 不在這裡直接返回，讓後續的 API 檢查來決定
  }
}

// 寫回 localStorage
function saveRoom() {
  try {
    // 檢查 room.value 和 roomCode.value 是否存在
    if (!room.value || !roomCode.value) {
      console.warn('房間資料或房間代碼不存在，跳過保存')
      return
    }
    
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

// 獲取意見列表
async function fetchQuestions() {
  if (!roomCode.value) return
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_comments?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const resp = await response.json()
    const data = resp["comments"] || []
    questions.value = data || []
    
    // 只有在 room.value 存在時才更新 localStorage 中的房間資料
    if (room.value) {
      saveRoom()
    }
  } catch (error) {
    console.error('獲取意見列表失敗:', error)
  }
}

// 意見操作
function deleteQuestion(id) {
  if (confirm('確定要刪除這個意見嗎？')) {
    questions.value = questions.value.filter(q => q.id !== id)
    room.value.questions = questions.value
    saveRoom()
  }
}

async function clearAllQuestions() {
  if (confirm('確定要清空所有意見嗎？此操作無法復原。')) {
    // 獲取當前主題名稱
    const currentTopic = topics.value[selectedTopicIndex.value]?.title
    
    if (!currentTopic) {
      showNotification('未選擇主題，無法清空意見', 'error')
      return
    }
    
    try {
      // 調用刪除主題評論的 API
      const response = await fetch(`${API_BASE_URL}/api/room_topic_comments`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          room: roomCode.value,
          topic: currentTopic
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        // 清空本地意見列表
        questions.value = []
        if (room.value) {
          room.value.questions = []
          saveRoom()
        }
        
        // 顯示詳細的清空結果
        const message = `已清空主題「${result.topic}」的所有內容：刪除了 ${result.deleted_comments_count} 個評論和 ${result.deleted_votes_count} 個投票記錄`
        showNotification(message, 'success')
        
        // 重新獲取意見列表以確保同步
        await fetchQuestions()
      } else {
        showNotification(result.error || '清空意見失敗', 'error')
      }
    } catch (error) {
      console.error('清空意見失敗:', error)
      showNotification('清空意見失敗，請稍後再試', 'error')
    }
  }
}

// 會議控制
async function endRoom() {
  if (confirm('確定要結束會議嗎？這將關閉房間並退出。')) {
    try {
      // 停止計時器 (如果有運行的話)
      if (timerRunning.value) {
        await stopTimer()
      }
      
      // 更新API狀態為 End
      await setRoomStatus('End')
      
      // 更新本地房間狀態（如果存在）
      if (room.value) {
        room.value.isActive = false
        room.value.endedAt = new Date().toISOString()
        saveRoom()
      }
      
      showNotification('會議已結束，房間已關閉', 'success')
      setTimeout(() => {router.push('/');}, 2000)
    } catch (error) {
      console.error('結束會議失敗:', error)
      showNotification('結束會議失敗，請稍後再試', 'error')
    }
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
  const date = new Date(dateString*1000)
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
  // 處理換行符號，將 \n 轉換為 <br>
  return div.innerHTML.replace(/\n/g, '<br>')
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
  // qrcodeSize.value = window.innerWidth < 768 ? 320 : 640
  // 寬度最多320，最少120，永遠不會超出視窗
  qrcodeSize.value = Math.max(120, Math.min(280, Math.floor(window.innerWidth * 0.3)));
}

// 監聽設定變化自動寫回
watch(settings, saveRoom, { deep: true })

// 側邊欄相關函數
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value.toString())
}

async function selectTopic(index) {
  selectedTopicIndex.value = index
  
  // 使用新的切換主題API
  const currentTopic = topics.value[index].title
  try {
    const success = await switchTopic(currentTopic)
    if (success) {
      // 切換成功後，立即獲取新主題的評論
      await fetchQuestions()
    }
  } catch (error) {
    console.error('切換主題時更新資料失敗:', error)
  }
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

async function saveTopicEdit() {
  if (editingTopicIndex.value !== null && editingTopicName.value.trim()) {
    const oldTopicName = topics.value[editingTopicIndex.value].title
    const newTopicName = editingTopicName.value.trim()
    
    // 如果名稱沒有改變，直接退出編輯模式
    if (oldTopicName === newTopicName) {
      editingTopicIndex.value = null
      editingTopicName.value = ''
      return
    }
    
    try {
      // 使用新的 rename_topic API
      const response = await fetch(`${API_BASE_URL}/api/room_rename_topic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          room: roomCode.value,
          old_topic: oldTopicName,
          new_topic: newTopicName
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        // 更新本地主題列表
        topics.value[editingTopicIndex.value].title = newTopicName
        saveTopics()
        
        // 如果重命名的是當前主題，刷新意見列表
        if (result.is_current_topic) {
          await fetchQuestions()
        }
        
        showNotification(`主題已重新命名為「${newTopicName}」`, 'success')
      } else {
        showNotification(result.error || '重新命名主題失敗', 'error')
        return
      }
    } catch (error) {
      console.error('重新命名主題失敗:', error)
      showNotification('重新命名主題失敗，請稍後再試', 'error')
      return
    }
    
    editingTopicIndex.value = null
    editingTopicName.value = ''
  }
}

function cancelTopicEdit() {
  editingTopicIndex.value = null
  editingTopicName.value = ''
}

async function addNewTopic() {
  const newTopicTitle = `主題 ${topics.value.length + 1}`
  topics.value.push({
    title: newTopicTitle,
    content: '',
    timestamp: new Date().toISOString()
  })
  // 選擇新添加的主題
  const newIndex = topics.value.length - 1
  selectedTopicIndex.value = newIndex
  saveTopics()
  
  // 自動切換到新主題
  try {
    await switchTopic(newTopicTitle)
    await fetchQuestions()
  } catch (error) {
    console.error('切換到新主題失敗:', error)
  }
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

async function applyTimerSettings() {
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
  
  // 如果時間已設置，與API同步並自動開始計時
  if (totalSeconds > 0) {
    setRoomState()
    startTimer() // 自動開始計時
  }
}

async function startTimer() {
  if (remainingTime.value <= 0) return
  
  timerRunning.value = true
  
  // 清除可能存在的舊計時器
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
  }
  
  // 更新房間狀態為討論中
  await setRoomStatus('Discussion')
  
  // 記錄計時器開始時間
  const startTime = Date.now()
  const initialSeconds = remainingTime.value
  
  // 設置新計時器，使用基於時間差的方式計算，而不是簡單地減1
  timerInterval.value = setInterval(() => {
    const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000)
    const newRemaining = initialSeconds - elapsedSeconds
    
    if (newRemaining > 0) {
      remainingTime.value = newRemaining
    } else {
      remainingTime.value = 0
      stopTimer()
      // 計時結束時發出通知
      showNotification('計時器時間到！', 'info')
    }
  }, 500) // 更頻繁檢查但只在必要時更新視圖
}

async function stopTimer() {
  timerRunning.value = false
  if (timerInterval.value) {
    clearInterval(timerInterval.value)
    timerInterval.value = null
  }
  
  // 更新房間狀態為暫停
  try {
    await setRoomStatus('Stop')
  } catch (error) {
    console.error('停止計時器時更新狀態失敗:', error)
  }
}

async function toggleTimer() {
  if (remainingTime.value <= 0) {
    // 如果沒有設置時間，開啟設置面板
    showTimerSettings()
    return
  }
  
  if (timerRunning.value) {
    await stopTimer()
    // stopTimer 已經會設置房間狀態為 Stop
  } else {
    await startTimer()
    // startTimer 已經會設置房間狀態為 Discussion
    // 同步當前主題和計時狀態到參與者面板
    await setRoomState()
  }
}

async function terminateTimer() {
  // 停止計時器 (內部已經會設置狀態為 Stop)
  await stopTimer()
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

// 房間狀態相關API函數
async function fetchRoomStatus() {
  try {
    // 如果計時器正在運行，不需要頻繁查詢房間狀態
    if (timerRunning.value && roomStatus.value === 'Discussion') {
      return roomStatus.value
    }
    
    const response = await fetch(`${API_BASE_URL}/api/room_status?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    const data = await response.json()
    const status = data.status
    // 只在狀態變化時更新
    if (roomStatus.value !== status) {
      roomStatus.value = status
      console.log(`房間狀態已更新：${status}`) // 便於調試
    }
    
    return status
  } catch (error) {
    console.error('獲取房間狀態失敗:', error)
    roomStatus.value = 'NotFound'
    return 'NotFound'
  }
}

async function setRoomStatus(status) {
  try {
    // 如果狀態沒有變化，不做任何事情
    if (roomStatus.value === status) {
      return
    }
    
    const response = await fetch(`${API_BASE_URL}/api/room_status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        status: status
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    roomStatus.value = status
    showNotification(`房間狀態已更新為：${roomStatusText.value}`, 'success')
  } catch (error) {
    console.error('設置房間狀態失敗:', error)
    showNotification('設置房間狀態失敗', 'error')
  }
}

// 新增的切換主題API函數
async function switchTopic(topicName) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_switch_topic`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        topic: topicName
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    if (data.success) {
      showNotification(`已切換到主題：${topicName}`, 'success')
      // 更新房間狀態
      roomStatus.value = data.status
      return true
    } else {
      throw new Error(data.error || '切換主題失敗')
    }
  } catch (error) {
    console.error('切換主題失敗:', error)
    showNotification('切換主題失敗', 'error')
    return false
  }
}

// 主題和計時相關的API函數
async function setRoomState() {
  if (!topics.value[selectedTopicIndex.value]) {
    return
  }
  
  const currentTopic = topics.value[selectedTopicIndex.value].title
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_state`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        topic: currentTopic,
        countdown: initialTime.value,
        time_start: Date.now() / 1000
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    showNotification('主題和計時器已同步到參與者面板', 'success')
  } catch (error) {
    console.error('設置房間狀態失敗:', error)
    showNotification('設置房間狀態失敗', 'error')
  }
}

let roomPoller
let dataPoller
onMounted(async () => {
  loadRoom()
  loadTopics()
  loadTimerSettings() // 載入計時器設置
    
  // 添加窗口大小變化的監聽器
  window.addEventListener('resize', updateQRCodeSize)
  
  // 首次檢查房間狀態，如果房間不存在則返回主頁
  const initialStatus = await fetchRoomStatus()
  if (initialStatus === 'NotFound') {
    showNotification('房間不存在，即將返回主頁', 'error')
    setTimeout(() => {
      router.push('/')
    }, 2000)
    return
  }
  
  // 延遲啟動意見輪詢，確保 loadRoom() 先完成
  setTimeout(() => {
    fetchQuestions() // 首次獲取
    dataPoller = setInterval(fetchQuestions, 5000)
  }, 100)
})

onBeforeUnmount(() => {
  // 組件卸載時清理
  window.removeEventListener('resize', updateQRCodeSize)
  clearInterval(dataPoller)
  clearInterval(roomPoller)
  
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
  height: calc(100vh - 70px - 6rem - 1px);
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

.btn-red {
  background: #ef4444; /* Red */
}

.btn-red:hover {
  background: #dc2626; /* Darker Red */
}

.qrcode-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  animation: fadeIn 0.3s;
  backdrop-filter: blur(4px);
}

.qrcode-modal {
  background: var(--background, #fff);
  border-radius: 1rem;
  width: 98vw;
  max-width: 420px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem 1rem;
  overflow: hidden;
}

.qrcode-modal-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}

.qrcode-modal-body {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qrcode-large {
  background: #fff;
  border-radius: 0.7rem;
  margin-bottom: 1.2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 320px;
  max-height: 320px;
  padding: 1rem;
  box-sizing: border-box;
}

.qrcode-modal-info {
  width: 100%;
  text-align: center;
  font-size: 1rem;
  word-break: break-all;
}

.qrcode-room-code {
  font-size: 1.08rem;
  font-weight: 500;
  color: var(--primary-color, #3451db);
  margin-bottom: 0.3em;
}

.qrcode-link-text {
  color: var(--text-secondary, #666);
  font-size: 0.93em;
  margin-top: 0.4em;
  word-break: break-all;
}

@media (max-width: 500px) {
  .qrcode-modal { max-width: 98vw; padding: 0.7rem 0.2rem; }
  .qrcode-large { max-width: 80vw; max-height: 80vw; padding: 0.4rem; }
}

/* .qrcode-modal-overlay {
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
  max-width: calc(640px + 6rem);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: modalSlideUp 0.3s ease;
} */

/* .qrcode-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
} */

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

/* .qrcode-modal-body {
  padding: clamp(1rem, 5vw, 1.5rem);
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
  max-height: 80vh;
} */

/* .qrcode-large {
  background: white;
  padding: clamp(1rem, 4%, 1.5rem);
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
  width: auto;
  max-width: 100%;
  overflow: hidden;
} */

/* .qrcode-modal-info {
  width: 100%;
  text-align: center;
} */

/* .qrcode-room-code {
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
} */

/* .qrcode-link-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  word-break: break-all;
} */

/* 房間狀態樣式 */
.room-status {
  margin-left: 1rem;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.9rem;
  background-color: #f0f0f0;
}

.status-notfound {
  background-color: #e5e5e5;
  color: #666666;
}

.status-stop {
  background-color: #fef3c7;
  color: #b45309;
}

.status-discussion {
  background-color: #dcfce7;
  color: #166534;
}

.status-end {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
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

/* 票數顯示樣式 */
.question-votes {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 意見資訊樣式 */
.question-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
}

.question-nickname {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: var(--primary-color);
  font-weight: 500;
}

.question-nickname i {
  font-size: 0.875rem;
  color: var(--primary-color);
}

.question-time {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 調整 question-meta 布局 */
.question-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 12px;
  gap: 16px;
}

/* 響應式調整 */
@media (max-width: 768px) {
  .question-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .question-info {
    align-items: flex-start;
    width: 100%;
  }
}
</style>