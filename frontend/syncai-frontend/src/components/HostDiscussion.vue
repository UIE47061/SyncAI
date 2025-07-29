<template>
  <div class="discussion-bg">
    <div class="discussion-main-card">
      <header style="display: flex; align-items: center; justify-content: space-between;">
        <h1>主題討論控場</h1>
        <!-- 小齒輪按鈕 -->
        <button class="gear-btn" @click="showSetting = !showSetting" title="設定">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
            <path d="M12 15.5A3.5 3.5 0 1 0 12 8.5a3.5 3.5 0 0 0 0 7zm7.43-2.06c.04-.3.07-.61.07-.94s-.03-.64-.07-.94l2.11-1.65a.5.5 0 0 0 .12-.64l-2-3.46a.5.5 0 0 0-.6-.22l-2.49 1a7.03 7.03 0 0 0-1.62-.94l-.38-2.65A.5.5 0 0 0 13 2h-4a.5.5 0 0 0-.5.42l-.38 2.65c-.59.22-1.14.52-1.62.94l-2.49-1a.5.5 0 0 0-.6.22l-2 3.46a.5.5 0 0 0 .12.64l2.11 1.65c-.04.3-.07.61-.07.94s.03.64.07.94l-2.11 1.65a.5.5 0 0 0-.12.64l2 3.46a.5.5 0 0 0 .6.22l2.49-1c.48.42 1.03.72 1.62.94l.38 2.65A.5.5 0 0 0 9 22h4a.5.5 0 0 0 .5-.42l.38-2.65c.59-.22 1.14-.52 1.62-.94l2.49 1a.5.5 0 0 0 .6-.22l2-3.46a.5.5 0 0 0-.12-.64l-2.11-1.65z" fill="#888"/>
          </svg>
        </button>
      </header>

      <!-- 設定區塊：點齒輪才顯示 -->
      <TopicSettingBlock
        v-if="showSetting"
        v-model:topic="topic"
        v-model:timerInput="timerInput"
        v-model:countdownActive="countdownActive"
        v-model:anonymousMode="anonymousMode"
        @start="startTimer"
        @reset="resetTimer"
      />

      <section class="topic-now">
        <h2>目前主題：</h2>
        <div class="current-topic">{{ topic || '（尚未設定主題）' }}</div>
        <div v-if="countdownActive || timeup" class="timer-bar">
          <span v-if="countdownActive" :class="{ 'danger': timeLeft <= 10 }">⏰ {{ timeLeft }} 秒</span>
          <span v-else class="timeout-text">🛑 時間到</span>
        </div>
      </section>

      <section class="comment-area">
        <h3>留言區</h3>
        <div class="comment-list">
          <div class="comment-item" v-for="msg in comments" :key="msg.id">
            <span v-if="!anonymousMode" class="comment-name">{{ msg.nickname }}：</span>
            <span class="comment-content">{{ msg.content }}</span>
          </div>
        </div>
      </section>

      <section v-if="timeup" class="after-timeup">
        <button @click="addTime">＋加 60 秒</button>
        <button @click="aiSummary">AI 統整</button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TopicSettingBlock from './TopicSettingBlock.vue'
import { useRoute } from 'vue-router'

const topic = ref('')
const timerInput = ref(60)
const timeLeft = ref(0)
const countdownActive = ref(false)
const timeup = ref(false)
const anonymousMode = ref(false)
const showSetting = ref(false)
const comments = ref([
  { id: 1, nickname: 'U1', content: '我覺得可以先釐清需求' },
  { id: 2, nickname: 'U2', content: '設計要簡潔，流程流暢！' },
  { id: 3, nickname: 'U3', content: '建議先討論RWD跟留言同步' }
])

let timer = null
const route = useRoute()
const roomId = route.query.room

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

const startTimer = async () => {
  if (!topic.value || timerInput.value <= 0) return
  timeLeft.value = timerInput.value
  countdownActive.value = true
  timeup.value = false
  if (timer) clearInterval(timer)
  const now = Date.now() / 1000
  timer = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
    } else {
      countdownActive.value = false
      timeup.value = true
      clearInterval(timer)
    }
  }, 1000)
  // 同步主題與倒數到後端
  await fetch(`${API_BASE}/api/room_state`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      room: roomId,
      topic: topic.value,
      countdown: timerInput.value,
      time_start: now
    })
  })
  // 通知參與者切畫面
  await fetch(`${API_BASE}/api/room_status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room: roomId, status: 'discussion' })
  })
}

const resetTimer = () => {
  if (timer) clearInterval(timer)
  countdownActive.value = false
  timeup.value = false
  timeLeft.value = 0
}

const addTime = () => {
  timeLeft.value = 60
  countdownActive.value = true
  timeup.value = false
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
    } else {
      countdownActive.value = false
      timeup.value = true
      clearInterval(timer)
    }
  }, 1000)
}

const aiSummary = () => {
  alert('（這裡串接 AI 摘要功能）')
}
</script>

<style scoped>
.gear-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.2em;
  margin-left: 0.5em;
  display: flex;
  align-items: center;
}
.gear-btn svg {
  vertical-align: middle;
}
.discussion-bg {
  min-height: 100vh;
  background: #18191d;
  display: flex;
  justify-content: center;
  align-items: center;
}
.discussion-main-card {
  width: 540px;
  max-width: 98vw;
  background: #222328;
  border-radius: 16px;
  box-shadow: 0 6px 30px rgba(0,0,0,0.18);
  padding: 2.2em 2em 1.2em 2em;
}
header h1 {
  text-align: center;
  font-size: 1.55em;
  margin-bottom: 1em;
  letter-spacing: 1px;
  color: #fff;
}
.topic-setting {
  display: flex;
  align-items: center;
  gap: 0.9em;
  margin-bottom: 1.4em;
}
.topic-setting input[type="text"] {
  flex: 1;
  padding: 0.4em 0.7em;
  border-radius: 7px;
  border: 1px solid #444;
  background: #2c2d33;
  color: #fff;
  font-size: 1em;
}
.topic-setting input[type="number"] {
  padding: 0.35em 0.3em;
  border-radius: 6px;
  border: 1px solid #444;
  background: #2c2d33;
  color: #fff;
  font-size: 1em;
}
.topic-setting button {
  padding: 0.45em 1.1em;
  border-radius: 7px;
  border: none;
  background: #007bff;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  font-size: 1em;
  margin-right: 2px;
}
.topic-setting button:disabled {
  background: #999;
  cursor: not-allowed;
}
.topic-now {
  background: #292a32;
  border-radius: 10px;
  padding: 1em;
  margin-bottom: 1.3em;
}
.current-topic {
  font-size: 1.18em;
  margin: 0.7em 0;
  color: #33aaff;
  font-weight: bold;
  text-align: center;
}
.timer-bar {
  text-align: center;
  font-size: 1.2em;
  margin-top: 0.3em;
}
.timer-bar .danger {
  color: #ff4a4a;
}
.timeout-text {
  color: #ffa200;
  font-weight: bold;
  font-size: 1.1em;
}
.comment-area {
  margin-bottom: 1.2em;
}
.comment-area h3 {
  margin-bottom: 0.8em;
  font-size: 1.07em;
  color: #fff;
}
.comment-list {
  max-height: 220px;
  overflow-y: auto;
  background: #23232b;
  border-radius: 7px;
  padding: 0.7em 1em;
}
.comment-item {
  padding: 0.36em 0;
  font-size: 1.07em;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  color: #fff;
  display: flex;
  align-items: center;
}
.comment-item:last-child {
  border-bottom: none;
}
.comment-name {
  color: #9ecbff;
  margin-right: 0.4em;
  font-size: 1em;
}
.after-timeup {
  text-align: center;
  margin-top: 1.2em;
}
.after-timeup button {
  margin: 0 0.5em;
  background: #ffc04a;
  color: #222;
  border-radius: 7px;
  border: none;
  padding: 0.5em 1.2em;
  font-weight: bold;
  cursor: pointer;
}
@media (max-width: 600px) {
  .discussion-main-card { padding: 1.1em 0.3em; width: 99vw; }
  .topic-setting { flex-direction: column; align-items: stretch; gap: 0.7em; }
}
</style>
