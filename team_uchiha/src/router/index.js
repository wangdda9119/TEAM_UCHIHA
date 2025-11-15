import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/HomePage.vue'
import LectureAnalyzer from '../components/LectureAnalyzer.vue'
import AgentInterface from '../components/AgentInterface.vue'

const routes = [
  { path: '/', component: HomePage },
  { path: '/lecture', component: LectureAnalyzer },
  { path: '/agent', component: AgentInterface }
]

export default createRouter({
  history: createWebHistory(),
  routes
})