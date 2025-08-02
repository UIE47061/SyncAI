<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>SyncAI</h1>
          <span>參與者</span>
        </div>
        <div class="nav-actions">
          <span class="room-info">代碼: <strong>{{ roomCode || '------' }}</strong></span>
          <div class="status-indicator" :class="'status-' + roomStatus.toLowerCase()">
            <i class="status-icon" :class="statusIcon"></i>
            {{ roomStatusText }}
          </div>
          <div class="timer-display" v-if="remainingTime > 0">
            <span class="timer">{{ formattedRemainingTime }}</span>
          </div>
        </div>
      </div>
    </nav>

    <main class="participant-content">
      <div class="participant-layout">
        <!-- 主題與問題區 -->
        <div class="topic-questions-container">
          <!-- 當前主題區塊 -->
          <div class="topic-panel">
            <div class="info-title">
              <i class="fa-solid fa-lightbulb"></i> 當前主題
            </div>
            <div class="current-topic">
              {{ currentTopic || '等待主持人設定主題' }}
            </div>
          </div>
          
          <!-- 提問面板 -->
          <div class="question-submit-panel">
            <div class="info-title">
              <i class="fa-solid fa-message"></i> 提出問題
            </div>
            <form @submit.prevent="submitQuestion">
              <input 
                v-model="newQuestion" 
                placeholder="請輸入您的問題..." 
                :disabled="roomStatus !== 'Discussion'"
              />
              <button 
                type="submit" 
                class="btn btn-primary" 
                :disabled="!newQuestion.trim() || roomStatus !== 'Discussion'"
              >
                <i class="fa-solid fa-paper-plane"></i> 提交問題
              </button>
            </form>
          </div>
        </div>
        
        <!-- 問題列表面板 -->
        <div class="questions-panel">
          <div class="info-title">
            <i class="fa-solid fa-comments"></i> 問題列表
          </div>
          
          <div v-if="questions.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="fa-regular fa-comment-dots"></i>
            </div>
            <div class="empty-text">目前還沒有問題。在討論期間，您可以提出問題！</div>
          </div>
          
          <div v-else class="question-list">
            <div v-for="q in sortedQuestions" :key="q.id" class="question-item">
              <div class="question-header">
                <div v-if="q.answered" class="answered-tag">
                  <i class="fa-solid fa-check"></i> 已回答
                </div>
                <div class="question-votes">
                  <button 
                    class="vote-button" 
                    @click="voteQuestion(q.id)" 
                    :disabled="q.answered || roomStatus !== 'Discussion'"
                    :class="{'voted': hasVoted(q.id)}"
                  >
                    <i class="vote-icon fa-solid fa-thumbs-up"></i>
                    <span class="vote-count">{{ q.votes || 0 }}</span>
                  </button>
                </div>
              </div>
              <div class="question-content">
                {{ q.text }}
              </div>
              <div class="question-meta">
                <div class="meta-item">
                  <i class="meta-icon fa-regular fa-clock"></i>
                  <span>{{ formatTime(q.createdAt) }}</span>
                </div>
                <div class="meta-item" v-if="q.nickname">
                  <i class="meta-icon fa-regular fa-user"></i>
                  <span>{{ q.nickname }}</span>
                </div>
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
        <i v-if="msg.type === 'success'" class="fa-solid fa-check-circle"></i>
        <i v-else-if="msg.type === 'error'" class="fa-solid fa-exclamation-circle"></i>
        <i v-else class="fa-solid fa-info-circle"></i>
        <span>{{ msg.text }}</span>
        <button @click="removeNotification(i)">&times;</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import QrcodeVue from 'qrcode.vue'

// API 基礎 URL 設定
const API_BASE_URL = 'http://localhost:8000' // 根據實際後端服務的地址和端口進行調整

const route = useRoute()
const roomCode = ref(route.query.room || '')
const roomLink = ref('')
const questions = ref([])
const newQuestion = ref('')
const notifications = ref([])
const roomStatus = ref('NotFound')
const currentTopic = ref('')
const remainingTime = ref(0)
const votedQuestions = ref(new Set())
const questionSort = ref('latest')

// 計算屬性
const canSubmit = computed(() => !!newQuestion.value.trim() && roomStatus.value === 'Discussion')

// 排序後的問題列表
const sortedQuestions = computed(() => {
  if (questionSort.value === 'votes') {
    return [...questions.value].sort((a, b) => (b.votes || 0) - (a.votes || 0))
  } else {
    return [...questions.value].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
  }
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

// 格式化剩餘時間
const formattedRemainingTime = computed(() => {
  if (remainingTime.value <= 0) return '00:00:00';
  
  const hours = Math.floor(remainingTime.value / 3600);
  const minutes = Math.floor((remainingTime.value % 3600) / 60);
  const seconds = remainingTime.value % 60;
  
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
})

// 房間狀態圖示
const statusIcon = computed(() => {
  switch(roomStatus.value) {
    case 'Discussion': return 'fa-solid fa-comments';
    case 'Stop': return 'fa-solid fa-pause';
    case 'End': return 'fa-solid fa-flag-checkered';
    case 'NotFound': return 'fa-solid fa-circle-exclamation';
    default: return 'fa-solid fa-question';
  }
})

// 檢查是否已投票
function hasVoted(questionId) {
  return votedQuestions.value.has(questionId)
}

// 取得會議資訊
onMounted(async () => {
  roomLink.value = `${window.location.protocol}//${window.location.hostname}:5173/participant?room=${roomCode.value}`
  
  // 初始加載數據
  await Promise.all([
    fetchQuestions(),
    fetchRoomStatus(),
    fetchRoomState()
  ])
  
  // 設置定時輪詢
  startPolling()
  
  // 註冊心跳服務（保持參與者在線狀態）
  registerHeartbeat()
})

// 開始數據輪詢
let questionsPoller, statusPoller, statePoller, heartbeatPoller
function startPolling() {
  // 每 5 秒輪詢一次問題列表
  questionsPoller = setInterval(fetchQuestions, 5000)
  
  // 每 3 秒輪詢一次房間狀態
  statusPoller = setInterval(fetchRoomStatus, 3000)
  
  // 每 1 秒輪詢一次房間主題和計時器狀態
  statePoller = setInterval(fetchRoomState, 1000)
}

// 清理輪詢器
onBeforeUnmount(() => {
  clearInterval(questionsPoller)
  clearInterval(statusPoller)
  clearInterval(statePoller)
  clearInterval(heartbeatPoller)
})

// 註冊心跳服務
function registerHeartbeat() {
  // 生成唯一設備ID
  const deviceId = localStorage.getItem('device_id') || `device_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
  localStorage.setItem('device_id', deviceId)
  
  // 註冊參與者
  joinRoom(deviceId)
  
  // 設置心跳，每 30 秒發送一次
  heartbeatPoller = setInterval(() => sendHeartbeat(deviceId), 30000)
}

// 加入房間
async function joinRoom(deviceId) {
  if (!roomCode.value) return
  
  try {
    const nickname = localStorage.getItem('nickname') || `訪客${Math.floor(Math.random() * 10000)}`
    localStorage.setItem('nickname', nickname)
    
    const response = await fetch(`${API_BASE_URL}/api/participants/join`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        device_id: deviceId,
        nickname: nickname
      })
    })
    
    if (!response.ok) {
      console.error('加入房間失敗')
    }
  } catch (error) {
    console.error('加入房間錯誤:', error)
  }
}

// 發送心跳
async function sendHeartbeat(deviceId) {
  if (!roomCode.value) return
  
  try {
    await fetch(`${API_BASE_URL}/api/participants/heartbeat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        device_id: deviceId
      })
    })
  } catch (error) {
    console.error('心跳發送錯誤:', error)
  }
}

// 獲取房間狀態
async function fetchRoomStatus() {
  if (!roomCode.value) return
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_status?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    roomStatus.value = data.status
    
    return data.status
  } catch (error) {
    console.error('獲取房間狀態失敗:', error)
    roomStatus.value = 'NotFound'
    return 'NotFound'
  }
}

// 獲取房間主題和計時器狀態
async function fetchRoomState() {
  if (!roomCode.value) return
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_state?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    currentTopic.value = data.topic || '等待主持人設定主題'
    remainingTime.value = data.countdown || 0
    
    return data
  } catch (error) {
    console.error('獲取房間狀態失敗:', error)
  }
}

// 獲取問題列表
async function fetchQuestions() {
  if (!roomCode.value) return
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_comments?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    questions.value = data.questions || []
  } catch (error) {
    console.error('獲取問題列表失敗:', error)
    questions.value = []
  }
}

// 複製會議室代碼
const copyRoomCode = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(roomCode.value)
      showNotification('代碼已複製', 'success')
    } else {
      const tmpInput = document.createElement('input')
      tmpInput.value = roomCode.value
      document.body.appendChild(tmpInput)
      tmpInput.select()
      document.execCommand('copy')
      document.body.removeChild(tmpInput)
      showNotification('代碼已複製', 'success')
    }
  } catch {
    showNotification('複製失敗，請手動複製', 'error')
  }
}

// 複製會議室連結
const copyRoomLink = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(roomLink.value)
      showNotification('連結已複製', 'success')
    } else {
      const tmpInput = document.createElement('input')
      tmpInput.value = roomLink.value
      document.body.appendChild(tmpInput)
      tmpInput.select()
      document.execCommand('copy')
      document.body.removeChild(tmpInput)
      showNotification('連結已複製', 'success')
    }
  } catch {
    showNotification('複製失敗，請手動複製', 'error')
  }
}

// 使用下方定義的 showNotification 函數

// 提問

// 提交問題
async function submitQuestion() {
  if (!newQuestion.value || !roomCode.value) return
  
  // 檢查提交頻率限制 (防止垃圾訊息)
  const lastSubmitTime = localStorage.getItem('lastQuestionSubmitTime')
  const currentTime = Date.now()
  
  if (lastSubmitTime && (currentTime - parseInt(lastSubmitTime)) < 3000) {
    showNotification('請稍候再提交問題', 'info')
    return
  }
  
  try {
    const deviceId = localStorage.getItem('device_id')
    const nickname = localStorage.getItem('nickname') || '匿名'
    
    const response = await fetch(`${API_BASE_URL}/api/room_comment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        room: roomCode.value, 
        content: newQuestion.value,
        nickname: nickname
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    // 記錄最後提交時間
    localStorage.setItem('lastQuestionSubmitTime', currentTime.toString())
    
    newQuestion.value = ''
    await fetchQuestions()
    showNotification('問題已提交', 'success')
  } catch (error) {
    console.error('提交問題失敗:', error)
    showNotification('提交問題失敗，請稍後再試', 'error')
  }
}

// 投票問題
async function voteQuestion(questionId) {
  if (!roomCode.value || !questionId) return
  
  try {
    const deviceId = localStorage.getItem('device_id') || `device_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
    localStorage.setItem('device_id', deviceId)
    
    // 檢查是否已經投過票
    const isVoted = hasVoted(questionId)
    const method = isVoted ? 'DELETE' : 'POST'
    
    const response = await fetch(`${API_BASE_URL}/api/questions/vote`, {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        room: roomCode.value, 
        question_id: questionId,
        device_id: deviceId
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    // 更新本地投票狀態
    if (isVoted) {
      votedQuestions.value.delete(questionId)
    } else {
      votedQuestions.value.add(questionId)
    }
    
    // 更新問題列表
    await fetchQuestions()
    
    showNotification(isVoted ? '已取消投票' : '已投票', 'success')
  } catch (error) {
    console.error('投票操作失敗:', error)
    showNotification('投票操作失敗，請稍後再試', 'error')
  }
}

// 顯示通知

// 顯示通知
function showNotification(text, type = 'info') {
  const notification = { text, type }
  notifications.value.push(notification)
  
  // 3秒後自動移除通知
  setTimeout(() => {
    const index = notifications.value.indexOf(notification)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }, 3000)
}

// 移除通知
function removeNotification(index) {
  notifications.value.splice(index, 1)
}

// 時間格式化
function formatTime(ts) {
  try {
    const d = new Date(ts)
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  } catch {
    return ''
  }
}
</script>

<style scoped>
@import url('../assets/styles.css');
@import url('../assets/participant.css');

/* 整體布局 - 覆蓋和擴展共享樣式 */
.navbar {
  background: var(--background);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
}

/* 其他樣式都在 participant.css 中定義 */

/* 在 styles.css 中定義 */

/* 會議資訊面板 */
.participant-info-panel {
  background: var(--secondary-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  padding: 22px 20px;
  color: #eee;
  margin-bottom: 24px;
  min-width: 0;
  transition: all 0.3s ease;
}

.participant-info-panel:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
  transform: translateY(-2px);
}

.info-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #e2e8f0;
  border-bottom: 1px solid #3b4253;
  padding-bottom: 10px;
}

.info-title i {
  color: #7db2ff;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.code-qrcode-row {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
}

.code-col {
  flex: 1.5 1 0;
  min-width: 180px;
}

.qrcode-col {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
}

.qrcode-caption {
  font-size: 0.93em;
  color: #aaa;
  margin-top: 8px;
}

.link-row {
  margin-top: 16px;
  flex: 1 1 100%;
}

.info-label {
  font-size: 0.97em;
  color: #9ca7be;
  margin-bottom: 6px;
}

.code-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.code-text, .link-text {
  font-family: 'Fira Mono', 'Consolas', monospace;
  font-size: 1.07em;
  background: #18191b;
  color: #3c91f6;
  border-radius: 8px;
  padding: 6px 12px;
  letter-spacing: 1.2px;
  overflow: auto;
  max-width: 100%;
}

.link-text {
  width: 100%;
  overflow-x: auto;
  white-space: nowrap;
}

.btn-icon {
  background: #2d3748;
  color: #e2e8f0;
  border: none;
  border-radius: 6px;
  font-size: 1em;
  padding: 6px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #3a4a63;
  transform: translateY(-2px);
}

.topic-panel {
  background: var(--secondary-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  padding: 22px 20px;
  color: #eee;
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.topic-panel:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
  transform: translateY(-2px);
}

.current-topic {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 14px 18px;
  border-left: 4px solid #7db2ff;
  font-size: 1.2rem;
  line-height: 1.5;
  color: #e2e8f0;
  margin-top: 10px;
}

.topic-container {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 12px 16px;
  border-left: 4px solid #7db2ff;
}

.topic-label {
  color: #9ca7be;
  margin-bottom: 6px;
}

/* 提問區 */
.question-submit-panel {
  background: var(--secondary-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  padding: 22px 20px;
  color: #eee;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.question-submit-panel:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
  transform: translateY(-2px);
}

.question-submit-panel form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.question-submit-panel input {
  border-radius: 8px;
  padding: 10px 14px;
  border: 1px solid #3b4253;
  background: #1e222a;
  color: #fff;
  font-size: 1em;
  transition: all 0.2s ease;
}

.question-submit-panel input:focus {
  border-color: #7db2ff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(125, 178, 255, 0.2);
}

.btn.btn-primary {
  background: linear-gradient(135deg, #3c91f6, #2d8cf0);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 1em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.btn.btn-primary:hover {
  background: linear-gradient(135deg, #4b9ef8, #3a96f3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(45, 140, 240, 0.3);
}

.btn.btn-primary:disabled {
  background: #4a5568;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* 問題列表 */
.questions-panel {
  background: var(--secondary-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  padding: 22px 20px;
  color: #eee;
  min-width: 0;
  grid-column: 1 / -1;
  max-height: 600px;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.questions-panel:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

.question-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.question-item {
  border: 1px solid #31354a;
  border-radius: 8px;
  padding: 14px 16px;
  background: #292f3a;
  transition: all 0.2s ease;
}

.question-item:hover {
  background: #2f3642;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.question-votes {
  display: flex;
  align-items: center;
  gap: 8px;
}

.vote-button {
  background: #2d3748;
  border: none;
  border-radius: 6px;
  padding: 4px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #a0aec0;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.vote-button:hover {
  background: #3a4a63;
}

.vote-button.voted {
  background: rgba(60, 145, 246, 0.2);
  color: #3c91f6;
}

.vote-icon {
  font-size: 1.1em;
}

.vote-count {
  font-weight: 500;
}

.answered-tag {
  background: rgba(25, 201, 114, 0.2);
  color: #19c972;
  font-size: 0.91em;
  border-radius: 4px;
  padding: 3px 8px;
  margin-right: 7px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.question-content {
  margin: 8px 0;
  line-height: 1.5;
  word-break: break-word;
}

.question-meta {
  font-size: 0.92em;
  color: #8fa2b3;
  margin-top: 8px;
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-icon {
  color: #a0aec0;
}

.empty-state {
  text-align: center;
  color: #a3b3c2;
  margin: 40px 0;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
}

.empty-icon {
  font-size: 2.8em;
  margin-bottom: 12px;
  color: #4a5568;
}

.empty-text {
  font-size: 1.05em;
  max-width: 280px;
  margin: 0 auto;
  line-height: 1.5;
}

/* 通知動畫 */
@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .nav-actions {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .question-list {
    grid-template-columns: 1fr;
  }
  
  .status-indicator {
    font-size: 0.9rem;
    padding: 4px 8px;
  }
  
  .timer {
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .participant-content {
    padding: 16px 12px;
  }
  
  .nav-container {
    padding: 0 12px;
    flex-direction: column;
    height: auto;
    padding: 10px;
  }
  
  .nav-brand {
    margin-bottom: 10px;
  }
  
  .nav-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .topic-questions-container {
    gap: 16px;
  }
}
</style>
