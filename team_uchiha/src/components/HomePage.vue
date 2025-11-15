<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="main-title">AI로 확장되는 <br>당신의 캠퍼스 라이프</h1>
        <p class="sub-title">학교 정보 · 학습지원 · 대용량 과제 채점까지 한 번에.</p>
        <p class="description">내부 RAG, 실시간 검색, PDF 분석 AI가 대학생활을 스마트하게 만든다.</p>
        
        <div class="cta-buttons">
          <button @click="handleLoginClick" class="btn btn-primary-large">
            🔑 로그인
          </button>
          <button @click="handleRegisterClick" class="btn btn-secondary-large">
            📝 회원가입
          </button>
        </div>
        
        <div class="slogan">
          "공부는 너가 하고, 고생은 AI가 한다."
        </div>
      </div>
    </section>

    <!-- Agent Section -->
    <section class="section agent-section">
      <div class="section-content">
        <div class="section-header">
          <h2>🤖 학교생활 도우미 Agent</h2>
          <p>채팅과 음성으로 언제든 질문하세요</p>
        </div>
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">💬</div>
            <h3>채팅/음성 기반</h3>
            <p>텍스트 입력 또는 음성으로 자연스럽게 대화</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🏫</div>
            <h3>협성대 정보 검색</h3>
            <p>내부 RAG로 학교 정보를 정확하게 제공</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🌐</div>
            <h3>실시간 구글 검색</h3>
            <p>최신 정보까지 실시간으로 검색하여 답변</p>
          </div>
        </div>
      </div>
    </section>

    <!-- PDF Learning Section -->
    <section class="section pdf-section">
      <div class="section-content">
        <div class="section-header">
          <h2>📖 PDF 학습 지원 AI</h2>
          <p>강의 자료를 스마트하게 분석하고 학습을 도와드립니다</p>
        </div>
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">📝</div>
            <h3>단원별 요약</h3>
            <p>PDF를 자동으로 분석하여 단원별로 핵심 내용 요약</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🔑</div>
            <h3>핵심 키워드 추출</h3>
            <p>중요한 개념과 키워드를 자동으로 추출</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">❓</div>
            <h3>퀴즈 생성</h3>
            <p>학습 내용을 바탕으로 객관식 문제 자동 생성</p>
          </div>
        </div>

      </div>
    </section>

    <!-- Grading Section -->
    <section class="section grading-section">
      <div class="section-content">
        <div class="section-header">
          <h2>⚡ 대용량 과제 자동 채점</h2>
          <p>수십 개의 과제를 한 번에 채점하고 결과를 시각화합니다</p>
        </div>
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">📋</div>
            <h3>채점 기준 반영</h3>
            <p>사용자 정의 Rubric에 따른 정확한 채점</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">💯</div>
            <h3>점수 + 근거 생성</h3>
            <p>점수와 함께 상세한 채점 근거 제공</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">📊</div>
            <h3>Excel 다운로드</h3>
            <p>채점 결과를 Excel 파일로 다운로드</p>
          </div>
        </div>

      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="bottom-cta">
      <div class="cta-content">
        <h2>캠퍼스 라이프, 이제는 AI가 도와준다.</h2>
        <p>지식·과제·학교생활… 모두 한 화면에서 해결.</p>
        <div class="cta-buttons">
          <button @click="handleLoginClick" class="btn btn-primary-large">
            🔑 로그인
          </button>
          <button @click="handleRegisterClick" class="btn btn-secondary-large">
            📝 회원가입
          </button>
        </div>
      </div>
    </section>

    <!-- Login Modal -->
    <div v-if="showLogin" class="modal-overlay" @click="showLogin = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>🔑 로그인</h2>
          <button @click="showLogin = false" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label>사용자명</label>
              <input v-model="loginForm.username" type="text" autocomplete="username" required>
            </div>
            <div class="form-group">
              <label>비밀번호</label>
              <input v-model="loginForm.password" type="password" autocomplete="current-password" required>
            </div>
            <button type="submit" :disabled="isLoading" class="btn btn-primary full-width">
              {{ isLoading ? '로그인 중...' : '로그인' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Register Modal -->
    <div v-if="showRegister" class="modal-overlay" @click="showRegister = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>📝 회원가입</h2>
          <button @click="showRegister = false" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <form @submit.prevent="handleRegister">
            <div class="form-group">
              <label>사용자명</label>
              <input 
                v-model="registerForm.username" 
                type="text" 
                autocomplete="username"
                :class="{ 'error': usernameError }"
                @input="validateUsername"
                required
              >
              <div class="form-hint">3-20자, 영문/숫자/언더스코어만 가능</div>
              <div v-if="usernameError" class="error-message">{{ usernameError }}</div>
            </div>
            <div class="form-group">
              <label>이메일</label>
              <input 
                v-model="registerForm.email" 
                type="email" 
                autocomplete="email"
                :class="{ 'error': emailError }"
                @input="validateEmail"
                required
              >
              <div class="form-hint">유효한 이메일 주소를 입력하세요</div>
              <div v-if="emailError" class="error-message">{{ emailError }}</div>
            </div>
            <div class="form-group">
              <label>비밀번호</label>
              <input 
                v-model="registerForm.password" 
                type="password" 
                autocomplete="new-password"
                :class="{ 'error': passwordError }"
                @input="validatePassword"
                required
              >
              <div class="form-hint">6-72자, 영문/숫자/특수문자 조합</div>
              <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
              <div class="password-strength">
                <div class="strength-bar">
                  <div :class="['strength-fill', passwordStrength]"></div>
                </div>
                <span class="strength-text">{{ passwordStrengthText }}</span>
              </div>
            </div>
            <div class="form-group">
              <label>역할</label>
              <select v-model="registerForm.role" required>
                <option value="student">학생</option>
                <option value="professor">교수</option>
              </select>
              <div class="form-hint">역할에 따라 이용 가능한 기능이 달라집니다</div>
            </div>
            <button 
              type="submit" 
              :disabled="isLoading || !isFormValid" 
              class="btn btn-primary full-width"
            >
              {{ isLoading ? '가입 중...' : '회원가입' }}
            </button>
          </form>
        </div>
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
  name: 'HomePage',
  data() {
    return {
      showLogin: false,
      showRegister: false,
      isLoading: false,
      statusMessage: '',
      statusType: 'info',
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        password: '',
        role: 'student'
      },
      usernameError: '',
      emailError: '',
      passwordError: '',
      passwordStrength: 'weak'
    }
  },
  computed: {
    passwordStrengthText() {
      const strength = {
        weak: '약함',
        medium: '보통',
        strong: '강함'
      }
      return strength[this.passwordStrength] || '약함'
    },
    isFormValid() {
      return !this.usernameError && !this.emailError && !this.passwordError &&
             this.registerForm.username && this.registerForm.email && this.registerForm.password
    }
  },
  methods: {
    handleLoginClick() {
      console.log('Login button clicked')
      this.showLogin = true
    },
    
    handleRegisterClick() {
      console.log('Register button clicked')
      this.showRegister = true
    },
    
    goToAgent() {
      this.$router.push('/agent')
    },
    
    goToLecture() {
      this.$router.push('/lecture')
    },
    
    goToGrading() {
      this.$router.push('/grading')
    },
    
    async handleLogin() {
      this.isLoading = true;
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.loginForm)
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: '서버 오류' }))
          throw new Error(errorData.detail || `HTTP ${response.status}: 로그인에 실패했습니다`)
        }
        
        const data = await response.json()
        
        // 토큰 저장
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        
        // 사용자 정보 가져오기 (토큰에서 추출)
        const payload = JSON.parse(atob(data.access_token.split('.')[1]))
        const userInfo = {
          name: payload.username,
          role: payload.role
        }
        localStorage.setItem('user_info', JSON.stringify(userInfo))
        
        this.showStatus('✅ 로그인 성공!', 'success')
        this.showLogin = false
        
        // 대시보드로 이동
        this.$router.push('/dashboard')
        
      } catch (error) {
        console.error('Login error:', error)
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          this.showStatus('❌ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.', 'error')
        } else {
          this.showStatus('❌ ' + error.message, 'error')
        }
      } finally {
        this.isLoading = false
      }
    },

    async handleRegister() {
      this.isLoading = true;
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.registerForm)
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: '서버 오류' }))
          throw new Error(errorData.detail || `HTTP ${response.status}: 회원가입에 실패했습니다`)
        }
        
        const data = await response.json()
        
        this.showStatus('✅ 회원가입 성공! 로그인해주세요.', 'success')
        this.showRegister = false
        this.showLogin = true
        
        // 폼 초기화
        this.registerForm = { username: '', email: '', password: '', role: 'student' }
        
      } catch (error) {
        this.showStatus('❌ ' + error.message, 'error')
      } finally {
        this.isLoading = false
      }
    },

    showStatus(message, type = 'info') {
      this.statusMessage = message;
      this.statusType = type;
      setTimeout(() => {
        this.statusMessage = '';
      }, 4000);
    },

    validateUsername() {
      const username = this.registerForm.username;
      if (!username) {
        this.usernameError = '';
        return;
      }
      if (username.length < 3) {
        this.usernameError = '사용자명은 3자 이상이어야 합니다';
      } else if (username.length > 20) {
        this.usernameError = '사용자명은 20자 이하여야 합니다';
      } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        this.usernameError = '영문, 숫자, 언더스코어만 사용 가능합니다';
      } else {
        this.usernameError = '';
      }
    },

    validateEmail() {
      const email = this.registerForm.email;
      if (!email) {
        this.emailError = '';
        return;
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        this.emailError = '올바른 이메일 형식이 아닙니다';
      } else {
        this.emailError = '';
      }
    },

    validatePassword() {
      const password = this.registerForm.password;
      if (!password) {
        this.passwordError = '';
        this.passwordStrength = 'weak';
        return;
      }
      
      if (password.length < 6) {
        this.passwordError = '비밀번호는 6자 이상이어야 합니다';
      } else if (password.length > 72) {
        this.passwordError = '비밀번호는 72자 이하여야 합니다';
      } else {
        this.passwordError = '';
      }

      // 비밀번호 강도 계산
      let strength = 0;
      if (password.length >= 8) strength++;
      if (/[a-z]/.test(password)) strength++;
      if (/[A-Z]/.test(password)) strength++;
      if (/[0-9]/.test(password)) strength++;
      if (/[^a-zA-Z0-9]/.test(password)) strength++;

      if (strength <= 2) {
        this.passwordStrength = 'weak';
      } else if (strength <= 3) {
        this.passwordStrength = 'medium';
      } else {
        this.passwordStrength = 'strong';
      }
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fdff 0%, #e8f4fd 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Hero Section */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 20px;
}

.hero-content {
  max-width: 900px;
}

.main-title {
  font-size: 4rem;
  font-weight: 800;
  color: #2c3e50;
  margin-bottom: 20px;
  line-height: 1.2;
}

.sub-title {
  font-size: 1.8rem;
  color: #34495e;
  margin-bottom: 15px;
  font-weight: 600;
}

.description {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin-bottom: 40px;
  line-height: 1.6;
}

.cta-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.slogan {
  font-size: 1.4rem;
  color: #e74c3c;
  font-weight: 700;
  font-style: italic;
  margin-top: 20px;
}

/* Section Styles */
.section {
  padding: 100px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-content {
  text-align: center;
}

.section-header {
  margin-bottom: 60px;
}

.section-header h2 {
  font-size: 2.8rem;
  color: #2c3e50;
  margin-bottom: 15px;
  font-weight: 700;
}

.section-header p {
  font-size: 1.3rem;
  color: #7f8c8d;
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
  margin-bottom: 50px;
}

.feature-item {
  text-align: center;
  padding: 40px 20px;
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-10px);
}

.feature-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  display: block;
}

.feature-item h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
  font-weight: 600;
}

.feature-item p {
  font-size: 1.1rem;
  color: #7f8c8d;
  line-height: 1.6;
}

.section-cta {
  text-align: center;
  margin-top: 40px;
}

/* Section Backgrounds */
.agent-section {
  background: rgba(255, 255, 255, 0.5);
}

.pdf-section {
  background: rgba(135, 206, 235, 0.1);
}

.grading-section {
  background: rgba(255, 255, 255, 0.7);
}

/* Bottom CTA */
.bottom-cta {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.cta-content h2 {
  font-size: 2.5rem;
  margin-bottom: 15px;
  font-weight: 700;
}

.cta-content p {
  font-size: 1.3rem;
  margin-bottom: 30px;
  opacity: 0.9;
}

/* Button Styles */
.btn {
  padding: 15px 30px;
  border: none;
  border-radius: 25px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.3);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(135, 206, 235, 0.4);
}

.btn-primary-large {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  padding: 20px 40px;
  font-size: 1.3rem;
  box-shadow: 0 6px 25px rgba(135, 206, 235, 0.4);
}

.btn-primary-large:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(135, 206, 235, 0.5);
}

.btn-secondary-large {
  background: rgba(255, 255, 255, 0.9);
  color: #2980b9;
  padding: 20px 40px;
  font-size: 1.3rem;
  border: 2px solid #87ceeb;
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.2);
}

.btn-secondary-large:hover {
  background: white;
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(135, 206, 235, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .main-title {
    font-size: 2.5rem;
  }
  
  .sub-title {
    font-size: 1.4rem;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .section {
    padding: 60px 20px;
  }
}

/* Modal Styles */
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  background: rgba(0, 0, 0, 0.5) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  z-index: 9999 !important;
}

.modal {
  background: white !important;
  border-radius: 12px !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
  max-width: 400px !important;
  width: 90% !important;
  max-height: 90vh !important;
  overflow-y: auto !important;
  position: relative !important;
  display: block !important;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.3em;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5em;
  cursor: pointer;
  padding: 0;
}

.modal-content {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1em;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error {
  border-color: #dc3545;
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
}

.form-hint {
  font-size: 0.8em;
  color: #666;
  margin-top: 4px;
}

.error-message {
  font-size: 0.8em;
  color: #dc3545;
  margin-top: 4px;
  font-weight: 500;
}

.password-strength {
  margin-top: 8px;
}

.strength-bar {
  width: 100%;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  width: 33%;
  background: #dc3545;
}

.strength-fill.medium {
  width: 66%;
  background: #ffc107;
}

.strength-fill.strong {
  width: 100%;
  background: #28a745;
}

.strength-text {
  font-size: 0.8em;
  font-weight: 500;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.full-width {
  width: 100%;
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
}

.status-toast.success {
  background-color: #e8f5e9;
  color: #388e3c;
  border-left: 4px solid #388e3c;
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