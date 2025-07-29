<template>
  <div class="app-bg">
    <div class="main-card">
      <header>
        <img src="/logo.png" alt="SyncAI Logo" class="logo" />
        <h1>SyncAI Meeting</h1>
      </header>

      <main>
        <section class="creation-zone" v-if="!meetingActive">
          <h2>開啟新會議</h2>
          <p>請輸入會議議題或主題名稱，即可產生專屬會議室。</p>
          <div class="input-group">
            <input
              type="text"
              v-model.trim="topic"
              @keyup.enter="startMeeting"
              placeholder="例如：2024 Q3 產品開發會議"
            />
            <button @click="startMeeting" :disabled="!topic">開啟會議室</button>
          </div>
        </section>

        <div v-if="meetingActive" class="host-main-row">
          <!-- 左側：參與者名單 Box -->
          <aside class="participant-list-box">
            <h3>已加入參與者</h3>
            <ul>
              <li v-for="p in participants" :key="p.device_id">{{ p.nickname }}</li>
            </ul>
          </aside>

          <!-- 右側：主持人主區 -->
          <section class="host-controls">
            <h2>主持人操作區</h2>
            <div class="info-card">
              <h3>會議主題：{{ topic }}</h3>
              <p>房間 ID：<strong>{{ roomId }}</strong></p>
              <div class="participant-link">
                <input type="text" :value="participantUrl" readonly ref="linkInput" />
                <button @click="copyLink">{{ copyButtonText }}</button>
              </div>
              <div class="qr-code-container">
                <qrcode-vue :value="participantUrl" :size="200" />
                <p>參與者入口 (掃描或複製連結)</p>
              </div>
            </div>
            <div class="control-buttons">
              <button @click="resetMeeting" class="danger">重設會議室</button>
              <button @click="goToDiscussion" class="primary">開始會議</button>
            </div>
          </section>
        </div>
      </main>

      <footer>
        <p>SyncAI Meeting &copy; 2024</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'

const topic = ref('')
const meetingActive = ref(false)
const roomId = ref('')
const hostIp = ref('')
const participantUrl = ref('')
const copyButtonText = ref('複製參與者連結')
const linkInput = ref(null)
const participants = ref([])
let interval = null

const router = useRouter()

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

const fetchParticipants = async () => {
  if (!roomId.value) return
  try {
    const res = await fetch(`${API_BASE}/api/participants?room=${roomId.value}`)
    const data = await res.json()
    participants.value = data.participants || []
  } catch (e) {
    participants.value = []
  }
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/api/hostip`)
    const data = await res.json()
    hostIp.value = data.ip
  } catch (e) {
    hostIp.value = ''
  }
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const generateRoomId = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < 6; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

const startMeeting = () => {
  if (!topic.value || !hostIp.value) return
  meetingActive.value = true
  roomId.value = generateRoomId()
  participantUrl.value = `http://${hostIp.value}:5173/join?room=${roomId.value}`
  fetchParticipants()
  if (interval) clearInterval(interval)
  interval = setInterval(fetchParticipants, 2000) // 2 秒更新一次
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(participantUrl.value)
    copyButtonText.value = '已複製！'
    linkInput.value && linkInput.value.select()
    setTimeout(() => {
      copyButtonText.value = '複製參與者連結'
    }, 2000)
  } catch (err) {
    copyButtonText.value = '複製失敗'
    setTimeout(() => {
      copyButtonText.value = '複製參與者連結'
    }, 2000)
  }
}

const resetMeeting = () => {
  topic.value = ''
  meetingActive.value = false
  roomId.value = ''
  participantUrl.value = ''
  copyButtonText.value = '複製參與者連結'
  if (interval) clearInterval(interval)
  participants.value = []
}

const goToDiscussion = async () => {
  // 先設定房間狀態為 discussion
  await fetch(`${API_BASE}/api/room_status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room: roomId.value, status: 'discussion' })
  })
  router.push({ path: '/discussion', query: { room: roomId.value } })
}
</script>

<style scoped>
.host-main-row {
  display: flex;
  flex-direction: row;
  gap: 32px;
  justify-content: center;
  align-items: flex-start;
  margin-top: 16px;
}

.participant-list-box {
  background: rgba(255,255,255,0.10);
  border-radius: 14px;
  min-width: 160px;
  max-width: 220px;
  padding: 20px 14px 20px 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  border: 1px solid #34363e;
  font-size: 1.09em;
  margin-bottom: 10px;
  color: #fff;
}
.participant-list-box h3 {
  margin-bottom: 1em;
  font-weight: bold;
  text-align: center;
  letter-spacing: 1px;
  font-size: 1.17em;
}
.participant-list-box ul {
  padding: 0;
  margin: 0;
  list-style: none;
}
.participant-list-box li {
  padding: 0.45em 0;
  border-bottom: 1px solid rgba(200,200,200,0.07);
  text-align: center;
}
.participant-list-box li:last-child {
  border-bottom: none;
}

.control-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 18px;
}
.control-buttons .primary {
  background: #2d8cf0;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.5em 1.4em;
  cursor: pointer;
  font-size: 1.1em;
}
.control-buttons .danger {
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.5em 1.4em;
  cursor: pointer;
  font-size: 1.1em;
}

@media (max-width: 700px) {
  .host-main-row {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  .participant-list-box {
    max-width: 100%;
    min-width: 0;
    margin: 0 auto 8px auto;
  }
}
</style>

<style src="../assets/style.css"></style>
