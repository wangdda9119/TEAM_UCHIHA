<template>
  <div class="agent-interface">
    <!-- Header -->
    <div class="header">
      <div class="header-content">
        <div class="title-section">
          <h1>🤖 React AI Agent</h1>
          <p class="subtitle">지능형 에이전트와 대화하세요</p>
        </div>
        <div class="language-selector">
          <select v-model="selectedLanguage" class="language-dropdown">
            <option value="ko">🇰🇷 한국어</option>
            <option value="en">🇺🇸 English</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" :class="['status-message', statusType]">
      {{ statusMessage }}
    </div>

    <!-- Chat Panel -->
    <div class="chat-container">
      <div class="chat-header">
        <h2>💬 대화</h2>
        <button @click="clearChat" class="btn btn-small btn-outline">
          🗑️ 초기화
        </button>
      </div>

        <!-- Chat Messages -->
        <div class="messages-container">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="['message', msg.role]"
          >
            <div class="message-header">
              <span class="role-badge" :class="msg.role">
                {{ msg.role === 'user' ? '👤 당신' : '🤖 에이전트' }}
              </span>
              <span v-if="msg.timestamp" class="timestamp">
                {{ formatTime(msg.timestamp) }}
              </span>
            </div>
            <div class="message-content" v-html="formatMessage(msg.content)"></div>
            <div v-if="msg.iterations !== undefined" class="message-meta">
              반복: {{ msg.iterations }}회
            </div>
          </div>

          <!-- Loading -->
          <div v-if="isLoading" class="message agent loading">
            <div class="message-content">
              <div class="spinner"></div>
              <span>에이전트가 생각 중입니다...</span>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="input-area">
          <textarea
            v-model="userInput"
            placeholder="에이전트에게 질문하세요..."
            @keydown.enter.ctrl="sendMessage"
            :disabled="isLoading"
            class="message-input"
          ></textarea>
          <div class="input-controls">
            <button
              @click="toggleRecording"
              :disabled="isLoading"
              :class="['btn', 'btn-voice', isRecording ? 'recording' : '']"
            >
              <span class="icon">{{ isRecording ? '⏹️' : '🎤' }}</span>
              {{ isRecording ? '녹음 중지' : '음성 입력' }}
            </button>
            <button
              @click="toggleSpeakMode"
              :disabled="isLoading"
              :class="['btn', 'btn-speak', speakMode ? 'active' : '']"
            >
              <span class="icon">{{ speakMode ? '🔊' : '🔇' }}</span>
              {{ speakMode ? '말하기 ON' : '말하기 OFF' }}
            </button>
            <button
              @click="sendMessage"
              :disabled="!userInput.trim() || isLoading"
              class="btn btn-primary"
            >
              <span class="icon">📤</span>
              전송 (Ctrl+Enter)
            </button>
            <span class="char-count">{{ userInput.length }} / 2000</span>
          </div>
        </div>
    </div>
  </div>
</template>

<script>
const API_BASE_URL = 'http://localhost:8000/api/v1/agent';

export default {
  name: 'AgentInterface',
  data() {
    return {
      messages: [],
      userInput: '',
      isLoading: false,
      statusMessage: '',
      statusType: 'info',
      maxIterations: 5,
      memorySize: 0,
      memoryData: [],
      showMemory: false,
      isRecording: false,
      mediaRecorder: null,
      audioChunks: [],
      selectedLanguage: 'ko',
      speakMode: false
    };
  },

  mounted() {
    this.checkHealth();
  },

  methods: {


    /**
     * 헬스 체크
     */
    async checkHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        if (data.status !== 'ok') {
          this.showStatus('⚠️ 에이전트 서비스 이상', 'error');
        }
      } catch (error) {
        this.showStatus('❌ 서버 연결 실패', 'error');
      }
    },

    /**
     * 메시지 전송
     */
    async sendMessage() {
      if (!this.userInput.trim() || this.isLoading) return;

      const question = this.userInput.trim();

      // 사용자 메시지 추가
      this.messages.push({
        role: 'user',
        content: question,
        timestamp: new Date()
      });

      this.userInput = '';
      this.isLoading = true;

      try {
        this.showStatus('🤖 에이전트가 처리 중입니다...', 'info');

        const response = await fetch(`${API_BASE_URL}/run`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            question: question,
            session_id: 'default_session',
            language: this.selectedLanguage
          })
        });

        if (!response.ok) {
          throw new Error('요청 실패');
        }

        const data = await response.json();

        // 에이전트 응답 추가
        this.messages.push({
          role: 'agent',
          content: data.answer,
          iterations: data.iterations,
          timestamp: new Date()
        });

        // 말하기 모드가 켜져 있으면 TTS 실행
        if (this.speakMode) {
          await this.speakText(data.answer);
        }

        this.showStatus('✅ 처리 완료!', 'success');

        // 스크롤 아래로
        this.$nextTick(() => {
          const container = document.querySelector('.messages-container');
          if (container) {
            container.scrollTop = container.scrollHeight;
          }
        });
      } catch (error) {
        this.showStatus(`❌ 오류: ${error.message}`, 'error');
        this.messages.push({
          role: 'agent',
          content: `❌ 오류 발생: ${error.message}`,
          timestamp: new Date()
        });
      } finally {
        this.isLoading = false;
      }
    },



    /**
     * 대화 초기화
     */
    clearChat() {
      this.messages = [];
      this.showStatus('💬 대화가 초기화되었습니다', 'success');
    },

    /**
     * 상태 메시지 표시
     */
    showStatus(message, type = 'info') {
      this.statusMessage = message;
      this.statusType = type;

      if (type === 'success' || type === 'error') {
        setTimeout(() => {
          this.statusMessage = '';
        }, 4000);
      }
    },

    /**
     * 메시지 포맷 (줄바꿈 처리)
     */
    formatMessage(content) {
      return content.replace(/\n/g, '<br>');
    },

    /**
     * 시간 포맷
     */
    formatTime(date) {
      if (!(date instanceof Date)) {
        date = new Date(date);
      }
      return date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    /**
     * 음성 녹음 토글
     */
    async toggleRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        await this.startRecording();
      }
    },

    /**
     * 녹음 시작
     */
    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
          await this.transcribeAudio(audioBlob);
        };

        this.mediaRecorder.start();
        this.isRecording = true;
        this.showStatus('🎤 녹음 중...', 'info');
      } catch (error) {
        this.showStatus('❌ 마이크 접근 실패: ' + error.message, 'error');
      }
    },

    /**
     * 녹음 중지
     */
    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        this.isRecording = false;
        this.showStatus('⏹️ 녹음 완료, 변환 중...', 'info');
      }
    },

    /**
     * 음성을 텍스트로 변환
     */
    async transcribeAudio(audioBlob) {
      try {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');

        const response = await fetch('http://localhost:8000/api/v1/stt-tts/transcribe', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('음성 인식 실패');
        }

        const data = await response.json();
        this.userInput = data.text;
        this.showStatus('✅ 음성 인식 완료!', 'success');
      } catch (error) {
        this.showStatus('❌ 음성 인식 오류: ' + error.message, 'error');
      }
    },

    /**
     * 말하기 모드 토글
     */
    toggleSpeakMode() {
      this.speakMode = !this.speakMode;
      this.showStatus(
        this.speakMode ? '🔊 말하기 모드 ON' : '🔇 말하기 모드 OFF', 
        'info'
      );
    },

    /**
     * 텍스트를 음성으로 읽어주기
     */
    async speakText(text) {
      try {
        const response = await fetch('http://localhost:8000/api/v1/stt-tts/synthesize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            text: text,
            voice: 'alloy'
          })
        });

        if (!response.ok) {
          throw new Error('음성 합성 실패');
        }

        const data = await response.json();
        
        // hex 문자열을 바이너리로 변환
        const audioBytes = new Uint8Array(
          data.audio.match(/.{1,2}/g).map(byte => parseInt(byte, 16))
        );
        
        // 오디오 재생
        const audioBlob = new Blob([audioBytes], { type: 'audio/mp3' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.play();
        
        // 메모리 정리
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
        };
        
      } catch (error) {
        console.error('TTS 오류:', error);
        this.showStatus('❌ 음성 합성 오류: ' + error.message, 'error');
      }
    }
  }
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.agent-interface {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 18px 24px 18px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Header */
.header {
  color: white;
  margin-bottom: 30px;
  padding-top: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.title-section {
  text-align: left;
}

.header h1 {
  font-size: 2.5em;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.subtitle {
  font-size: 1.1em;
  opacity: 0.9;
  margin: 0;
}

.language-selector {
  display: flex;
  align-items: center;
}

.language-dropdown {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  min-width: 120px;
}

.language-dropdown:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
}

/* Status Message */
.status-message {
  max-width: 1200px;
  margin: 0 auto 20px;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 500;
  animation: slideIn 0.3s ease-out;
}

.status-message.info {
  background-color: #e3f2fd;
  color: #1976d2;
  border-left: 4px solid #1976d2;
}

.status-message.success {
  background-color: #e8f5e9;
  color: #388e3c;
  border-left: 4px solid #388e3c;
}

.status-message.error {
  background-color: #ffebee;
  color: #d32f2f;
  border-left: 4px solid #d32f2f;
}

/* Chat Container */
.chat-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  animation: fadeIn 0.4s ease-out;
  margin-bottom: 20px;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.2em;
  font-weight: 600;
}

.chat-container {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 220px);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: #fafafa;
}

/* Messages */
.message {
  display: flex;
  flex-direction: column;
  max-width: 72%;
  animation: fadeIn 0.25s ease-out;
}

.message.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #4f6fe6 0%, #6b4ea8 100%);
  color: white;
  border-radius: 14px 14px 2px 14px;
  padding: 10px 14px;
}

.message.agent {
  align-self: flex-start;
  background: #ffffff;
  color: #222;
  border-radius: 14px 14px 14px 2px;
  padding: 10px 14px;
  border: 1px solid #eef0f3;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.role-badge {
  font-size: 0.85em;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

.role-badge.user {
  background: rgba(255, 255, 255, 0.2);
}

.role-badge.agent {
  background: rgba(0, 0, 0, 0.1);
}

.timestamp {
  font-size: 0.75em;
  opacity: 0.7;
}

.message-content {
  padding: 6px 4px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-meta {
  font-size: 0.85em;
  opacity: 0.8;
  margin-top: 8px;
  padding: 0 16px 8px;
}

.message.loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Input Area */
.input-area {
  padding: 26px;
  border-top: 1px solid #e9edf3;
  background: #ffffff;
}

.message-input {
  width: 100%;
  padding: 16px;
  border: 1px solid #e6e9ef;
  border-radius: 12px;
  font-family: inherit;
  font-size: 1.05em;
  resize: vertical;
  min-height: 120px;
  transition: box-shadow 0.3s ease, border-color 0.2s ease;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  gap: 10px;
}

.char-count {
  font-size: 0.85em;
  color: #999;
}



/* Button Styles */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-small {
  padding: 8px 16px;
  font-size: 0.9em;
}

.btn-outline {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover:not(:disabled) {
  background: #f0f4ff;
}

.btn-voice {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
}

.btn-voice:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.6);
}

.btn-voice.recording {
  background: linear-gradient(135deg, #dc3545 0%, #e74c3c 100%);
  animation: pulse 1.5s infinite;
}

.btn-speak {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.4);
}

.btn-speak:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 193, 7, 0.6);
}

.btn-speak.active {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
  box-shadow: 0 4px 15px rgba(23, 162, 184, 0.4);
}

@keyframes pulse {
  0% {
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
  }
  50% {
    box-shadow: 0 6px 25px rgba(220, 53, 69, 0.8);
  }
  100% {
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
  }
}

.icon {
  font-size: 1.1em;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
