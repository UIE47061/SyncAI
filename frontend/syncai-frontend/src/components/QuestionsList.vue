<template>
  <div class="questions-panel">
    <div class="panel-header">
      <h2>意見列表 - {{ currentTopicTitle }}</h2>
      <div class="panel-controls">
        <select v-model="localSortBy" class="sort-options" @change="updateSortBy">
          <option value="votes">按票數排序</option>
          <option value="time">按時間排序</option>
        </select>
        <button class="btn-qrcode" id="summary-btn" @click="summaryAI" :title="`統整主題「${currentTopicTitle}」的意見`">
          AI統整
        </button>
        <button class="btn-red btn-qrcode" @click="clearAllQuestions" :title="`清空主題「${currentTopicTitle}」的所有評論`">
          <i class="fa-solid fa-trash-can"></i>
          清空評論
        </button>
      </div>
    </div>
    <div class="questions-container">
      <template v-if="sortedQuestions.length === 0">
        <div class="empty-state">
          <div class="empty-icon">
            <i class="fa-regular fa-comment-dots"></i>
          </div>
          <h3>等待參與者提問</h3>
          <p>分享會議室代碼讓參與者加入並開始提問</p>
        </div>
      </template>
      <template v-else>
        <div
          v-for="q in sortedQuestions"
          :key="q.id"
          :class="['question-item', { 'ai-summary-item': q.isAISummary }]"
        >
          <!-- AI 總結樣式 -->
          <template v-if="q.isAISummary">
            <div class="question-header">
              <div class="question-text">
                <h3><i class="fa-solid fa-robot"></i> AI 會議總結</h3>
                <div class="ai-content" v-html="q.content.replace(/\\n/g, '<br>')"></div>
              </div>
              <div class="question-actions">
                <button class="btn-icon" @click="deleteQuestion(q.id)" title="刪除此總結">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </div>
            <div class="question-meta">
              <div class="question-info">
                <div class="question-time">{{ formatTime(q.ts) }}</div>
              </div>
            </div>
          </template>

          <!-- 一般留言樣式 -->
          <template v-else>
            <div class="question-header">
              <div class="question-text" v-html="escapeHtml(q.content)"></div>
              <div class="question-actions">
                <button class="btn-icon" @click="deleteQuestion(q.id)" title="刪除意見">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </div>
            <div class="question-meta">
              <div class="question-votes">
                <span class="vote-item"><i class="fa-solid fa-thumbs-up"></i> {{ q.vote_good || 0 }}</span>
                <span class="vote-item"><i class="fa-solid fa-thumbs-down"></i> {{ q.vote_bad || 0 }}</span>
              </div>
              <div class="question-info">
                <div class="question-nickname" v-if="q.nickname"><i class="fa-regular fa-user"></i> {{ q.nickname }}</div>
                <div class="question-time">{{ formatTime(q.ts) }}</div>
              </div>
            </div>
          </template>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  questions: {
    type: Array,
    required: true
  },
  currentTopicTitle: {
    type: String,
    required: true
  },
  sortBy: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['delete-question', 'summary-ai', 'clear-all-questions', 'update-sort-by'])

const localSortBy = ref(props.sortBy)

// 監聽父組件的 sortBy 變化
watch(() => props.sortBy, (newValue) => {
  localSortBy.value = newValue
})

const sortedQuestions = computed(() => {
  // 1. 先將 AI 總結和一般留言分開
  const aiSummaries = props.questions.filter(q => q.isAISummary)
  const normalQuestions = props.questions.filter(q => !q.isAISummary)

  // 2. 只對一般留言進行排序
  const sortedNormal = [...normalQuestions].sort((a, b) => {
    if (localSortBy.value === 'votes') {
      const aVotes = (a.vote_good || 0) - (a.vote_bad || 0)
      const bVotes = (b.vote_good || 0) - (b.vote_bad || 0)
      if (bVotes !== aVotes) return bVotes - aVotes
    }
    // 時間排序
    return (b.ts || 0) - (a.ts || 0)
  })

  // 3. 最後，將 AI 總結放回陣列的最前面
  return [...aiSummaries, ...sortedNormal]
})

function updateSortBy() {
  emit('update-sort-by', localSortBy.value)
}

function deleteQuestion(id) {
  emit('delete-question', id)
}

function summaryAI() {
  emit('summary-ai')
}

function clearAllQuestions() {
  emit('clear-all-questions')
}

function formatTime(dateString) {
  const date = new Date(dateString * 1000)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '剛剛'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分鐘前`
  return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  // 處理換行符號，將 \n 轉換為 <br>
  return div.innerHTML.replace(/\\n/g, '<br>')
}
</script>

<style scoped>
.questions-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 1rem;
  overflow: hidden;
}

.panel-header {
  padding: 1.3rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--background);
}

.panel-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.panel-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.sort-options {
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.btn-qrcode {
  background: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}

.btn-qrcode:hover {
  background: var(--primary-hover);
  color: white;
}

.btn-red {
  background: #ef4444;
}

.btn-red:hover {
  background: #dc2626;
}

.questions-container {
  height: calc(100% - 80px);
  overflow-y: auto;
  padding: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.question-item {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  transition: all 0.2s;
}

.question-item:hover {
  border-color: var(--primary-color);
  box-shadow: var(--shadow);
}

.ai-summary-item {
  background: var(--ai-summary-background);
  border: 1px solid var(--ai-summary-border-color);
  border-left: 5px solid var(--ai-summary-accent-border-color);
  box-shadow: 0 4px 12px var(--ai-summary-shadow-color);
  animation: fadeInHighlight 0.5s ease;
}

.ai-summary-item h3 {
  color: var(--ai-summary-header-color);
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 1.15em;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-summary-item .ai-content {
  color: var(--ai-summary-content-color);
  line-height: 1.6;
  font-size: 0.95em;
}

@keyframes fadeInHighlight {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.question-text {
  font-weight: 500;
  color: var(--text-primary);
  flex: 1;
  margin-right: 1rem;
}

.question-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-secondary);
  border-radius: 0.25rem;
  transition: color 0.2s;
}

.btn-icon:hover {
  background: var(--surface);
}

.question-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 12px;
  gap: 16px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.question-votes {
  display: flex;
  gap: 12px;
  align-items: center;
  gap: 0.25rem;
  background: var(--primary-color);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.vote-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.question-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-end;
}

.question-nickname {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: var(--primary-color);
  font-weight: 500;
}

.question-nickname i {
  font-size: 0.875rem;
  color: var(--primary-color);
}

/* 響應式調整 */
@media (max-width: 1024px) {
  .questions-container { 
    height: 500px; 
  }
}

@media (max-width: 768px) {
  .question-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .question-info {
    align-items: flex-start;
    width: 100%;
  }

  .panel-controls { 
    flex-direction: column; 
    gap: 0.5rem; 
  }
}
</style>