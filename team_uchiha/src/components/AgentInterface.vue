<template>
  <div class="agent-interface">
    <!-- Header -->
    <div class="header">
      <h1>🤖 React AI Agent</h1>
      <p class="subtitle">지능형 에이전트와 대화하세요</p>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" :class="['status-message', statusType]">
      {{ statusMessage }}
    </div>

  <div class="container-fluid agent-container px-4">
      <!-- Left Panel: Chat -->
  <section class="chat-panel">
        <div class="section-header">
          <h2>💬 대화</h2>
          <button @click="clearChat" class="btn btn-small btn-outline">
            🗑️  초기화
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
            <div class="message-content">{{ msg.content }}</div>
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
      </section>

      <!-- Right Panel: Info & Tools -->
  <section class="info-panel">
        <!-- Tools Section -->
        <div class="section-header">
          <h3>🔧 사용 가능한 도구</h3>
        </div>

        <div class="tools-list">
          <div
            v-for="tool in availableTools"
            :key="tool.tool_id"
            class="tool-card"
          >
            <div class="tool-name">{{ tool.name }}</div>
            <div class="tool-description">{{ tool.description }}</div>
          </div>
        </div>

        <!-- Settings -->
        <div class="section-header" style="margin-top: 20px">
          <h3>⚙️ 설정</h3>
        </div>

        <div class="settings">
          <div class="setting-item">
            <label>최대 반복 횟수</label>
            <input
              v-model.number="maxIterations"
              type="number"
              min="1"
              max="10"
              :disabled="isLoading"
              class="setting-input"
            />
          </div>

          <div class="setting-item">
            <label>메모리 크기</label>
            <div class="memory-info">{{ memorySize }} 항목</div>
            <button
              @click="clearMemory"
              :disabled="memorySize === 0 || isLoading"
              class="btn btn-small btn-outline"
            >
              메모리 초기화
            </button>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="section-header" style="margin-top: 20px">
          <h3>⚡ 빠른 질문</h3>
        </div>

        <div class="quick-questions">
          <button
            v-for="(q, idx) in quickQuestions"
            :key="idx"
            @click="sendQuickQuestion(q)"
            :disabled="isLoading"
            class="btn btn-small btn-outline"
          >
            {{ q.emoji }} {{ q.text }}
          </button>
        </div>

        <!-- Stats -->
        <div class="section-header" style="margin-top: 20px">
          <h3>📊 통계</h3>
        </div>

        <div class="stats">
          <div class="stat-item">
            <span class="stat-label">총 메시지</span>
            <span class="stat-value">{{ messages.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">총 반복</span>
            <span class="stat-value">{{ totalIterations }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">메모리 크기</span>
            <span class="stat-value">{{ memorySize }}</span>
          </div>
        </div>
      </section>
    </div>

    <!-- Memory Viewer Modal -->
    <div v-if="showMemory" class="modal-overlay" @click="showMemory = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>📝 에이전트 메모리</h2>
          <button @click="showMemory = false" class="close-btn">✕</button>
        </div>

        <div class="modal-content">
          <div v-for="(item, idx) in memoryData" :key="idx" class="memory-item">
            <div class="memory-type">
              {{ item.type === 'agent_step' ? '💭' : '👁️' }}
              {{ item.type === 'agent_step' ? '에이전트 단계' : '관찰' }}
            </div>
            <div class="memory-detail">
              <small>반복: {{ item.iteration }}</small>
              <div v-if="item.thought" class="memory-field">
                <strong>생각:</strong> {{ item.thought }}
              </div>
              <div v-if="item.action" class="memory-field">
                <strong>행동:</strong> {{ item.action }}
              </div>
              <div v-if="item.action_input" class="memory-field">
                <strong>입력:</strong> {{ item.action_input }}
              </div>
              <div v-if="item.observation" class="memory-field">
                <strong>관찰:</strong> {{ item.observation }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  <!-- Footer -->
    <div class="footer">
      <p>💡 팁: 에이전트는 웹 검색과 계산 도구를 사용할 수 있습니다</p>
      <button
        @click="showMemory = true"
        class="btn btn-small btn-outline"
      >
        📝 메모리 보기
      </button>
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
      totalIterations: 0,
      availableTools: [],
      quickQuestions: [
        {
          emoji: '🌍',
          text: '최신 AI 뉴스'
        },
        {
          emoji: '🐍',
          text: '파이썬 최신 버전'
        },
        {
          emoji: '📊',
          text: '2 + 2는?'
        },
        {
          emoji: '🚀',
          text: 'React 장점'
        }
      ]
    };
  },

  mounted() {
    this.loadTools();
    this.checkHealth();
  },

  methods: {
    /**
     * 도구 목록 로드
     */
    async loadTools() {
      try {
        const response = await fetch(`${API_BASE_URL}/tools`);
        const data = await response.json();
        this.availableTools = data.tools || [];
      } catch (error) {
        console.error('도구 목록 로드 실패:', error);
      }
    },

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
            max_iterations: this.maxIterations
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

        this.totalIterations += data.iterations;
        this.memorySize = data.memory ? data.memory.length : 0;
        this.memoryData = data.memory || [];

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
     * 빠른 질문 전송
     */
    sendQuickQuestion(question) {
      this.userInput = question.text;
      this.$nextTick(() => this.sendMessage());
    },

    /**
     * 메모리 초기화
     */
    async clearMemory() {
      try {
        await fetch(`${API_BASE_URL}/memory`, {
          method: 'DELETE'
        });

        this.memorySize = 0;
        this.memoryData = [];
        this.totalIterations = 0;
        this.showStatus('🗑️  메모리가 초기화되었습니다', 'success');
      } catch (error) {
        this.showStatus(`❌ 메모리 초기화 실패: ${error.message}`, 'error');
      }
    },

    /**
     * 대화 초기화
     */
    clearChat() {
      this.messages = [];
      this.totalIterations = 0;
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
  text-align: center;
  color: white;
  margin-bottom: 30px;
  padding-top: 20px;
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

/* Container */
.agent-container {
  width: 100%;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 24px;
  margin-bottom: 18px;
}

@media (max-width: 1024px) {
  .agent-container {
    grid-template-columns: 1fr;
  }
}

/* Section */
.chat-panel,
.info-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  animation: fadeIn 0.4s ease-out;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.section-header h2,
.section-header h3 {
  margin: 0;
  font-size: 1.2em;
  font-weight: 600;
}

/* Chat Panel */
.chat-panel {
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

/* Info Panel */
.info-panel {
  max-height: calc(100vh - 120px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 20px;
}

.tools-list {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-card {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  border-left: 4px solid #667eea;
}

.tool-name {
  font-weight: 600;
  color: #667eea;
  margin-bottom: 4px;
}

.tool-description {
  font-size: 0.85em;
  color: #666;
}

.settings {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  border-top: 1px solid #e0e0e0;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item label {
  font-weight: 600;
  font-size: 0.9em;
  color: #333;
}

.setting-input {
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 0.9em;
}

.memory-info {
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  font-weight: 600;
  color: #667eea;
}

.quick-questions {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 1px solid #e0e0e0;
}

.stats {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-top: 1px solid #e0e0e0;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.stat-label {
  font-size: 0.9em;
  color: #666;
}

.stat-value {
  font-weight: 700;
  color: #667eea;
  font-size: 1.2em;
}

/* Modal */
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
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease-out;
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
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.memory-item {
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.memory-type {
  font-weight: 700;
  color: #667eea;
  margin-bottom: 10px;
}

.memory-detail {
  font-size: 0.9em;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.memory-detail small {
  color: #999;
}

.memory-field {
  padding: 8px;
  background: white;
  border-radius: 4px;
  word-break: break-word;
}

.memory-field strong {
  color: #667eea;
}

/* Footer */
.footer {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  color: white;
  padding: 20px;
  font-size: 0.9em;
}

.footer p {
  margin: 0 0 15px 0;
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
