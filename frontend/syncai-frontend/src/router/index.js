import { createRouter, createWebHistory } from 'vue-router'
import HostPage from '../components/HostPage.vue'
import ParticipantJoin from '../components/ParticipantJoin.vue'
import HostDiscussion from '../components/HostDiscussion.vue'
import ParticipantDiscussion from '../components/ParticipantDiscussion.vue'

const routes = [
  { path: '/', component: HostPage },
  { path: '/join', component: ParticipantJoin },
  { path: '/discussion', component: HostDiscussion }, // 主持人討論頁
  { path: '/participant-discussion', component: ParticipantDiscussion } // 參與者討論頁
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
