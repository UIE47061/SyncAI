<template>
  <div>
    <!-- 導覽列 -->
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>SyncAI</h1>
          <span>互動問答平台</span>
        </div>
        <div class="nav-actions">
          <button class="btn btn-outline" @click="openModal('join')">加入會議</button>
          <button class="btn btn-primary" @click="openModal('create')">建立會議室</button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <section class="hero">
        <div class="hero-content">
          <h2>讓每個聲音都被聽見</h2>
          <p>建立互動會議室，讓參與者匿名提問、投票，讓會議更有參與感</p>
          <div class="hero-actions">
            <button class="btn btn-primary btn-large" @click="openModal('create')">
              <span>➕</span>
              建立新會議室
            </button>
          </div>
        </div>
      </section>
      <section class="features">
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">❓</div>
            <h3>匿名提問</h3>
            <p>參與者可以匿名提出問題，消除發言障礙</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">👍</div>
            <h3>即時投票</h3>
            <p>對問題進行投票，熱門問題自動排序</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>AI即時統整</h3>
            <p>本地AI及時統整大家意見並給出建議</p>
          </div>
        </div>
      </section>
    </main>

    <!-- 建立會議室 Modal -->
    <div class="modal" :class="{ active: showCreateModal }" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>建立新會議室</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="createRoom">
          <div class="form-group">
            <label for="roomTitle">會議室名稱</label>
            <input type="text" id="roomTitle" v-model="createForm.title" required placeholder="輸入會議室名稱" />
          </div>
          <div class="form-group">
            <label for="hostName">主持人姓名</label>
            <input type="text" id="hostName" v-model="createForm.host" required placeholder="輸入您的姓名" />
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
            <button type="submit" class="btn btn-primary">建立會議室</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 加入會議室 Modal -->
    <div class="modal" :class="{ active: showJoinModal }" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>加入會議室</h3>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="joinRoom">
          <div class="form-group">
            <label for="roomCode">會議室代碼</label>
            <input
              type="text"
              id="roomCode"
              v-model="joinCode"
              required
              placeholder="輸入 6 位數代碼"
              maxlength="6"
            />
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
            <button type="submit" class="btn btn-primary">加入會議室</button>
          </div>
        </form>
      </div>
    </div>

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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// --- 只保留這個 API_BASE ---
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `http://${window.location.hostname}:8000`

// --- Modal 狀態 ---
const showCreateModal = ref(false)
const showJoinModal = ref(false)
const createForm = reactive({ title: '', host: '' })
const joinCode = ref('')

// --- 通知 ---
const notifications = ref([])

// --- Modal 開關 ---
function openModal(type) {
  if (type === 'create') showCreateModal.value = true
  if (type === 'join') showJoinModal.value = true
  setTimeout(() => {
    if (type === 'create') document.getElementById('roomTitle')?.focus()
    if (type === 'join') document.getElementById('roomCode')?.focus()
  }, 200)
}
function closeModal() {
  showCreateModal.value = false
  showJoinModal.value = false
}

// --- 建立會議室 ---
async function createRoom() {
  if (!createForm.title.trim() || !createForm.host.trim()) {
    showNotification('請填寫所有必填欄位', 'error')
    return
  }
  try {
    const resp = await fetch(`${API_BASE}/api/rooms`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: createForm.title.trim(),
        host: createForm.host.trim()
      })
    })
    if (!resp.ok) throw new Error("建立失敗")
    const data = await resp.json()
    closeModal()
    createForm.title = ''
    createForm.host = ''
    showNotification(`會議室建立成功！代碼：${data.code || data.room_code}`, 'success')
    setTimeout(() => {
      router.push(`/host?room=${data.code || data.room_code}`)
    }, 1000)
  } catch (err) {
    showNotification('建立會議室失敗，請稍後再試', 'error')
  }
}

// --- 加入會議室 ---
async function joinRoom() {
  const code = joinCode.value.trim().toUpperCase()
  if (!code || code.length !== 6) {
    showNotification('請輸入有效的 6 位數會議室代碼', 'error')
    return
  }
  try {
    const resp = await fetch(`${API_BASE}/api/rooms`)
    const rooms = await resp.json()
    const room = rooms.find(r => r.code === code)
    if (!room) {
      showNotification('找不到該會議室，請檢查代碼是否正確', 'error')
      return
    }
    if (!room.is_active) {
      showNotification('該會議室已結束', 'error')
      return
    }
    closeModal()
    joinCode.value = ''
    showNotification('正在加入會議室...', 'success')
    setTimeout(() => {
      router.push(`/participant?room=${code}`)
    }, 1000)
  } catch (e) {
    showNotification('加入會議室失敗，請稍後再試', 'error')
  }
}

// --- 通知 ---
function showNotification(text, type = 'info') {
  notifications.value.push({ text, type })
  setTimeout(() => notifications.value.shift(), 4000)
}
function removeNotification(i) {
  notifications.value.splice(i, 1)
}
</script>

<style scoped>
@import url('../assets/styles.css');
.fade-enter-active, .fade-leave-active {
  transition: opacity .3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
