import { createApp } from 'vue'
import './assets/layout.css'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Axios 기본 설정
axios.defaults.baseURL = 'http://localhost:8000'

const app = createApp(App)
app.use(router)
app.config.globalProperties.$http = axios
app.mount('#app')
