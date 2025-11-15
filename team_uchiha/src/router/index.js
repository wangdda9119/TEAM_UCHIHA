import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/HomePage.vue'
import Dashboard from '../components/Dashboard.vue'
import LectureAnalyzer from '../components/LectureAnalyzer.vue'
import AgentInterface from '../components/AgentInterface.vue'
import AssignmentGrader from '../components/AssignmentGrader.vue'

// 로그인 검사 함수
function requireAuth(to, from, next) {
  const token = localStorage.getItem('access_token')
  if (token) {
    next()
  } else {
    next('/')
  }
}

// 교수 권한 검사 함수
function requireProfessor(to, from, next) {
  const token = localStorage.getItem('access_token')
  const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')
  
  if (token && userInfo.role === 'professor') {
    next()
  } else {
    alert('교수만 이용 가능한 서비스입니다.')
    next('/dashboard')
  }
}

const routes = [
  { path: '/', component: HomePage },
  { path: '/dashboard', component: Dashboard, beforeEnter: requireAuth },
  { path: '/lecture', component: LectureAnalyzer, beforeEnter: requireAuth },
  { path: '/agent', component: AgentInterface, beforeEnter: requireAuth },
  { path: '/grading', component: AssignmentGrader, beforeEnter: requireProfessor }
]

export default createRouter({
  history: createWebHistory(),
  routes
})