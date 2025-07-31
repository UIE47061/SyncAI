<template>
  <div>
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>MeetQ</h1>
          <span>參與者</span>
        </div>
        <div class="nav-actions">
          <span class="room-info">代碼: <strong>{{ roomCode || '------' }}</strong></span>
        </div>
      </div>
    </nav>

    <main class="participant-content">
      <div class="participant-layout">
        <!-- 會議資訊/分享 -->
        <div class="participant-info-panel">
          <h2>會議資訊</h2>
          <div class="info-row">
            <div class="code-qrcode-row">
              <div class="code-col">
                <div class="info-label">會議室代碼</div>
                <div class="code-display">
                  <span class="code-text">{{ roomCode }}</span>
                  <button class="btn-icon" @click="copyRoomCode" title="複製代碼">📋</button>
                </div>
              </div>
              <div class="qrcode-col" v-if="roomLink">
                <qrcode-vue :value="roomLink" :size="90" />
                <div class="qrcode-caption">點擊或掃碼邀朋友</div>
              </div>
            </div>
            <div class="link-row">
              <span class="info-label">加入連結</span>
              <div class="code-display">
                <span class="link-text">{{ roomLink }}</span>
                <button class="btn-icon" @click="copyRoomLink" title="複製連結">📋</button>
              </div>
            </div>
          </div>
        </div>
        <!-- 提問區 -->
        <div class="question-submit-panel">
          <h2>我要提問</h2>
          <form @submit.prevent="submitQuestion">
            <input v-model="newQuestion" placeholder="輸入你的問題" maxlength="80" />
            <button class="btn btn-primary" :disabled="!canSubmit">送出</button>
          </form>
        </div>
        <!-- 問題列表 -->
        <div class="questions-panel">
          <h2>問題列表</h2>
          <div v-if="questions.length === 0" class="empty-state">
            <div class="empty-icon">🤔</div>
            <div>目前沒有問題，趕快發問吧！</div>
          </div>
          <div v-else>
            <div v-for="q in questions" :key="q.id" class="question-item">
              <div class="question-header">
                <span v-html="escapeHtml(q.text)"></span>
                <div class="question-votes">
                  <button class="btn-icon" @click="voteQuestion(q.id)" :disabled="q.answered">
                    👍
                  </button>
                  <span>{{ q.votes || 0 }}</span>
                </div>
              </div>
              <div class="question-meta">
                <span v-if="q.answered" class="answered-tag">已回答</span>
                <span>{{ formatTime(q.createdAt) }}</span>
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
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import QrcodeVue from 'qrcode.vue'

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

const route = useRoute()
const roomCode = ref(route.query.room || '')
const roomLink = ref('')
const questions = ref([])
const newQuestion = ref('')
const notifications = ref([])

const canSubmit = computed(() => !!newQuestion.value.trim())

// 取得會議資訊
onMounted(async () => {
  roomLink.value = `${window.location.protocol}//${window.location.hostname}:5173/participant?room=${roomCode.value}`
  await fetchQuestions()
})

async function fetchQuestions() {
  if (!roomCode.value) return
  try {
    const resp = await fetch(`${API_BASE}/api/questions?room=${roomCode.value}`)
    const data = await resp.json()
    questions.value = data.questions || []
  } catch {
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

function showNotification(text, type = 'info') {
  notifications.value.push({ text, type })
  setTimeout(() => notifications.value.shift(), 4000)
}
function removeNotification(i) {
  notifications.value.splice(i, 1)
}

// 提問
async function submitQuestion() {
  if (!canSubmit.value) return
  try {
    const resp = await fetch(`${API_BASE}/api/questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room: roomCode.value, text: newQuestion.value.trim() })
    })
    if (resp.ok) {
      newQuestion.value = ''
      await fetchQuestions()
      showNotification('問題已送出', 'success')
    } else {
      showNotification('提問失敗', 'error')
    }
  } catch {
    showNotification('提問失敗', 'error')
  }
}

// 投票
async function voteQuestion(qid) {
  try {
    const resp = await fetch(`${API_BASE}/api/questions/vote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ room: roomCode.value, question_id: qid })
    })
    if (resp.ok) {
      await fetchQuestions()
      showNotification('已投票', 'success')
    } else {
      showNotification('投票失敗', 'error')
    }
  } catch {
    showNotification('投票失敗', 'error')
  }
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

// html escape
function escapeHtml(html) {
  if (!html) return ''
  return html.replace(/[<>&"]/g, function(c) {
    return {'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;'}[c]
  })
}
</script>

<style scoped>
/* Navbar */
.navbar {
  background: #222e42;
  color: #fff;
  padding: 0 0 0 12px;
}
.nav-container {
  max-width: 980px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 62px;
}
.nav-brand h1 {
  font-size: 1.32em;
  letter-spacing: 2px;
  font-weight: bold;
  margin-right: 14px;
}
.nav-brand span {
  font-size: 1em;
  color: #7db2ff;
  margin-left: 6px;
}
.room-info {
  color: #b6c6e6;
  font-size: 1.08em;
  margin-right: 18px;
}
.participant-content {
  background: #191c21;
  min-height: calc(100vh - 62px);
  padding: 32px 0;
}
.participant-layout {
  max-width: 940px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.1fr 1fr 1.7fr;
  gap: 26px;
}
@media (max-width: 950px) {
  .participant-layout {
    grid-template-columns: 1fr;
    gap: 18px;
  }
}
/* info panel */
.participant-info-panel {
  background: #262c38;
  border-radius: 11px;
  padding: 22px 20px 18px 20px;
  color: #eee;
  margin-bottom: 8px;
  min-width: 0;
}
.info-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.code-qrcode-row {
  display: flex;
  align-items: flex-start;
  gap: 17px;
}
.code-col {
  flex: 1.5 1 0;
  min-width: 95px;
}
.qrcode-col {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.qrcode-caption {
  font-size: 0.93em;
  color: #aaa;
  margin-top: 4px;
}
.link-row {
  margin-top: 6px;
  flex: 1 1 100%;
}
.info-label {
  font-size: 0.97em;
  color: #9ca7be;
}
.code-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}
.code-text, .link-text {
  font-family: 'Fira Mono', 'Consolas', monospace;
  font-size: 1.07em;
  background: #18191b;
  color: #3c91f6;
  border-radius: 6px;
  padding: 2px 8px;
  letter-spacing: 1.2px;
  max-width: 180px;
  overflow: auto;
}
.btn-icon {
  background: #25272c;
  color: #e1e3ea;
  border: none;
  border-radius: 5px;
  font-size: 1em;
  padding: 4px 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-icon:hover {
  background: #353944;
}
/* 提問區 */
.question-submit-panel {
  background: #242a33;
  border-radius: 11px;
  padding: 20px 20px 14px 20px;
  color: #eee;
}
.question-submit-panel form {
  display: flex;
  gap: 10px;
  margin-top: 12px;
}
.question-submit-panel input {
  flex: 1;
  border-radius: 5px;
  padding: 6px 10px;
  border: 1px solid #2c3340;
  background: #22262b;
  color: #fff;
  font-size: 1em;
}
.btn.btn-primary {
  background: #2d8cf0;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.4em 1.15em;
  font-size: 1em;
  cursor: pointer;
}
.btn.btn-primary:disabled {
  background: #628bba;
  cursor: not-allowed;
}
/* 問題列表 */
.questions-panel {
  background: #23272e;
  border-radius: 11px;
  padding: 20px 18px 13px 18px;
  color: #eee;
  min-width: 0;
}
.question-item {
  border-bottom: 1px solid #31354a;
  padding: 8px 0 7px 0;
}
.question-item:last-child {
  border-bottom: none;
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.question-votes {
  display: flex;
  align-items: center;
  gap: 4px;
}
.answered-tag {
  background: #19c972;
  color: #fff;
  font-size: 0.91em;
  border-radius: 4px;
  padding: 1px 6px;
  margin-right: 7px;
}
.question-meta {
  font-size: 0.97em;
  color: #8fa2b3;
  margin-top: 2px;
  display: flex;
  gap: 13px;
}
.empty-state {
  text-align: center;
  color: #a3b3c2;
  margin-top: 24px;
}
.empty-icon {
  font-size: 2.4em;
  margin-bottom: 5px;
}
/* 通知 */
.notification {
  display: flex;
  align-items: center;
  background: #222e42;
  color: #fff;
  border-radius: 8px;
  padding: 12px 18px;
  box-shadow: 0 2px 16px rgba(40,40,60,0.20);
  font-size: 1.05em;
  margin-bottom: 10px;
  min-width: 180px;
  max-width: 350px;
  word-break: break-all;
  gap: 10px;
}
.notification-success {
  background: #2d8f2d;
}
.notification-error {
  background: #c03b38;
}
.notification-info {
  background: #224270;
}
.notification button {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1.15em;
  cursor: pointer;
  margin-left: 12px;
  line-height: 1;
}
</style>
