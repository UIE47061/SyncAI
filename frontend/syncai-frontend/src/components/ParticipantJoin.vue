<template>
  <div class="join-bg">
    <div class="join-card">
      <h1>SyncAI 會議參與</h1>
      <p v-if="!joined">請輸入暱稱加入會議（房間：{{ roomId }}）</p>
      <div v-if="!joined" class="input-group">
        <input
          v-model="nickname"
          placeholder="輸入暱稱"
          @keyup.enter="joinMeeting"
          class="rwd-input"
        />
        <button :disabled="!nickname" @click="joinMeeting" class="rwd-btn">加入</button>
      </div>
      <div v-else class="waiting">
        <h2>Hi {{ nickname }} 👋</h2>
        <p>你已成功加入會議，請等待主持人開始互動！</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import { useRouter } from 'vue-router'

const router = useRouter()
const nickname = ref('')
const roomId = ref('')
const joined = ref(false)
const deviceId = ref('')

// 自動偵測 API base url
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  roomId.value = urlParams.get('room') || ''

  const deviceIdKey = `syncai_${roomId.value}_device`
  deviceId.value = localStorage.getItem(deviceIdKey) || uuidv4()
  if (!localStorage.getItem(deviceIdKey)) {
    localStorage.setItem(deviceIdKey, deviceId.value)
  }

  setInterval(() => {
    fetch(`${API_BASE}/api/participants/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        room: roomId.value,
        device_id: deviceId.value
      })
    })
  }, 5000)

  setInterval(async () => {
    if (!roomId.value) return
    const res = await fetch(`${API_BASE}/api/room_status?room=${roomId.value}`)
    const data = await res.json()
    if (data.status === 'discussion') {
      router.push({ path: '/participant-discussion', query: { room: roomId.value } })
    }
  }, 2000)
})

const joinMeeting = async () => {
  if (!nickname.value || !roomId.value) return
  try {
    await fetch(`${API_BASE}/api/participants/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        room: roomId.value,
        nickname: nickname.value,
        device_id: deviceId.value
      })
    })
    joined.value = true
  } catch (e) {
    alert('加入失敗，請稍後再試')
  }
}
</script>

<style>
.join-bg {
  min-height: 100vh;
  background: #f4f8fc;
  display: flex;
  justify-content: center;
  align-items: center;
}
.join-card {
  max-width: 400px;
  width: 100%;
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.1);
  padding: 2em;
  text-align: center;
  margin: 1em;
}
.input-group {
  margin: 1.5em 0;
  display: flex;
  gap: 0.7em;
  justify-content: center;
}
.rwd-input {
  font-size: 1.1em;
  width: 70%;
  padding: 0.5em;
  border-radius: 8px;
  border: 1px solid #ccc;
  min-width: 120px;
  max-width: 220px;
  box-sizing: border-box;
}
.rwd-btn {
  background: #007bff;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.5em 1.4em;
  cursor: pointer;
  font-size: 1.1em;
  min-width: 80px;
}
.waiting {
  margin-top: 2em;
}

/* RWD 響應式設計 */
@media (max-width: 600px) {
  .join-card {
    max-width: 100vw;
    border-radius: 0;
    box-shadow: none;
    padding: 1em 0.2em;
    margin: 0;
  }
  .input-group {
    flex-direction: column;
    gap: 0.3em;
    align-items: stretch;
  }
  .rwd-input {
    width: 100%;
    max-width: 100vw;
    min-width: 0;
    font-size: 1em;
  }
  .rwd-btn {
    width: 100%;
    font-size: 1em;
    min-width: 0;
    padding: 0.7em 0;
  }
}
</style>
