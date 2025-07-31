<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>Sync_AI</h1>
          <span>主持人面板</span>
        </div>
        <div class="nav-actions">
          <div class="room-info">
            <span class="room-code">代碼: <strong>{{ roomCode || '------' }}</strong></span>
            <span class="participant-count">參與者: <strong>{{ room?.participants ?? 0 }}</strong></span>
          </div>
          <button class="btn btn-outline" @click="endRoom">結束會議</button>
        </div>
      </div>
    </nav>
    
    <main class="host-content">
      <div class="host-layout">
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
                <div class="empty-icon">💭</div>
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
                      {{ q.answered ? '✅' : '⭕' }}
                    </button>
                    <button class="btn-icon" @click="deleteQuestion(q.id)" title="刪除問題">🗑️</button>
                  </div>
                </div>
                <div class="question-meta">
                  <div class="question-votes">
                    👍 {{ q.votes || 0 }}
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
          </div>
          <div class="control-section">
            <h3>分享會議室</h3>
            <div class="share-row">
              <!-- 左側資訊 -->
              <div class="share-options">
                <div class="share-item">
                  <span>會議室代碼</span>
                  <div class="code-display">
                    <span>{{ roomCode }}</span>
                    <button class="btn-icon" @click="copyRoomCode" title="複製代碼">📋</button>
                  </div>
                </div>
              </div>
              <!-- QRCode 右側 -->
              <div class="qrcode-side">
                <qrcode-vue :value="roomLink" :size="100" />
              </div>
            </div>
            <div class="share-item">
                  <span>加入連結</span>
                  <div class="code-display">
                    <span>{{ roomLink }}</span>
                    <button class="btn-icon" @click="copyRoomLink" title="複製連結">📋</button>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import QrcodeVue from 'qrcode.vue'

// 狀態
const room = ref(null)
const roomCode = ref('')
const questions = ref([])
const settings = reactive({ allowQuestions: true, allowVoting: true })
const sortBy = ref('votes')
const notifications = ref([])

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
    rooms.set(roomCode.value, room.value)
    localStorage.setItem('Sync_AI_rooms', JSON.stringify(Array.from(rooms.entries())))
  } catch (e) {
    //
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

// 監聽設定變化自動寫回
watch(settings, saveRoom, { deep: true })

// 輪詢
let poller
onMounted(() => {
  loadRoom()
  poller = setInterval(() => {
    loadRoom()
  }, 3000)
})
</script>

<style scoped>
@import url('../assets/styles.css');
@import url('../assets/host.css');
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
.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
