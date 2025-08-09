<template>
  <div>
    <!-- 導覽列 -->
  <nav class="navbar">
      <div class="nav-container">
    <div class="nav-brand" @click="router.push('/')" aria-label="返回主頁">
          <img src="/icon.png" alt="SyncAI" class="brand-icon" />
          <h1>SyncAI</h1>
          <span>參與者</span>
        </div>
        <div class="nav-actions">
          <span class="room-info room-code">代碼: <strong>{{ roomCode || '------' }}</strong></span>
          <!-- 用戶暱稱顯示 -->
          <div class="user-nickname" @click="openNicknameEditModal" title="點擊修改暱稱">
            <i class="fa-solid fa-user"></i>
            <span>{{ currentNickname || '載入中...' }}</span>
            <i class="fa-solid fa-pen edit-icon"></i>
          </div>
          <div class="status-indicator" :class="'status-' + roomStatus.toLowerCase()">
            <i class="status-icon" :class="statusIcon"></i>
            {{ roomStatusText }}
          </div>
          <div class="timer-display" v-if="remainingTime > 0 && roomStatus === 'Discussion'">
            <span class="timer">{{ formattedRemainingTime }}</span>
          </div>
          <!-- 當房間不存在時顯示返回主頁按鈕 -->
          <button 
            v-if="roomStatus === 'NotFound' || roomStatus === 'End'"
            class="btn btn-outline btn-home"
            @click="goHome"
            title="返回主頁"
          >
            <i class="fa-solid fa-home"></i> 返回主頁
          </button>
        </div>
      </div>
    </nav>

    <main class="participant-content">
      <div class="participant-layout">
        <!-- 主題與意見區 - 合併為一個區域 -->
        <div class="topic-questions-container">
          <!-- 當前主題區塊 - 突出顯示 -->
          <div class="topic-section">
            <div class="topic-header">
              <i class="fa-solid fa-lightbulb"></i>
              <h3>當前主題</h3>
            </div>
            <div class="current-topic">
              {{ currentTopic || '等待主持人設定主題' }}
            </div>
          </div>
          
          <!-- 提問面板 -->
          <div class="question-submit-section">
            <form @submit.prevent="submitQuestion">
              <textarea 
                v-model="newQuestion" 
                placeholder="請輸入您的意見..." 
                :disabled="roomStatus !== 'Discussion'"
                rows="3"
                @keydown.ctrl.enter="submitQuestion"
                @keydown.meta.enter="submitQuestion"
              ></textarea>
              <button 
                type="submit" 
                class="btn btn-primary" 
                :disabled="!newQuestion.trim() || roomStatus !== 'Discussion'"
              >
                <i class="fa-solid fa-paper-plane"></i> 提交意見
              </button>
            </form>
          </div>
        </div>
        
        <!-- 意見列表面板 -->
        <div class="questions-panel">
          <div class="info-title">
            <i class="fa-solid fa-comments"></i> 意見列表
          </div>
          
          <div v-if="questions.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="fa-regular fa-comment-dots"></i>
            </div>
            <div class="empty-text">目前還沒有意見。在討論期間，您可以提出意見！</div>
          </div>
          
          <div v-else class="question-list">
            <div v-for="q in sortedQuestions" :key="q.id" class="question-item">
              <div class="question-header">
                <div class="question-meta">
                  <div class="meta-item" v-if="q.nickname">
                    <i class="meta-icon fa-regular fa-user"></i>
                    <span>{{ q.nickname }}</span>
                  </div>
                  <div class="meta-item">
                    <i class="meta-icon fa-regular fa-clock"></i>
                    <span>{{ formatTime(q.ts) }}</span>
                  </div>
                </div>
                <div class="question-left">
                  <div v-if="q.answered" class="answered-tag">
                    <i class="fa-solid fa-check"></i> 已回答
                  </div>
                  <div class="question-votes">
                    <button 
                      class="vote-button vote-good" 
                      @click="voteQuestion(q.id, 'good')" 
                      :disabled="q.answered || roomStatus !== 'Discussion'"
                      :class="{'voted': hasVotedGood(q.id)}"
                    >
                      <i class="vote-icon fa-solid fa-thumbs-up"></i>
                      <span class="vote-count">{{ q.vote_good || 0 }}</span>
                    </button>
                    <button 
                      class="vote-button vote-bad" 
                      @click="voteQuestion(q.id, 'bad')" 
                      :disabled="q.answered || roomStatus !== 'Discussion'"
                      :class="{'voted': hasVotedBad(q.id)}"
                    >
                      <i class="vote-icon fa-solid fa-thumbs-down"></i>
                      <span class="vote-count">{{ q.vote_bad || 0 }}</span>
                    </button>
                  </div>
                </div>
              </div>
              <div class="question-content">
                {{ q.content }}
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

    <!-- 取名視窗 -->
    <div v-if="showNameModal" class="name-modal-overlay" @click.self="useAnonymous">
      <div class="name-modal">
        <div class="name-modal-header">
          <h3>歡迎加入會議室</h3>
          <p>請輸入您的暱稱，或選擇以匿名身份參與</p>
        </div>
        <div class="name-modal-body">
          <div class="nickname-input-group">
            <input 
              v-model="userNickname" 
              @keyup.enter="confirmNickname"
              @keyup.esc="useAnonymous"
              placeholder="輸入您的暱稱..."
              class="nickname-input"
              maxlength="10"
              ref="nicknameInput"
            />
            <div class="input-hint">最多 10 個字元</div>
          </div>
          <div class="name-modal-actions">
            <button @click="confirmNickname" class="btn btn-primary">
              <i class="fa-solid fa-check"></i>
              {{ userNickname.trim() ? '使用此暱稱' : '匿名參與' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 暱稱編輯視窗 -->
    <div v-if="showNicknameEditModal" class="nickname-edit-modal-overlay" @click.self="closeNicknameEditModal">
      <div class="nickname-edit-modal">
        <div class="nickname-edit-modal-header">
          <h3>修改暱稱</h3>
          <button class="btn-close" @click="closeNicknameEditModal">&times;</button>
        </div>
        <div class="nickname-edit-modal-body">
          <div class="nickname-edit-input-group">
            <label for="nicknameEdit">新暱稱</label>
            <input 
              id="nicknameEdit"
              v-model="newNicknameInput" 
              @keyup.enter="confirmNicknameEdit"
              @keyup.esc="closeNicknameEditModal"
              placeholder="輸入新的暱稱..."
              class="nickname-edit-input"
              maxlength="10"
            />
            <div class="input-hint">最多 10 個字元，留空則自動產生匿名名稱</div>
          </div>
          <div class="nickname-edit-modal-actions">
            <button @click="confirmNicknameEdit" class="btn btn-primary">
              <i class="fa-solid fa-check"></i>
              確認修改
            </button>
            <button @click="closeNicknameEditModal" class="btn btn-outline">
              <i class="fa-solid fa-xmark"></i>
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'

// API 基礎 URL 設定
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`  // 根據實際後端服務的地址和端口進行調整

const route = useRoute()
const router = useRouter()
const roomCode = ref(route.query.room || '')
const roomLink = ref('')
const questions = ref([])
const newQuestion = ref('')
const notifications = ref([])
const roomStatus = ref('NotFound')
const currentTopic = ref('')
const remainingTime = ref(0)
const votedQuestions = ref({ good: new Set(), bad: new Set() })
const questionSort = ref('latest')

// 取名相關狀態
const showNameModal = ref(false)
const userNickname = ref('')

// 暱稱編輯相關狀態
const showNicknameEditModal = ref(false)
const currentNickname = ref('')
const newNicknameInput = ref('')
const roomNicknameKey = `nickname_${roomCode.value}`

// 計算屬性
const canSubmit = computed(() => !!newQuestion.value.trim() && roomStatus.value === 'Discussion')

// 排序後的意見列表
const sortedQuestions = computed(() => {
  if (questionSort.value === 'votes') {
    return [...questions.value].sort((a, b) => (b.vote_good || 0) - (a.vote_good || 0))
  } else {
    return [...questions.value].sort((a, b) => (b.ts || 0) - (a.ts || 0))
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

// 檢查是否已投好評
function hasVotedGood(questionId) {
  return votedQuestions.value.good.has(questionId)
}

// 檢查是否已投差評
function hasVotedBad(questionId) {
  return votedQuestions.value.bad.has(questionId)
}

// 檢查是否已投票（保持兼容性）
function hasVoted(questionId) {
  return hasVotedGood(questionId) || hasVotedBad(questionId)
}

// 取得會議資訊
onMounted(async () => {
  roomLink.value = `${window.location.protocol}//${window.location.hostname}:5173/participant?room=${roomCode.value}`
  
  // 如果沒有房間代碼，直接返回主頁
  if (!roomCode.value) {
    showNotification('請提供房間代碼', 'error')
    setTimeout(() => {
      router.push('/')
    }, 2000)
    return
  }
  
  // 初始檢查房間狀態
  const initialStatus = await fetchRoomStatus()
  
  // 如果房間不存在，顯示提示並返回主頁，不顯示取名視窗
  if (initialStatus === 'NotFound') {
    showNotification('該房間尚未建立，即將返回主頁！', 'error')
    setTimeout(() => {
      router.push('/')
    }, 3000) // 3秒後自動返回主頁
    return
  }
  
  // 房間存在時才檢查是否需要顯示取名視窗
  await checkAndShowNameModal()

  // 繼續加載其他數據
  await Promise.all([
    fetchQuestions(),
    fetchRoomState()
  ])
  
  // 設置定時輪詢
  startPolling()
})

// 開始數據輪詢
let questionsPoller, statusPoller, statePoller, heartbeatPoller, localTimerPoller
function startPolling() {
  // 每 3 秒輪詢一次房間狀態
  statusPoller = setInterval(fetchRoomStatus, 3000)
  
  // 每 5 秒輪詢一次房間主題和計時器狀態（降低輪詢頻率）
  statePoller = setInterval(fetchRoomState, 5000)
  
  // 每 10 秒輪詢一次意見列表作為備份
  questionsPoller = setInterval(fetchQuestions, 10000)
  
  // 每秒更新本地計時器（避免跳動）
  localTimerPoller = setInterval(() => {
    if (remainingTime.value > 0 && roomStatus.value === 'Discussion') {
      remainingTime.value = Math.max(0, remainingTime.value - 1)
    }
  }, 1000)
}

// 清理輪詢器
onBeforeUnmount(() => {
  clearAllPolling()
  // 確保恢復頁面滾動
  document.body.style.overflow = ''
})

// 清理所有輪詢
function clearAllPolling() {
  clearInterval(questionsPoller)
  clearInterval(statusPoller)
  clearInterval(statePoller)
  clearInterval(heartbeatPoller)
  clearInterval(localTimerPoller)
}

// 檢查是否需要顯示取名視窗
async function checkAndShowNameModal() {
  // 檢查是否已有該房間的暱稱記錄
  const savedNickname = localStorage.getItem(roomNicknameKey)
  
  if (!savedNickname) {
    // 首次進入此房間，顯示取名視窗
    showNameModal.value = true
    // 阻止背景滾動
    document.body.style.overflow = 'hidden'
    // 等待 DOM 更新後聚焦到輸入框
    await nextTick()
    const input = document.querySelector('.nickname-input')
    if (input) {
      input.focus()
    }
    // 等待使用者取名，不立即註冊心跳服務
  } else {
    // 已有暱稱記錄，直接使用並註冊心跳服務
    currentNickname.value = savedNickname
    registerHeartbeat()
  }
}

// 開啟暱稱編輯視窗
async function openNicknameEditModal() {
  const nickname = localStorage.getItem(roomNicknameKey) || ''
  currentNickname.value = nickname
  newNicknameInput.value = nickname
  showNicknameEditModal.value = true
  // 阻止背景滾動
  document.body.style.overflow = 'hidden'
  // 等待 DOM 更新後聚焦到輸入框
  await nextTick()
  const input = document.querySelector('.nickname-edit-input')
  if (input) {
    input.focus()
    input.select() // 選中所有文字
  }
}

// 確認暱稱修改
async function confirmNicknameEdit() {
  const trimmedName = newNicknameInput.value.trim()
  let finalNickname = ''
  
  if (trimmedName) {
    finalNickname = trimmedName
  } else {
    // 使用匿名（隨機訪客）
    finalNickname = `訪客${Math.floor(Math.random() * 10000)}`
  }
  
  // 如果暱稱沒有改變，直接關閉
  if (finalNickname === currentNickname.value) {
    closeNicknameEditModal()
    return
  }
  
  try {
    const deviceId = localStorage.getItem('device_id')
    if (!deviceId) {
      showNotification('設備ID不存在，請重新載入頁面', 'error')
      return
    }
    
    // 調用 API 更新暱稱
    const response = await fetch(`${API_BASE_URL}/api/participants/update_nickname`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        room: roomCode.value,
        device_id: deviceId,
        old_nickname: currentNickname.value,
        new_nickname: finalNickname
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      // 更新本地存儲和顯示
      localStorage.setItem(roomNicknameKey, finalNickname)
      currentNickname.value = finalNickname
      
      // 關閉視窗
      closeNicknameEditModal()
      
      // 顯示成功訊息
      const message = result.updated_comments_count > 0 
        ? `暱稱已更新為「${finalNickname}」，同時更新了 ${result.updated_comments_count} 則留言`
        : `暱稱已更新為「${finalNickname}」`
      
      showNotification(message, 'success')
      
      // 重新獲取意見列表以同步更新
      await fetchQuestions()
    } else {
      showNotification(result.error || '更新暱稱失敗', 'error')
    }
  } catch (error) {
    console.error('更新暱稱失敗:', error)
    showNotification('更新暱稱失敗，請稍後再試', 'error')
  }
}

// 關閉暱稱編輯視窗
function closeNicknameEditModal() {
  showNicknameEditModal.value = false
  document.body.style.overflow = ''
  newNicknameInput.value = ''
}

// 確認暱稱
function confirmNickname() {
  const trimmedName = userNickname.value.trim()
  let finalNickname = ''
  
  if (trimmedName) {
    finalNickname = trimmedName
  } else {
    // 使用匿名（隨機訪客）
    finalNickname = `訪客${Math.floor(Math.random() * 10000)}`
  }
  
  // 同時保存該房間的暱稱記錄
  localStorage.setItem(roomNicknameKey, finalNickname)
  
  // 更新當前暱稱顯示
  currentNickname.value = finalNickname
  
  // 關閉視窗
  showNameModal.value = false
  
  // 恢復頁面滾動
  document.body.style.overflow = ''
  
  // 顯示確認訊息
  if (trimmedName) {
    showNotification(`歡迎，${finalNickname}！`, 'success')
  } else {
    showNotification(`以匿名身份進入會議室`, 'info')
  }
  
  // 取名完成後，註冊心跳服務
  registerHeartbeat()
}

// 使用匿名身份
function useAnonymous() {
  userNickname.value = '' // 清空輸入
  confirmNickname() // 執行確認邏輯
}

// 註冊心跳服務
function registerHeartbeat() {
  // 生成唯一設備ID
  const deviceId = localStorage.getItem('device_id') || `device_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
  localStorage.setItem('device_id', deviceId)
  
  // 註冊參與者
  joinRoom(deviceId)
  
  // 設置心跳，每 3 秒發送一次
  heartbeatPoller = setInterval(() => sendHeartbeat(deviceId), 3000)
}

// 加入房間
async function joinRoom(deviceId) {
  if (!roomCode.value) return
  
  try {
    const nickname = localStorage.getItem(roomNicknameKey)
    
    // 確保有暱稱才加入房間
    if (!nickname) {
      console.error('沒有暱稱無法加入房間')
      return
    }

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
  if (!roomCode.value) return 'NotFound'
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_status?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    roomStatus.value = data.status
    
    // 如果在輪詢中檢測到房間不存在，停止輪詢
    if (data.status === 'NotFound') {
      clearAllPolling()
    }
    
    return data.status
  } catch (error) {
    console.error('獲取房間狀態失敗:', error)
    roomStatus.value = 'NotFound'
    return 'NotFound'
  }
}

// 獲取房間主題、計時器狀態、名稱
async function fetchRoomState() {
  if (!roomCode.value) return

  currentNickname.value = localStorage.getItem(roomNicknameKey) || '匿名'
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/room_state?room=${roomCode.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    const previousTopic = currentTopic.value
    currentTopic.value = data.topic || '等待主持人設定主題'
    
    // 如果主題改變了，更新意見列表
    if (previousTopic !== currentTopic.value && data.comments) {
      questions.value = data.comments || []
      // 獲取用戶投票記錄
      await fetchUserVotes()
    }
    
    // 如果房間狀態為結束或停止，計時器設為0
    if (roomStatus.value === 'End' || roomStatus.value === 'Stop') {
      remainingTime.value = 0
    } else {
      remainingTime.value = data.countdown || 0
    }
    
    return data
  } catch (error) {
    console.error('獲取房間狀態失敗:', error)
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
    
    // 獲取用戶投票記錄
    await fetchUserVotes()
  } catch (error) {
    console.error('獲取意見列表失敗:', error)
    questions.value = []
  }
}

// 獲取用戶投票記錄
async function fetchUserVotes() {
  if (!roomCode.value) return
  
  try {
    const deviceId = localStorage.getItem('device_id')
    if (!deviceId) return
    
    const response = await fetch(`${API_BASE_URL}/api/questions/votes?room=${roomCode.value}&device_id=${deviceId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    votedQuestions.value.good = new Set(data.voted_good || [])
    votedQuestions.value.bad = new Set(data.voted_bad || [])
  } catch (error) {
    console.error('獲取投票記錄失敗:', error)
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

// 提交意見
async function submitQuestion() {
  if (!newQuestion.value || !roomCode.value) return
  
  // 檢查提交頻率限制 (防止垃圾訊息)
  const lastSubmitTime = localStorage.getItem('lastQuestionSubmitTime')
  const currentTime = Date.now()
  
  if (lastSubmitTime && (currentTime - parseInt(lastSubmitTime)) < 3000) {
    showNotification('請稍候再提交意見', 'info')
    return
  }
  
  try {
    const deviceId = localStorage.getItem('device_id')
    const nickname = localStorage.getItem(roomNicknameKey) || '匿名'
    
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
    showNotification('意見已提交', 'success')
  } catch (error) {
    console.error('提交意見失敗:', error)
    showNotification('提交意見失敗，請稍後再試', 'error')
  }
}

// 投票意見
async function voteQuestion(questionId, voteType = 'good') {
  if (!roomCode.value || !questionId) return
  
  try {
    const deviceId = localStorage.getItem('device_id') || `device_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`
    localStorage.setItem('device_id', deviceId)
    
    // 檢查是否已經投過該類型的票
    const isVoted = voteType === 'good' ? hasVotedGood(questionId) : hasVotedBad(questionId)
    const method = isVoted ? 'DELETE' : 'POST'
    
    const response = await fetch(`${API_BASE_URL}/api/questions/vote`, {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ 
        room: roomCode.value, 
        comment_id: questionId,
        device_id: deviceId,
        vote_type: voteType
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (!data.success) {
      if (data.already_voted) {
        showNotification(`您已經投過${voteType === 'good' ? '好評' : '差評'}了`, 'info')
      } else {
        showNotification(data.error || '投票操作失敗', 'error')
      }
      return
    }
    
    // 更新本地投票狀態
    if (isVoted) {
      // 取消投票
      if (voteType === 'good') {
        votedQuestions.value.good.delete(questionId)
        showNotification('已取消好評', 'success')
      } else {
        votedQuestions.value.bad.delete(questionId)
        showNotification('已取消差評', 'success')
      }
    } else {
      // 新增投票
      if (voteType === 'good') {
        votedQuestions.value.good.add(questionId)
        // 如果之前投了差評，移除差評記錄
        votedQuestions.value.bad.delete(questionId)
        showNotification('已投好評', 'success')
      } else {
        votedQuestions.value.bad.add(questionId)
        // 如果之前投了好評，移除好評記錄
        votedQuestions.value.good.delete(questionId)
        showNotification('已投差評', 'success')
      }
    }
    
    // 更新意見列表中的投票數
    const question = questions.value.find(q => q.id === questionId)
    if (question) {
      question.vote_good = data.vote_good
      question.vote_bad = data.vote_bad
      question.votes = data.vote_good // 保持兼容性
    }
    
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
    // 如果是 Unix 時間戳（秒），轉為毫秒
    const timestamp = typeof ts === 'number' && ts < 1e12 ? ts * 1000 : ts
    const d = new Date(timestamp)
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  } catch {
    return ''
  }
}

// 返回主頁
function goHome() {
  clearAllPolling()
  router.push('/')
}
</script>

<style scoped>
@import url('../assets/styles.css');

/* 整體布局 - 覆蓋和擴展共享樣式 */
.navbar {
  background: var(--background);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
}

.participant-content {
  padding: 1.5rem 1rem;
}

.participant-layout {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr; /* 手機預設單欄（上下） */
  gap: 24px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.topic-questions-container {
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  box-shadow: var(--shadow);
  padding: 0;
  color: var(--text-primary);
  overflow: hidden;
  transition: all 0.3s ease;
}

.room-info {
  color: #b6c6e6;
  font-size: 1.08em;
}

.room-info strong {
  color: var(--primary-color);
}

/* 合併面板樣式 - 參考主持人頁面配色 */
.topic-questions-container:hover {
  box-shadow: var(--shadow-lg);
}

/* 主題區塊 - 突出但和諧的設計 */
.topic-section {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  padding: 24px 28px;
  position: relative;
  overflow: hidden;
}

.topic-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.topic-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.topic-header i {
  font-size: 1.3rem;
  color: #fbbf24;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.topic-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.current-topic {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  padding: 18px 22px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 1.1rem;
  line-height: 1.6;
  color: #ffffff;
  position: relative;
  z-index: 1;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 提問區塊 - 使用統一的配色 */
.question-submit-section {
  padding: 24px 28px;
  background: var(--background);
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}

.question-header i {
  font-size: 1.1rem;
  color: var(--primary-color);
}

.question-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.question-submit-section form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.question-submit-section textarea {
  border-radius: 0.75rem;
  padding: 12px 16px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}

.question-submit-section textarea:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  background: var(--background);
}

.question-submit-section textarea::placeholder {
  color: var(--text-secondary);
}

.question-submit-section .btn.btn-primary {
  background: var(--primary-color);
  color: #ffffff;
  border: none;
  border-radius: 0.75rem;
  padding: 12px 18px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  box-shadow: var(--shadow);
}

.question-submit-section .btn.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.question-submit-section .btn.btn-primary:disabled {
  background: var(--secondary-color);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* 響應式設計 */

.btn.btn-secondary {
  background: linear-gradient(135deg, #6b7280, #4b5563);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.btn.btn-secondary:hover {
  background: linear-gradient(135deg, #7c8fa5, #5a6575);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
}

.btn-home {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 意見列表 - 統一配色方案 */
.questions-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  box-shadow: var(--shadow);
  padding: 24px 28px;
  color: var(--text-primary);
  min-width: 0;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.questions-panel:hover {
  box-shadow: var(--shadow-lg);
}

.questions-panel .info-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
  padding-bottom: 12px;
}

.questions-panel .info-title i {
  color: var(--primary-color);
  font-size: 1.3rem;
}

.question-list {
  display: grid;
  gap: 16px;
  margin-top: 20px;
}

.question-item {
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  padding: 16px 18px;
  background: var(--background);
  transition: all 0.2s ease;
}

.question-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-votes {
  display: flex;
  align-items: center;
  gap: 8px;
}

.vote-button {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.vote-button:hover:not(:disabled) {
  background: var(--background);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.vote-button.vote-good.voted {
  background: rgba(37, 99, 235, 0.1);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.vote-button.vote-bad.voted {
  background: rgba(220, 38, 38, 0.1);
  color: var(--danger-color);
  border-color: var(--danger-color);
}

.vote-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vote-icon {
  font-size: 1em;
}

.vote-count {
  font-weight: 500;
}

.answered-tag {
  background: rgba(5, 150, 105, 0.1);
  color: var(--success-color);
  font-size: 0.875rem;
  border-radius: 0.375rem;
  padding: 4px 8px;
  margin-right: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  border: 1px solid rgba(5, 150, 105, 0.2);
}

.question-content {
  margin: 12px 0;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
  color: var(--text-primary);
  font-size: 1rem;
}

.question-meta {
  font-size: 0.875rem;
  color: var(--text-secondary);
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-icon {
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  color: var(--text-secondary);
  margin: 50px 0;
  padding: 30px;
  background: var(--surface);
  border-radius: 1rem;
  border: 1px dashed var(--border);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  color: var(--text-secondary);
}

.empty-text {
  font-size: 1.1em;
  max-width: 320px;
  margin: 0 auto;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* 按鈕樣式補充 */
.btn-home {
  display: flex;
  align-items: center;
  gap: 6px;
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
  
  .topic-questions-container {
    border-radius: 12px;
  }
  
  .topic-section {
    padding: 20px 20px;
  }
  
  .question-submit-section {
    padding: 20px 20px;
  }
  
  .topic-header h3 {
    font-size: 1.2rem;
  }
  
  .current-topic {
    padding: 16px 18px;
    font-size: 1.1rem;
  }
  
  .questions-panel {
    padding: 20px 20px;
  }
}

/* 桌面佈局：左右兩欄 */
@media (min-width: 1024px) {
  .participant-layout {
    grid-template-columns: 1fr 1.35fr; /* 左：主題與提問；右：意見列表 */
    align-items: start; /* 避免等高拉伸 */
  }

  /* 兩欄模式下移除左側卡片的下邊距，使用欄間距 */
  .topic-questions-container {
    margin-bottom: 0;
  }

  /* 讓右側卡片不再跨欄，正常佔據第二欄 */
  .questions-panel {
    grid-column: auto;
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
    flex-wrap: nowrap;
  }
  
  .nav-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .topic-section {
    padding: 18px 16px;
  }
  
  .question-submit-section {
    padding: 18px 16px;
  }
  
  .topic-header h3 {
    font-size: 1.1rem;
  }
  
  .current-topic {
    padding: 14px 16px;
    font-size: 1rem;
  }
  
  .questions-panel {
    padding: 18px 16px;
  }
  
  .question-item {
    padding: 16px 18px;
  }
  
  .vote-button {
    padding: 5px 10px;
    font-size: 0.85rem;
  }
}

/* 取名視窗樣式 */
.name-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.2s ease;
}

.name-modal {
  background: var(--background);
  border-radius: 1.25rem;
  width: 90%;
  max-width: 480px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideUp 0.3s ease;
  overflow: hidden;
  border: 1px solid var(--border);
}

.name-modal-header {
  padding: 2rem 2rem 1rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  position: relative;
}

.name-modal-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.name-modal-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  position: relative;
  z-index: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.name-modal-header p {
  font-size: 1rem;
  margin: 0;
  opacity: 0.95;
  position: relative;
  z-index: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.name-modal-body {
  padding: 2rem;
}

.nickname-input-group {
  margin-bottom: 1.5rem;
}

.nickname-input {
  width: 100%;
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.nickname-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15);
  background: var(--background);
}

.nickname-input::placeholder {
  color: var(--text-secondary);
}

.input-hint {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  text-align: center;
}

.name-modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.name-modal-actions .btn {
  padding: 0.875rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
}

.name-modal-actions .btn-primary {
  background: var(--primary-color);
  color: white;
  box-shadow: var(--shadow);
}

.name-modal-actions .btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.name-modal-actions .btn-outline {
  background: transparent;
  border: 2px solid var(--border);
  color: var(--text-secondary);
}

.name-modal-actions .btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
  border-color: var(--text-secondary);
}

@keyframes modalSlideUp {
  from { 
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to { 
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 響應式設計 - 取名視窗 */
@media (max-width: 480px) {
  .name-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .name-modal-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  .name-modal-header h3 {
    font-size: 1.3rem;
  }
  
  .name-modal-header p {
    font-size: 0.95rem;
  }
  
  .name-modal-body {
    padding: 1.5rem;
  }
  
  .nickname-input {
    padding: 0.875rem 1rem;
    font-size: 1rem;
  }
}

/* 用戶暱稱顯示樣式 */
.user-nickname {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 100px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  position: relative;
  max-width: 200px;
}

.user-nickname:hover {
  background: var(--background);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.user-nickname span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  flex: 1;
}

.user-nickname .edit-icon {
  opacity: 0.6;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.user-nickname:hover .edit-icon {
  opacity: 1;
  color: var(--primary-color);
}

/* 暱稱編輯視窗樣式 */
.nickname-edit-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.2s ease;
}

.nickname-edit-modal {
  background: var(--background);
  border-radius: 1rem;
  width: 90%;
  max-width: 450px;
  box-shadow: var(--shadow-lg);
  animation: modalSlideUp 0.3s ease;
  overflow: hidden;
  border: 1px solid var(--border);
}

.nickname-edit-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.nickname-edit-modal-header h3 {
  font-size: 1.25rem;
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
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.btn-close:hover {
  background: var(--border);
  color: var(--text-primary);
}

.nickname-edit-modal-body {
  padding: 2rem;
}

.nickname-edit-input-group {
  margin-bottom: 1.5rem;
}

.nickname-edit-input-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.nickname-edit-input {
  width: 100%;
  padding: 0.875rem 1rem;
  border-radius: 0.5rem;
  border: 2px solid var(--border);
  background: var(--surface);
  color: var(--text-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.nickname-edit-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
  background: var(--background);
}

.nickname-edit-input::placeholder {
  color: var(--text-secondary);
}

.nickname-edit-modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.nickname-edit-modal-actions .btn {
  padding: 0.75rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border: none;
}

.nickname-edit-modal-actions .btn-primary {
  background: var(--primary-color);
  color: white;
}

.nickname-edit-modal-actions .btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow);
}

.nickname-edit-modal-actions .btn-outline {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.nickname-edit-modal-actions .btn-outline:hover {
  background: var(--surface);
  color: var(--text-primary);
  border-color: var(--text-secondary);
}

/* 響應式設計 - 暱稱相關 */
@media (max-width: 768px) {
  .user-nickname {
    max-width: 150px;
    padding: 6px 12px;
    font-size: 0.85rem;
  }
  
  .nickname-edit-modal {
    width: 95%;
    margin: 1rem;
  }
  
  .nickname-edit-modal-header {
    padding: 1.25rem 1.5rem;
  }
  
  .nickname-edit-modal-body {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .user-nickname {
    max-width: 120px;
    padding: 5px 10px;
    font-size: 0.8rem;
  }
  
  .nav-actions {
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .nickname-edit-modal-actions {
    flex-direction: column;
  }
  
  .nickname-edit-modal-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
