<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="user-info">
        <h1>🎓 캠퍼스 AI 대시보드</h1>
        <div class="user-details">
          <span class="user-name">{{ userInfo.name }}님</span>
          <span class="user-role" :class="userInfo.role">{{ getRoleText() }}</span>
        </div>
      </div>
      <button @click="logout" class="logout-btn">🚪 로그아웃</button>
    </div>

    <!-- Services Grid -->
    <div class="services-grid">
      <!-- 챗봇 서비스 -->
      <div class="service-card" @click="goToAgent">
        <div class="service-icon">🤖</div>
        <h3>AI 챗봇</h3>
        <p>학교 정보 검색과 실시간 질문 답변</p>
        <div class="service-status available">이용 가능</div>
      </div>

      <!-- PDF 학습 서비스 -->
      <div class="service-card" @click="goToLecture">
        <div class="service-icon">📚</div>
        <h3>PDF 학습 지원</h3>
        <p>강의 자료 요약 및 퀴즈 생성</p>
        <div class="service-status available">이용 가능</div>
      </div>

      <!-- 과제 채점 서비스 (교수만) -->
      <div 
        class="service-card" 
        :class="{ 'disabled': userInfo.role !== 'professor' }"
        @click="goToGrading"
      >
        <div class="service-icon">⚡</div>
        <h3>과제 자동 채점</h3>
        <p>대용량 과제 일괄 채점 및 분석</p>
        <div 
          class="service-status" 
          :class="userInfo.role === 'professor' ? 'available' : 'restricted'"
        >
          {{ userInfo.role === 'professor' ? '이용 가능' : '교수 전용' }}
        </div>
      </div>
    </div>


  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      userInfo: {
        name: '',
        role: ''
      },

    }
  },
  
  mounted() {
    this.loadUserInfo()
  },
  
  methods: {
    loadUserInfo() {
      const token = localStorage.getItem('access_token')
      if (!token) {
        this.$router.push('/')
        return
      }
      
      // 토큰에서 사용자 정보 추출 (실제로는 JWT 디코딩)
      const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')
      this.userInfo = userInfo
      

    },
    
    getRoleText() {
      return this.userInfo.role === 'professor' ? '교수' : '학생'
    },
    
    goToAgent() {
      this.$router.push('/agent')
    },
    
    goToLecture() {
      this.$router.push('/lecture')
    },
    
    goToGrading() {
      if (this.userInfo.role === 'professor') {
        this.$router.push('/grading')
      } else {
        alert('교수만 이용 가능한 서비스입니다.')
      }
    },
    
    async logout() {
      try {
        const token = localStorage.getItem('access_token')
        if (token) {
          await fetch('http://localhost:8000/api/v1/auth/logout', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token })
          })
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_info')
        this.$router.push('/')
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fdff 0%, #e8f4fd 100%);
  padding: 30px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.95);
  padding: 25px 30px;
  border-radius: 20px;
  border: 2px solid #e0f2fe;
  box-shadow: 0 8px 25px rgba(135, 206, 235, 0.15);
}

.user-info h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2rem;
  font-weight: 800;
}

.user-details {
  display: flex;
  gap: 15px;
  align-items: center;
}

.user-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}

.user-role {
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 600;
}

.user-role.professor {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
}

.user-role.student {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
}

.logout-btn {
  padding: 12px 20px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: #c0392b;
  transform: translateY(-2px);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.service-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  border-radius: 20px;
  border: 2px solid #e0f2fe;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.service-card:hover:not(.disabled) {
  transform: translateY(-5px);
  border-color: #87ceeb;
  box-shadow: 0 12px 30px rgba(135, 206, 235, 0.2);
}

.service-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.service-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.service-card h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.5rem;
  font-weight: 700;
}

.service-card p {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

.service-status {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  display: inline-block;
}

.service-status.available {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
  border: 2px solid #28a745;
}

.service-status.restricted {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
  border: 2px solid #dc3545;
}



@media (max-width: 768px) {
  .dashboard {
    padding: 20px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
}
</style>