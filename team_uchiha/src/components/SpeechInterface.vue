<template>
  <div class="speech-interface">
    <!-- Header -->
    <div class="header">
      <h1>🎤 음성 인터페이스</h1>
      <p class="subtitle">음성 인식 및 음성 합성 테스트</p>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" :class="['status-message', statusType]">
      {{ statusMessage }}
    </div>

    <div class="container">
      <!-- STT Section -->
      <section class="section stt-section">
        <div class="section-header">
          <h2>음성 인식 (STT)</h2>
          <span class="badge">OpenAI Whisper</span>
        </div>

        <div class="content">
          <!-- Recording Controls -->
          <div class="controls">
            <button
              @click="toggleRecording"
              :class="['btn', 'btn-primary', isRecording ? 'recording' : '']"
              :disabled="isLoading"
            >
              <span v-if="!isRecording" class="icon">🔴</span>
              <span v-else class="icon pulse">⏹️</span>
              {{ isRecording ? '녹음 중지' : '녹음 시작' }}
            </button>

            <div class="recording-info" v-if="isRecording">
              <span class="dot"></span>
              <span>녹음 중...</span>
            </div>
          </div>

          <!-- Transcription Result -->
          <div class="result-box">
            <div class="result-label">인식된 텍스트</div>
            <div class="result-text">
              {{ transcribedText || '녹음 후 텍스트가 표시됩니다' }}
            </div>
            <button
              v-if="transcribedText"
              @click="copyToClipboard(transcribedText)"
              class="btn btn-small btn-outline"
            >
              📋 복사
            </button>
          </div>

          <!-- Waveform Animation -->
          <div v-if="isRecording" class="waveform">
            <span></span><span></span><span></span><span></span><span></span>
          </div>
        </div>
      </section>

      <!-- Divider -->
      <div class="divider"></div>

      <!-- TTS Section -->
      <section class="section tts-section">
        <div class="section-header">
          <h2>음성 합성 (TTS)</h2>
          <span class="badge">OpenAI TTS</span>
        </div>

        <div class="content">
          <!-- Text Input -->
          <div class="input-group">
            <label for="text-input">변환할 텍스트</label>
            <textarea
              id="text-input"
              v-model="textForSpeech"
              placeholder="음성으로 변환할 텍스트를 입력하세요..."
              class="text-input"
              maxlength="4096"
            ></textarea>
            <div class="char-count">{{ textForSpeech.length }} / 4096</div>
          </div>

          <!-- Voice Selection -->
          <div class="voice-selection">
            <label>음성 선택</label>
            <div class="voice-options">
              <button
                v-for="v in voices"
                :key="v"
                @click="selectedVoice = v"
                :class="['voice-btn', selectedVoice === v ? 'active' : '']"
              >
                {{ v }}
              </button>
            </div>
          </div>

          <!-- Synthesize Button -->
          <div class="controls">
            <button
              @click="synthesizeSpeech"
              :disabled="!textForSpeech.trim() || isLoading"
              class="btn btn-primary"
            >
              <span class="icon">🔊</span>
              음성 생성 및 재생
            </button>
          </div>

          <!-- Loading Indicator -->
          <div v-if="isLoading" class="loading">
            <div class="spinner"></div>
            <span>처리 중...</span>
          </div>

          <!-- Test Phrases -->
          <div class="quick-phrases">
            <label>빠른 테스트 문구</label>
            <div class="phrase-buttons">
              <button
                v-for="phrase in testPhrases"
                :key="phrase"
                @click="usePhrase(phrase)"
                class="btn btn-small btn-outline"
              >
                {{ phrase }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- History Section -->
    <section class="section history-section" v-if="history.length > 0">
      <div class="section-header">
        <h2>변환 이력</h2>
        <button @click="clearHistory" class="btn btn-small btn-outline">
          지우기
        </button>
      </div>

      <div class="history-list">
        <div v-for="(item, index) in history" :key="index" class="history-item">
          <div class="history-type">{{ item.type }}</div>
          <div class="history-content">{{ item.content }}</div>
          <div class="history-time">{{ item.time }}</div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <div class="footer">
      <p>💡 팁: OpenAI API 키가 .env 파일에 설정되어 있어야 합니다</p>
      <p v-if="!apiHealthy" class="error">⚠️ API 연결 실패 - 서버를 확인하세요</p>
    </div>
  </div>
</template>

<script>
import AudioRecorder, { playAudio } from '@/utils/audioUtils.js';
import SpeechAPIClient from '@/api/speechClient.js';

export default {
  name: 'SpeechInterface',
  data() {
    return {
      audioRecorder: null,
      isRecording: false,
      isLoading: false,
      transcribedText: '',
      textForSpeech: '',
      selectedVoice: 'alloy',
      statusMessage: '',
      statusType: 'info',
      apiHealthy: false,
      history: [],
      voices: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
      testPhrases: [
        '안녕하세요',
        '날씨가 좋네요',
        '오늘 하루 잘 보냈나요?',
        'Welcome to Uchiha project'
      ]
    };
  },

  mounted() {
    this.audioRecorder = new AudioRecorder();
    this.checkAPIHealth();
  },

  methods: {
    /**
     * Check API connection
     */
    async checkAPIHealth() {
      try {
        this.apiHealthy = await SpeechAPIClient.healthCheck();
        if (!this.apiHealthy) {
          this.showStatus('⚠️ API 서버 연결 실패', 'error');
        }
      } catch (error) {
        console.error('Health check failed:', error);
        this.apiHealthy = false;
      }
    },

    /**
     * Toggle recording
     */
    async toggleRecording() {
      try {
        if (this.isRecording) {
          await this.stopRecording();
        } else {
          await this.startRecording();
        }
      } catch (error) {
        this.showStatus(`❌ ${error.message}`, 'error');
      }
    },

    /**
     * Start recording
     */
    async startRecording() {
      try {
        await this.audioRecorder.startRecording();
        this.isRecording = true;
        this.transcribedText = '';
        this.showStatus('🎤 녹음이 시작되었습니다', 'info');
      } catch (error) {
        this.showStatus(`❌ 녹음 시작 실패: ${error.message}`, 'error');
      }
    },

    /**
     * Stop recording and transcribe
     */
    async stopRecording() {
      try {
        this.isRecording = false;
        this.isLoading = true;
        this.showStatus('⏳ 음성 인식 중...', 'info');

        // Get audio blob
        const audioBlob = await this.audioRecorder.stopRecording();
        console.log('Audio blob size:', audioBlob.size);

        // Send to API
        const transcription = await SpeechAPIClient.transcribeAudio(audioBlob);
        this.transcribedText = transcription;

        // Add to history
        this.addToHistory('STT', transcription);

        this.showStatus('✅ 음성 인식 완료!', 'success');

      } catch (error) {
        this.showStatus(`❌ 오류: ${error.message}`, 'error');
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Synthesize text to speech
     */
    async synthesizeSpeech() {
      try {
        if (!this.textForSpeech.trim()) {
          this.showStatus('❌ 텍스트를 입력하세요', 'error');
          return;
        }

        this.isLoading = true;
        this.showStatus('⏳ 음성 생성 중...', 'info');

        // Request synthesis
        const audioBlob = await SpeechAPIClient.synthesizeText(
          this.textForSpeech,
          this.selectedVoice
        );

        console.log('Audio blob size:', audioBlob.size);

        // Play audio
        await playAudio(audioBlob);

        // Add to history
        this.addToHistory('TTS', `[${this.selectedVoice}] ${this.textForSpeech}`);

        this.showStatus('✅ 음성 재생 완료!', 'success');

      } catch (error) {
        this.showStatus(`❌ 오류: ${error.message}`, 'error');
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Use quick phrase
     */
    usePhrase(phrase) {
      this.textForSpeech = phrase;
    },

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text);
        this.showStatus('📋 클립보드에 복사됨', 'success');
      } catch (error) {
        this.showStatus('❌ 복사 실패', 'error');
      }
    },

    /**
     * Show status message
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
     * Add to history
     */
    addToHistory(type, content) {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('ko-KR');

      this.history.unshift({
        type,
        content: content.substring(0, 100),
        time: timeStr
      });

      if (this.history.length > 10) {
        this.history.pop();
      }
    },

    /**
     * Clear history
     */
    clearHistory() {
      this.history = [];
      this.showStatus('🗑️ 이력이 삭제되었습니다', 'info');
    }
  }
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.speech-interface {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
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
  max-width: 600px;
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

/* Container */
.container {
  max-width: 900px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
  }
}

/* Section */
.section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.section-header h2 {
  margin: 0;
  font-size: 1.3em;
  font-weight: 600;
}

.badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
}

.content {
  padding: 25px;
}

/* Controls */
.controls {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
}

.recording-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #d32f2f;
  font-weight: 500;
}

.dot {
  width: 8px;
  height: 8px;
  background: #d32f2f;
  border-radius: 50%;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
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

.btn-primary.recording {
  background: linear-gradient(135deg, #f44336 0%, #e91e63 100%);
  animation: pulse-btn 1.5s ease-in-out infinite;
}

@keyframes pulse-btn {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4);
  }
  50% {
    box-shadow: 0 6px 25px rgba(244, 67, 54, 0.8);
  }
}

.btn-outline {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover:not(:disabled) {
  background: #f0f4ff;
}

.btn-small {
  padding: 8px 16px;
  font-size: 0.9em;
}

.icon {
  font-size: 1.1em;
}

.icon.pulse {
  animation: pulse-icon 0.6s ease-in-out infinite;
}

@keyframes pulse-icon {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

/* Result Box */
.result-box {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
}

.result-label {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 8px;
  font-weight: 600;
  text-transform: uppercase;
}

.result-text {
  flex: 1;
  word-wrap: break-word;
  color: #333;
  font-size: 1em;
  line-height: 1.6;
  margin-bottom: 12px;
}

/* Waveform */
.waveform {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 6px;
  height: 50px;
  margin-top: 20px;
}

.waveform span {
  width: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  animation: wave 0.6s ease-in-out infinite;
}

.waveform span:nth-child(1) { animation-delay: 0s; }
.waveform span:nth-child(2) { animation-delay: 0.1s; }
.waveform span:nth-child(3) { animation-delay: 0.2s; }
.waveform span:nth-child(4) { animation-delay: 0.1s; }
.waveform span:nth-child(5) { animation-delay: 0s; }

@keyframes wave {
  0%, 100% {
    height: 10px;
  }
  50% {
    height: 40px;
  }
}

/* Input Group */
.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 0.95em;
}

.text-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1em;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.3s ease;
}

.text-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.char-count {
  font-size: 0.85em;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

/* Voice Selection */
.voice-selection {
  margin-bottom: 20px;
}

.voice-selection label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
  font-size: 0.95em;
}

.voice-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

@media (max-width: 600px) {
  .voice-options {
    grid-template-columns: repeat(2, 1fr);
  }
}

.voice-btn {
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  text-transform: capitalize;
}

.voice-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.voice-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

/* Loading */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  color: #667eea;
  font-weight: 500;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Quick Phrases */
.quick-phrases {
  margin-top: 20px;
}

.quick-phrases label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
  font-size: 0.95em;
}

.phrase-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

/* Divider */
.divider {
  grid-column: 1 / -1;
  height: 2px;
  background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
  margin: 10px 0;
}

@media (max-width: 768px) {
  .divider {
    display: none;
  }
}

/* History Section */
.history-section {
  max-width: 900px;
  margin: 0 auto 30px;
}

.history-list {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 15px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
  align-items: center;
  border-left: 4px solid #667eea;
}

.history-type {
  font-weight: 600;
  color: #667eea;
  font-size: 0.9em;
  min-width: 50px;
}

.history-content {
  color: #333;
  word-break: break-word;
}

.history-time {
  font-size: 0.85em;
  color: #999;
  white-space: nowrap;
}

/* Footer */
.footer {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
  color: white;
  padding: 20px;
  font-size: 0.9em;
}

.footer p {
  margin: 8px 0;
}

.footer .error {
  color: #ffcdd2;
  font-weight: 500;
}
</style>
