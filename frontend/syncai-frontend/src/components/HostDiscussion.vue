<template>
  <div class="discussion-bg">
    <!-- 齒輪 -->
    <button class="gear-btn" @click="showSetting = !showSetting" title="設定" aria-label="設定">
      <!-- SVG 齒輪圖示，強烈顯眼 -->
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
        <circle cx="14" cy="14" r="12" fill="#23232b" stroke="#33aaff" stroke-width="2"/>
        <g stroke="#33aaff" stroke-width="2" stroke-linecap="round">
          <path d="M14 6V3"/>
          <path d="M14 25v-3"/>
          <path d="M22 14h3"/>
          <path d="M3 14h3"/>
          <path d="M19.8 8.2l2.1-2.1"/>
          <path d="M6.1 21.9l2.1-2.1"/>
          <path d="M19.8 19.8l2.1 2.1"/>
          <path d="M6.1 6.1l2.1 2.1"/>
        </g>
        <circle cx="14" cy="14" r="4.2" fill="#18191d" stroke="#33aaff" stroke-width="2"/>
      </svg>
    </button>

    <div class="main-row">
      <!-- 主內容區 -->
      <div class="discussion-main-card">
        <header class="discussion-header">
          <h1>主題討論控場</h1>
        </header>

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
            <div class="comment-item" v-for="msg in comments" :key="msg.id || msg.ts || (msg.time + msg.nickname)">
              <!-- 留言顯示是否匿名可依 room 狀態的 anonymous 屬性決定 -->
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

      <!-- 右側：主持人控制面板（浮動 modal） -->
      <transition name="side-panel-fade">
        <div v-if="showSetting" class="overlay" @click.self="showSetting = false">
          <aside class="side-panel" style="display:flex; flex-direction: column; gap: 1.3em; padding: 2em 2.4em; border-radius: 20px; background: #1e2538; box-shadow: 0 8px 24px rgba(0,0,0,0.35); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #cbd5e1;">
            <div class="form-group topic-input" style="display: flex; flex-direction: column; gap: 0.4em;">
              <label for="topic-input" style="font-weight: 600; font-size: 1.05em;">主題</label>
              <input id="topic-input" type="text" v-model="topic" placeholder="請輸入討論主題" style="width: 100%; border-radius: 12px; border: none; padding: 0.6em 1em; font-size: 1em; background: #2a2f4a; color: #e2e8f0; box-shadow: inset 0 0 4px #3b4a6b;" />
            </div>

            <div class="form-group timer-section" style="display: flex; flex-direction: column; gap: 0.8em;">
              <label for="timer-input" style="font-weight: 600; font-size: 1.05em;">時間（分鐘）</label>
              <input id="timer-input" type="number" min="1" v-model="timerInput" style="width: 100%; border-radius: 12px; border: none; padding: 0.55em 1em; font-size: 1em; background: #2a2f4a; color: #e2e8f0; box-shadow: inset 0 0 4px #3b4a6b;" />
              <div class="quick-buttons" style="display: flex; gap: 0.6em; margin-top: 0.2em;">
                <button type="button" @click="timerInput = 5" style="flex: 1; background: #3b4a6b; color: #a5b4fc; border: none; border-radius: 10px; padding: 0.5em 0; font-weight: 600; cursor: pointer; transition: background-color 0.2s;">5 分鐘</button>
                <button type="button" @click="timerInput = 10" style="flex: 1; background: #3b4a6b; color: #a5b4fc; border: none; border-radius: 10px; padding: 0.5em 0; font-weight: 600; cursor: pointer; transition: background-color 0.2s;">10 分鐘</button>
                <button type="button" @click="timerInput = 15" style="flex: 1; background: #3b4a6b; color: #a5b4fc; border: none; border-radius: 10px; padding: 0.5em 0; font-weight: 600; cursor: pointer; transition: background-color 0.2s;">15 分鐘</button>
                <button type="button" @click="timerInput = 30" style="flex: 1; background: #3b4a6b; color: #a5b4fc; border: none; border-radius: 10px; padding: 0.5em 0; font-weight: 600; cursor: pointer; transition: background-color 0.2s;">30 分鐘</button>
              </div>
            </div>

            <div class="form-group anonymous-toggle" style="display: flex; align-items: center; gap: 0.8em; font-weight: 600; font-size: 1em; color: #a5b4fc;">
              <input id="anonymous-checkbox" type="checkbox" v-model="anonymousMode" style="width: 18px; height: 18px; cursor: pointer;" />
              <label for="anonymous-checkbox" style="cursor: pointer; user-select: none;">匿名留言</label>
            </div>

            <button @click="startTimer" style="margin-top: auto; background-color: #3b82f6; color: white; font-weight: 700; font-size: 1.15em; padding: 0.85em 0; border-radius: 16px; border: none; cursor: pointer; width: 100%; box-shadow: 0 4px 12px rgb(59 130 246 / 0.6); transition: background-color 0.3s;">
              啟動倒數
            </button>
          </aside>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import TopicSettingBlock from './TopicSettingBlock.vue'
import { useRoute } from 'vue-router'

const topic = ref('')
const timerInput = ref(60)
const timeLeft = ref(0)
const countdownActive = ref(false)
const timeup = ref(false)
const anonymousMode = ref(false)
const showSetting = ref(false)
// 頁面進入時 side-panel 預設隱藏
onMounted(() => {
  showSetting.value = false
})
// 留言資料，預設為空陣列，動態取得
const comments = ref([])

let timer = null
const route = useRoute()
const roomId = route.query.room

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

let commentsInterval = null

/**
 * 向後端取得留言資料，並寫入 comments
 * 若留言 time 欄位不存在，則補上 new Date().toLocaleTimeString()
 */
async function fetchComments() {
  try {
    // 向 API 取得留言資料
    const res = await fetch(`${API_BASE}/api/room_comments?room=${roomId}`)
    if (!res.ok) return
    const arr = await res.json()
    const list = Array.isArray(arr.comments) ? arr.comments : []
    // 確保每則留言有 time 欄（若無則補 new Date().toLocaleTimeString()）
    comments.value = list.map(msg => ({
      ...msg,
      time: msg.time ? msg.time : new Date().toLocaleTimeString()
    }))
  } catch (e) {
    // 可視需求顯示錯誤訊息
    // console.error('fetchComments error', e)
  }
}

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

// ----- 留言同步邏輯 -----
onMounted(() => {
  // 頁面進入時自動取得留言
  fetchComments()
  // 每 2 秒輪詢同步留言
  commentsInterval = setInterval(fetchComments, 2000)
})
onUnmounted(() => {
  if (commentsInterval) clearInterval(commentsInterval)
})

/**
 * 發送留言後自動刷新留言（請將此函數於 sendComment 或相關流程呼叫）
 * 範例如下：
 *   await sendComment(...)
 *   await fetchComments()
 */
</script>

<style scoped>
.gear-btn {
  background: rgba(30, 40, 60, 0.78);
  border: none;
  cursor: pointer;
  padding: 0.32em 0.45em;
  margin-left: 1em;
  display: flex;
  align-items: center;
  border-radius: 50%;
  transition: box-shadow 0.13s, background 0.15s;
  box-shadow: 0 2px 10px rgba(51,170,255,0.09);
  position: absolute;
  top: 1.2em;
  right: 1.5em;
  z-index: 1001;
}
.gear-btn svg {
  vertical-align: middle;
  filter: drop-shadow(0 0 2px #33aaff88);
}
.gear-btn:hover, .gear-btn:focus {
  background: #23232b;
  box-shadow: 0 0 0 3px #33aaff33;
  outline: none;
}
.discussion-bg {
  min-height: 100vh;
  background: #18191d;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 100vw;
  min-height: 100vh;
  padding: 0;
}
.main-row {
  display: flex;
  flex-direction: row;
  gap: 36px;
  align-items: flex-start;
  width: 100%;
  max-width: 1160px;
  justify-content: center;
}
.discussion-main-card {
  flex: 1 1 540px;
  max-width: 600px;
  min-width: 320px;
  margin: 0 auto;
  background: #222328e6;
  border-radius: 18px;
  box-shadow: 0 8px 36px rgba(0,0,0,0.23), 0 0px 0px 1.5px #33aaff22;
  padding: 2.2em 2em 1.2em 2em;
  z-index: 10;
  position: relative;
}

.discussion-header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.7em;
  margin-bottom: 1.15em;
  position: relative;
}
.discussion-header h1 {
  flex: 1 0 auto;
  font-size: 1.57em;
  margin: 0;
  letter-spacing: 1.2px;
  color: #fff;
  text-align: left;
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

/* 新增 overlay 與浮動 side-panel 樣式 */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(24,25,29,0.72);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5em;
  backdrop-filter: blur(2.5px);
}

.side-panel {
  background: rgba(38,40,55,0.97);
  border-radius: 18px;
  box-shadow: 0 8px 36px rgba(0,0,0,0.25), 0 0 0 1.5px #33aaff44;
  padding: 1.2em 1.3em 1em 1.3em;
  width: 360px;
  max-width: 100vw;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.gear-btn-fixed {
  position: fixed;
  top: 28px;
  right: 36px;
  z-index: 2001;
  background: rgba(30,40,60,0.88);
  border: none;
  border-radius: 50%;
  box-shadow: 0 2px 12px rgba(51,170,255,0.12);
  padding: 0.36em 0.47em;
  cursor: pointer;
  transition: box-shadow 0.15s, background 0.15s;
}
.gear-btn-fixed:hover, .gear-btn-fixed:focus {
  background: #23232b;
  box-shadow: 0 0 0 4px #33aaff44;
}

/* RWD 下，side-panel 保持置中 */
@media (max-width: 1500px) {
  .gear-btn-fixed { 
    top: 11px; right: 8px; 
  }
  .main-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    max-width: 1000vw;
    z-index: 1;
  }
  .discussion-main-card {
    max-width: 98vw;
    margin: 0 auto;
    position: relative;
    z-index: 10;
  }
  .overlay {
    justify-content: center;
    align-items: center;
    padding: 0;
  }
  .side-panel {
    width: 100vw;
    max-width: 100vw;
    border-radius: 14px;
    box-shadow: 0 8px 36px rgba(0,0,0,0.25), 0 0 0 1.5px #33aaff44;
    max-height: 70vh;
    padding: 1.1em 0.9em 0.9em 0.9em;
    background: rgba(30,40,60,0.97);
  }
}
</style>
