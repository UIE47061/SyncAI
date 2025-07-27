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

        <section class="host-controls" v-if="meetingActive">
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
          </div>
        </section>
      </main>

      <footer>
        <p>SyncAI Meeting &copy; 2024</p>
      </footer>
    </div>
  </div>
</template>


<script setup>
import { ref } from 'vue'
import QrcodeVue from 'qrcode.vue'

const topic = ref('')
const meetingActive = ref(false)
const roomId = ref('')
const participantUrl = ref('')
const copyButtonText = ref('複製參與者連結')
const linkInput = ref(null)

const generateRoomId = (length = 6) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

const startMeeting = () => {
  if (!topic.value) return
  meetingActive.value = true
  roomId.value = generateRoomId()
  // 建議：區網公開時請用你的電腦 IP
  const baseUrl = window.location.origin + window.location.pathname
  participantUrl.value = `${baseUrl}?room=${roomId.value}`
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
}
</script>

<style src="./assets/style.css"></style>
