<template>
  <div class="discussion-bg">
    <div class="discussion-card">
      <h2>討論進行中</h2>
      <div class="topic-box">
        <span class="label">本題：</span>
        <span class="topic">{{ topic }}</span>
      </div>
      <div class="timer-box">
        <span>剩餘時間：</span>
        <span class="timer">{{ countdown }} 秒</span>
      </div>
      <div class="comment-box">
        <textarea
          v-model="comment"
          placeholder="輸入你的想法或問題..."
          rows="3"
        ></textarea>
        <button class="send-btn" :disabled="!comment.trim()" @click="sendComment">送出留言</button>
        <!-- 之後可綁定送出API -->
      </div>
      <div class="comment-list">
        <div class="comment-item" v-for="msg in comments" :key="msg.ts">
          <span class="comment-name">{{ msg.nickname }}：</span>
          <span class="comment-content">{{ msg.content }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const topic = ref('（等待主持人題目）')
const countdown = ref(60)
const comment = ref('')
const comments = ref([])
const nickname = ref('') // 你可以從 localStorage 或 query 取得
const route = useRoute()
const roomId = route.query.room
let interval = null

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

const fetchRoomState = async () => {
  if (!roomId) return
  const res = await fetch(`${API_BASE}/api/room_state?room=${roomId}`)
  const data = await res.json()
  topic.value = data.topic || '（等待主持人題目）'
  countdown.value = data.countdown
  comments.value = data.comments || []
}

const sendComment = async () => {
  if (!comment.value.trim()) return
  await fetch(`${API_BASE}/api/room_comment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      room: roomId,
      nickname: nickname.value || '匿名',
      content: comment.value
    })
  })
  comment.value = ''
  // 送出後自動刷新留言
  fetchRoomState()
}

onMounted(() => {
  fetchRoomState()
  interval = setInterval(fetchRoomState, 1000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})
</script>

<style scoped>
.discussion-bg {
  min-height: 100vh;
  background: #f4f8fc;
  display: flex;
  justify-content: center;
  align-items: center;
}
.discussion-card {
  max-width: 420px;
  width: 100%;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.1);
  padding: 2em 1.2em;
  text-align: center;
  margin: 1em;
}
.topic-box {
  margin: 1.2em 0 0.8em 0;
  font-size: 1.1em;
}
.topic-box .label {
  color: #888;
  margin-right: 0.5em;
}
.topic {
  font-weight: bold;
  color: #2d8cf0;
}
.timer-box {
  margin-bottom: 1.2em;
  font-size: 1.1em;
}
.timer {
  font-weight: bold;
  color: #e67e22;
  margin-left: 0.5em;
}
.comment-box {
  display: flex;
  flex-direction: column;
  gap: 0.7em;
}
textarea {
  resize: none;
  border-radius: 8px;
  border: 1px solid #ccc;
  padding: 0.7em;
  font-size: 1em;
}
.send-btn {
  background: #2d8cf0;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.6em 0;
  cursor: not-allowed;
  font-size: 1.1em;
}
.comment-list {
  text-align: left;
  margin-top: 1.2em;
}
.comment-item {
  margin-bottom: 0.8em;
}
.comment-name {
  font-weight: bold;
  color: #333;
}
.comment-content {
  color: #555;
}
</style>