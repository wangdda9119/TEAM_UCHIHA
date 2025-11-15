<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="header">
      <h1>🎓 UCHIHA AI 대시보드</h1>
      <p class="subtitle">원하는 서비스를 선택하세요</p>
    </div>

    <!-- Service Cards -->
    <div class="services-grid">
      <!-- 1. 챗봇 -->
      <div class="service-card active" @click="$emit('navigate', 'chat')">
        <div class="card-icon">🤖</div>
        <h3>AI 챗봇</h3>
        <p>지능형 AI 에이전트와 대화하고 질문하세요</p>
        <div class="card-status">사용 가능</div>
      </div>

      <!-- 2. 수업자료 요약 및 퀴즈생성 -->
      <div class="service-card" @click="handleComingSoon('수업자료 요약 및 퀴즈생성')">
        <div class="card-icon">📚</div>
        <h3>수업자료 요약 & 퀴즈</h3>
        <p>수업 자료를 요약하고 퀴즈를 자동 생성합니다</p>
        <div class="card-status coming-soon">준비 중</div>
      </div>

      <!-- 3. 과제채점 (교수만) -->
      <div 
        :class="['service-card', { 'disabled': userRole !== 'professor' }]"
        @click="handleRoleRestricted('과제채점', 'professor')"
      >
        <div class="card-icon">📝</div>
        <h3>과제 채점</h3>
        <p>AI를 활용한 자동 과제 채점 시스템</p>
        <div v-if="userRole === 'professor'" class="card-status coming-soon">준비 중</div>
        <div v-else class="card-status restricted">교수 전용</div>
      </div>

      <!-- 4. 강의계획서 생성 (교수만) -->
      <div 
        :class="['service-card', { 'disabled': userRole !== 'professor' }]"
        @click="handleRoleRestricted('강의계획서 생성', 'professor')"
      >
        <div class="card-icon">📋</div>
        <h3>강의계획서 생성</h3>
        <p>AI 기반 강의계획서 자동 생성 및 수정</p>
        <div v-if="userRole === 'professor'" class="card-status coming-soon">준비 중</div>
        <div v-else class="card-status restricted">교수 전용</div>
      </div>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" :class="['status-toast', statusType]">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      userRole: 'student', // 임시로 student 설정 (추후 API에서 가져올 예정)
      statusMessage: '',
      statusType: 'info'
    }
  },
  methods: {
    handleComingSoon(serviceName) {
      this.showStatus(`🚧 ${serviceName} 서비스는 준비 중입니다`, 'info');
    },

    handleRoleRestricted(serviceName, requiredRole) {
      if (this.userRole !== requiredRole) {
        this.showStatus(`🔒 ${serviceName}은 ${requiredRole === 'professor' ? '교수' : '학생'}만 사용할 수 있습니다`, 'error');
        return;
      }
      this.handleComingSoon(serviceName);
    },

    showStatus(message, type = 'info') {
      this.statusMessage = message;
      this.statusType = type;
      setTimeout(() => {
        this.statusMessage = '';
      }, 3000);
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  text-align: center;
  color: white;
  margin-bottom: 50px;
}

.header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
  font-weight: 700;
}

.subtitle {
  font-size: 1.2em;
  opacity: 0.9;
  margin: 0;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

.service-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.service-card.active {
  border: 2px solid #667eea;
}

.service-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.service-card.disabled:hover {
  transform: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-icon {
  font-size: 3em;
  margin-bottom: 20px;
  display: block;
}

.service-card h3 {
  font-size: 1.4em;
  margin: 0 0 15px 0;
  color: #333;
  font-weight: 600;
}

.service-card p {
  color: #666;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.card-status {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.8em;
  font-weight: 600;
}

.card-status {
  background: #e8f5e9;
  color: #388e3c;
}

.card-status.coming-soon {
  background: #fff3e0;
  color: #f57c00;
}

.card-status.restricted {
  background: #ffebee;
  color: #d32f2f;
}

.status-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  font-weight: 500;
  z-index: 1001;
  animation: slideIn 0.3s ease-out;
  max-width: 300px;
}

.status-toast.info {
  background-color: #e3f2fd;
  color: #1976d2;
  border-left: 4px solid #1976d2;
}

.status-toast.error {
  background-color: #ffebee;
  color: #d32f2f;
  border-left: 4px solid #d32f2f;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>