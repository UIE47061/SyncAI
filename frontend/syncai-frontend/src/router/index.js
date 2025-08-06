import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import HostPanel from '../components/HostPanel.vue'
import ParticipantPanel from '../components/ParticipantPanel.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/host', component: HostPanel },
  { path: '/participant', component: ParticipantPanel }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
