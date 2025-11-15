<template>
  <div class="home-page">
    <!-- Hero Section -->
    <div class="hero">
      <h1>🤖 UCHIHA AI Assistant</h1>
      <p class="subtitle">지능형 AI 에이전트와 함께하는 스마트한 대화 경험</p>
      
      <div class="features">
        <div class="feature">
          <span class="icon">🎤</span>
          <h3>음성 인식</h3>
          <p>말로 질문하고 음성으로 답변을 들어보세요</p>
        </div>
        <div class="feature">
          <span class="icon">🌐</span>
          <h3>웹 검색</h3>
          <p>실시간 정보 검색과 정확한 답변 제공</p>
        </div>
        <div class="feature">
          <span class="icon">🔍</span>
          <h3>협성대 정보</h3>
          <p>협성대학교 관련 정보를 빠르게 찾아드립니다</p>
        </div>
      </div>

      <div class="auth-buttons">
        <button @click="showLogin = true" class="btn btn-primary">
          🔑 로그인
        </button>
        <button @click="showRegister = true" class="btn btn-outline">
          📝 회원가입
        </button>
      </div>
    </div>

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
              <input v-model="loginForm.username" type="text" required>
            </div>
            <div class="form-group">
              <label>비밀번호</label>
              <input v-model="loginForm.password" type="password" required>
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
        password: ''
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
    async handleLogin() {
      this.isLoading = true;
      try {
        const response = await fetch('http://localhost:8000/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.loginForm)
        });

        const data = await response.json();

        if (response.ok) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          this.showStatus('✅ 로그인 성공!', 'success');
          this.showLogin = false;
          this.$emit('login-success');
        } else {
          this.showStatus('❌ ' + data.detail, 'error');
        }
      } catch (error) {
        this.showStatus('❌ 로그인 실패: ' + error.message, 'error');
      } finally {
        this.isLoading = false;
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
        });

        const data = await response.json();

        if (response.ok) {
          this.showStatus('✅ 회원가입 성공! 로그인해주세요.', 'success');
          this.showRegister = false;
          this.showLogin = true;
        } else {
          this.showStatus('❌ ' + data.detail, 'error');
        }
      } catch (error) {
        this.showStatus('❌ 회원가입 실패: ' + error.message, 'error');
      } finally {
        this.isLoading = false;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.hero {
  text-align: center;
  color: white;
  max-width: 800px;
  padding: 40px 20px;
}

.hero h1 {
  font-size: 3em;
  margin-bottom: 20px;
  font-weight: 700;
}

.subtitle {
  font-size: 1.3em;
  margin-bottom: 50px;
  opacity: 0.9;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  margin-bottom: 50px;
}

.feature {
  background: rgba(255, 255, 255, 0.1);
  padding: 30px 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.feature .icon {
  font-size: 2.5em;
  display: block;
  margin-bottom: 15px;
}

.feature h3 {
  margin: 0 0 10px 0;
  font-size: 1.2em;
}

.feature p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9em;
}

.auth-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.btn {
  padding: 15px 30px;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-primary {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
}

.btn-primary:hover {
  background: white;
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  overflow: hidden;
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

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1em;
  box-sizing: border-box;
}

.form-group input:focus {
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