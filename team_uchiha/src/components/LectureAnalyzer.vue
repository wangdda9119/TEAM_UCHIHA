<template>
  <div class="lecture-analyzer">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="main-title">📚 PDF 학습 지원 AI</h1>
        <p class="sub-title">강의 자료를 스마트하게 분석하고 학습을 도와드립니다</p>
        <p class="description">단원별 요약, 핵심 키워드 추출, 퀴즈 생성까지 자동으로</p>
      </div>
    </section>

    <!-- Upload Section -->
    <section class="section upload-section">
      <div class="section-content">
        <div class="section-header">
          <h2>📄 1단계: PDF 파일 업로드</h2>
          <p>분석하고 싶은 강의 PDF 파일을 업로드하세요</p>
        </div>
        
        <div class="upload-area">
          <div class="upload-box" :class="{ 'dragover': isDragOver, 'uploaded': selectedFile }" 
               @dragover.prevent="isDragOver = true" 
               @dragleave.prevent="isDragOver = false"
               @drop.prevent="handleFileDrop">
            <div v-if="!selectedFile" class="upload-placeholder">
              <div class="upload-icon">📁</div>
              <p class="upload-text">클릭하거나 파일을 드래그하여 업로드</p>
              <p class="upload-hint">PDF 파일만 지원됩니다</p>
            </div>
            <div v-else class="file-info">
              <div class="file-icon">📝</div>
              <div class="file-details">
                <p class="file-name">{{ selectedFile.name }}</p>
                <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
              <button @click="removeFile" class="remove-btn">×</button>
            </div>
          </div>
          
          <input 
            type="file" 
            @change="handleFileUpload" 
            accept=".pdf"
            :disabled="uploading"
            ref="fileInput"
            class="file-input"
          />
          
          <div class="upload-actions">
            <button @click="triggerFileInput" :disabled="uploading" class="btn btn-secondary">
              📁 파일 선택
            </button>
            <button @click="uploadPdf" :disabled="!selectedFile || uploading" class="btn btn-primary">
              {{ uploading ? '업로드 중...' : '🚀 업로드 시작' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Action Section -->
    <section v-if="sessionId" class="section action-section">
      <div class="section-content">
        <div class="section-header">
          <h2>⚙️ 2단계: AI 분석 실행</h2>
          <p>업로드된 PDF를 분석하여 학습 자료를 생성합니다</p>
        </div>
        
        <div class="action-grid">
          <div class="action-card">
            <div class="action-icon">📝</div>
            <h3>단원별 요약</h3>
            <p>PDF 내용을 단원별로 나누어 핵심 내용을 요약합니다</p>
            <button 
              @click="generateSummary" 
              :disabled="summaryLoading"
              class="btn btn-primary action-btn"
            >
              {{ summaryLoading ? '요약 생성 중...' : '요약 생성' }}
            </button>
          </div>
          
          <div class="action-card" :class="{ 'disabled': !hasSummary }">
            <div class="action-icon">🎯</div>
            <h3>퀴즈 생성</h3>
            <p>요약된 내용을 바탕으로 학습 퀴즈를 생성합니다</p>
            <button 
              @click="generateQuiz" 
              :disabled="quizLoading || !hasSummary"
              class="btn btn-primary action-btn"
            >
              {{ quizLoading ? '퀴즈 생성 중...' : '퀴즈 생성' }}
            </button>
            <p v-if="!hasSummary" class="requirement-text">먼저 요약을 생성해주세요</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Results Section -->
    <section v-if="summaryData || quizData" class="section results-section">
      <div class="section-content">
        <div class="section-header">
          <h2>🎆 3단계: 분석 결과</h2>
          <p>AI가 분석한 결과를 확인하고 학습에 활용하세요</p>
        </div>
        
        <!-- Summary Results -->
        <div v-if="summaryData" class="result-block">
          <div class="result-header">
            <h3>📋 단원별 요약 결과</h3>
            <span class="result-count">{{ summaryData.chapters.length }}개 단원</span>
          </div>
          
          <div class="chapters-grid">
            <div v-for="(chapter, idx) in summaryData.chapters" :key="idx" class="chapter-card">
              <div class="chapter-number">{{ idx + 1 }}</div>
              <div class="chapter-content">
                <h4 class="chapter-title">{{ chapter.단원제목 }}</h4>
                <p class="chapter-summary">{{ chapter.요약 }}</p>
                <div class="keywords">
                  <span v-for="keyword in chapter.핵심키워드" :key="keyword" class="keyword-tag">
                    {{ keyword }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quiz Results -->
        <div v-if="quizData" class="result-block">
          <div class="result-header">
            <h3>🎯 생성된 퀴즈</h3>
            <span class="result-count">{{ getTotalQuestions() }}개 문제</span>
          </div>
          
          <!-- Hamburger Button -->
          <div class="hamburger-container">
            <button @click="toggleNavigation" class="hamburger-btn" :class="{ 'active': showNavigation }">
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
          
          <!-- Quiz Navigation -->
          <div class="quiz-navigation" :class="{ 'show': showNavigation }">
            <div class="nav-header">
              <h4>단원 네비게이션</h4>
              <button @click="toggleNavigation" class="close-nav">×</button>
            </div>
            <div class="nav-buttons">
              <button 
                v-for="(chapter, idx) in quizData" 
                :key="idx"
                @click="goToChapter(idx); showNavigation = false"
                class="nav-btn"
                :class="{ 'active': currentChapterIndex === idx }"
              >
                {{ idx + 1 }}. {{ chapter.chapter_title }}
              </button>
            </div>
          </div>
          
          <!-- Navigation Overlay -->
          <div v-if="showNavigation" class="nav-overlay" @click="showNavigation = false"></div>
          
          <div class="quiz-container">
            <div v-for="(chapter, idx) in quizData" :key="idx" :id="`chapter-${idx}`" class="quiz-chapter">
              <h4 class="quiz-chapter-title">{{ chapter.chapter_title }}</h4>
              
              <div class="questions-list">
                <div v-for="(question, qIdx) in chapter.questions" :key="qIdx" class="question-card">
                  <div class="question-header">
                    <span class="question-number">Q{{ qIdx + 1 }}</span>
                    <h5 class="question-text">{{ question.문제 }}</h5>
                  </div>
                  
                  <div class="options-grid">
                    <button 
                      v-for="(option, optKey) in question.선택지" 
                      :key="optKey" 
                      @click="selectAnswer(idx, qIdx, optKey)"
                      class="option-button"
                      :class="{
                        'selected': isAnswerSelected(idx, qIdx, optKey),
                        'correct': shouldShowExplanation(idx, qIdx) && isCorrectAnswer(idx, qIdx, optKey),
                        'incorrect': shouldShowExplanation(idx, qIdx) && isAnswerSelected(idx, qIdx, optKey) && !isCorrectAnswer(idx, qIdx, optKey)
                      }"
                      :disabled="shouldShowExplanation(idx, qIdx)"
                    >
                      <span class="option-number">{{ optKey }}</span>
                      <span class="option-text">{{ option }}</span>
                    </button>
                  </div>
                  
                  <div v-if="shouldShowExplanation(idx, qIdx)" class="question-footer">
                    <div class="correct-answer">
                      <strong>정답: {{ question.정답 }}</strong>
                    </div>
                    <div class="explanation">
                      <p>{{ question.해설 }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LectureAnalyzer',
  data() {
    return {
      selectedFile: null,
      uploading: false,
      sessionId: null,
      summaryLoading: false,
      quizLoading: false,
      summaryData: null,
      quizData: null,
      hasSummary: false,
      isDragOver: false,
      currentChapterIndex: 0,
      userAnswers: {},
      showExplanations: {},
      showNavigation: false
    }
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0]
    },
    
    handleFileDrop(event) {
      this.isDragOver = false
      const files = event.dataTransfer.files
      if (files.length > 0 && files[0].type === 'application/pdf') {
        this.selectedFile = files[0]
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    removeFile() {
      this.selectedFile = null
      this.$refs.fileInput.value = ''
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    getTotalQuestions() {
      if (!this.quizData) return 0
      return this.quizData.reduce((total, chapter) => total + chapter.questions.length, 0)
    },
    
    selectAnswer(chapterIndex, questionIndex, selectedOption) {
      const key = `${chapterIndex}-${questionIndex}`
      this.userAnswers = { ...this.userAnswers, [key]: selectedOption }
      this.showExplanations = { ...this.showExplanations, [key]: true }
    },
    
    toggleNavigation() {
      this.showNavigation = !this.showNavigation
    },
    
    isAnswerSelected(chapterIndex, questionIndex, option) {
      const key = `${chapterIndex}-${questionIndex}`
      return this.userAnswers[key] === option
    },
    
    isCorrectAnswer(chapterIndex, questionIndex, option) {
      return this.quizData[chapterIndex].questions[questionIndex].정답 === option
    },
    
    shouldShowExplanation(chapterIndex, questionIndex) {
      const key = `${chapterIndex}-${questionIndex}`
      return this.showExplanations[key]
    },
    
    goToChapter(index) {
      this.currentChapterIndex = index
      this.$nextTick(() => {
        const element = document.getElementById(`chapter-${index}`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      })
    },
    
    async uploadPdf() {
      if (!this.selectedFile) return
      
      this.uploading = true
      const formData = new FormData()
      formData.append('file', this.selectedFile)
      
      try {
        const response = await axios.post('/api/v1/lecture/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        this.sessionId = response.data.session_id
        alert(`업로드 완료: ${response.data.filename}`)
      } catch (error) {
        alert('업로드 실패: ' + error.response?.data?.detail)
      } finally {
        this.uploading = false
      }
    },
    
    async generateSummary() {
      this.summaryLoading = true
      
      try {
        const response = await axios.post(`/api/v1/lecture/summarize/${this.sessionId}`)
        this.summaryData = response.data.data
        this.hasSummary = true
        alert('요약 생성 완료!')
      } catch (error) {
        alert('요약 생성 실패: ' + error.response?.data?.detail)
      } finally {
        this.summaryLoading = false
      }
    },
    
    async generateQuiz() {
      this.quizLoading = true
      
      try {
        const response = await axios.post(`/api/v1/lecture/quiz/${this.sessionId}`)
        this.quizData = response.data.data
        alert('퀴즈 생성 완료!')
      } catch (error) {
        alert('퀴즈 생성 실패: ' + error.response?.data?.detail)
      } finally {
        this.quizLoading = false
      }
    }
  },
  
  beforeUnmount() {
    // 컴포넌트 종료 시 세션 정리
    if (this.sessionId) {
      axios.delete(`/api/v1/lecture/cleanup/${this.sessionId}`)
    }
  }
}
</script>

<style scoped>
/* Lecture Analyzer - 심플·와이드 디자인 */
.lecture-analyzer {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fdff 0%, #e8f4fd 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Hero Section */
.hero {
  padding: 100px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.main-title {
  font-size: 3.5rem;
  font-weight: 800;
  color: #2c3e50;
  margin-bottom: 20px;
}

.sub-title {
  font-size: 1.6rem;
  color: #34495e;
  margin-bottom: 15px;
  font-weight: 600;
}

.description {
  font-size: 1.2rem;
  color: #7f8c8d;
  line-height: 1.6;
}

/* Section Styles */
.section {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-content {
  text-align: center;
}

.section-header {
  margin-bottom: 50px;
}

.section-header h2 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
  font-weight: 700;
}

.section-header p {
  font-size: 1.2rem;
  color: #7f8c8d;
  max-width: 600px;
  margin: 0 auto;
}

/* Upload Section */
.upload-section {
  background: rgba(255, 255, 255, 0.5);
}

.upload-area {
  max-width: 600px;
  margin: 0 auto;
}

.upload-box {
  border: 3px dashed #87ceeb;
  border-radius: 20px;
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  cursor: pointer;
  margin-bottom: 30px;
}

.upload-box.dragover {
  border-color: #5dade2;
  background: rgba(135, 206, 235, 0.1);
  transform: scale(1.02);
}

.upload-box.uploaded {
  border-color: #28a745;
  background: rgba(40, 167, 69, 0.05);
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  color: #87ceeb;
}

.upload-text {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 600;
}

.upload-hint {
  font-size: 1rem;
  color: #7f8c8d;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 20px;
  text-align: left;
}

.file-icon {
  font-size: 3rem;
  color: #28a745;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.file-size {
  font-size: 1rem;
  color: #7f8c8d;
}

.remove-btn {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.file-input {
  display: none;
}

.upload-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

/* Action Section */
.action-section {
  background: rgba(135, 206, 235, 0.1);
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 40px;
  max-width: 800px;
  margin: 0 auto;
}

.action-card {
  background: rgba(255, 255, 255, 0.9);
  padding: 40px 30px;
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-5px);
  border-color: #87ceeb;
  box-shadow: 0 10px 30px rgba(135, 206, 235, 0.2);
}

.action-card.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.action-icon {
  font-size: 3.5rem;
  margin-bottom: 20px;
  display: block;
}

.action-card h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
  font-weight: 600;
}

.action-card p {
  font-size: 1.1rem;
  color: #7f8c8d;
  line-height: 1.6;
  margin-bottom: 25px;
}

.action-btn {
  width: 100%;
  padding: 15px;
  font-size: 1.1rem;
}

.requirement-text {
  font-size: 0.9rem;
  color: #e74c3c;
  font-style: italic;
  margin-top: 10px;
}

/* Results Section */
.results-section {
  background: rgba(255, 255, 255, 0.7);
}

.result-block {
  margin-bottom: 60px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #87ceeb;
}

.result-header h3 {
  font-size: 2rem;
  color: #2c3e50;
  font-weight: 700;
}

.result-count {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
}

/* Chapter Cards */
.chapters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.chapter-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 15px;
  padding: 25px;
  display: flex;
  gap: 20px;
  transition: all 0.3s ease;
  border: 2px solid #e0f2fe;
}

.chapter-card:hover {
  transform: translateY(-3px);
  border-color: #87ceeb;
  box-shadow: 0 8px 25px rgba(135, 206, 235, 0.15);
}

.chapter-number {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
}

.chapter-content {
  flex: 1;
  text-align: left;
}

.chapter-title {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 600;
}

.chapter-summary {
  font-size: 1rem;
  color: #34495e;
  line-height: 1.6;
  margin-bottom: 15px;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  background: rgba(135, 206, 235, 0.2);
  color: #2980b9;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Quiz Styles */
.quiz-container {
  text-align: left;
}

.quiz-chapter {
  margin-bottom: 40px;
}

.quiz-chapter-title {
  font-size: 1.5rem;
  color: white;
  margin-bottom: 20px;
  padding: 18px 25px;
  background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
  border-radius: 15px;
  font-weight: 700;
  box-shadow: 0 4px 15px rgba(41, 128, 185, 0.3);
  border: 2px solid #2471a3;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.question-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 15px;
  padding: 25px;
  border: 2px solid #e0f2fe;
  transition: all 0.3s ease;
}

.question-card:hover {
  border-color: #87ceeb;
  box-shadow: 0 5px 20px rgba(135, 206, 235, 0.1);
}

.question-header {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.question-number {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  padding: 8px 12px;
  border-radius: 10px;
  font-weight: 600;
  flex-shrink: 0;
}

.question-text {
  font-size: 1.2rem;
  color: #2c3e50;
  font-weight: 600;
  line-height: 1.5;
  margin: 0;
}

/* Hamburger Button */
.hamburger-container {
  position: fixed;
  bottom: 30px;
  left: 30px;
  z-index: 1001;
}

.hamburger-btn {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 4px;
  box-shadow: 0 6px 20px rgba(135, 206, 235, 0.4);
  transition: all 0.3s ease;
}

.hamburger-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 25px rgba(135, 206, 235, 0.5);
}

.hamburger-btn span {
  width: 20px;
  height: 2px;
  background: white;
  border-radius: 1px;
  transition: all 0.3s ease;
}

.hamburger-btn.active span:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger-btn.active span:nth-child(2) {
  opacity: 0;
}

.hamburger-btn.active span:nth-child(3) {
  transform: rotate(-45deg) translate(7px, -6px);
}

/* Quiz Navigation */
.quiz-navigation {
  position: fixed;
  bottom: 30px;
  left: 30px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  padding: 25px;
  border: 3px solid #87ceeb;
  box-shadow: 0 12px 40px rgba(135, 206, 235, 0.3);
  backdrop-filter: blur(15px);
  max-width: 350px;
  z-index: 1000;
  transform: translateX(-400px);
  transition: transform 0.3s ease;
}

.quiz-navigation.show {
  transform: translateX(0);
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0f2fe;
}

.nav-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 700;
}

.close-nav {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-nav:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.nav-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.nav-btn {
  padding: 12px 16px;
  background: rgba(135, 206, 235, 0.1);
  border: 2px solid transparent;
  border-radius: 12px;
  color: #2980b9;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  font-size: 0.95rem;
}

.nav-btn:hover {
  background: rgba(135, 206, 235, 0.2);
  border-color: #87ceeb;
  transform: translateX(5px);
}

.nav-btn.active {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  border-color: #5dade2;
  transform: translateX(5px);
}

/* Navigation Overlay */
.nav-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 999;
  backdrop-filter: blur(2px);
}

.options-grid {
  display: grid;
  gap: 10px;
  margin-bottom: 20px;
}

.option-button {
  display: flex;
  gap: 12px;
  padding: 12px 15px;
  background: rgba(248, 249, 250, 0.8);
  border: 2px solid transparent;
  border-radius: 10px;
  align-items: center;
  transition: all 0.3s ease;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.option-button:hover:not(:disabled) {
  background: rgba(135, 206, 235, 0.1);
  border-color: #87ceeb;
  transform: translateY(-1px);
}

.option-button.selected {
  background: rgba(135, 206, 235, 0.2);
  border-color: #87ceeb;
}

.option-button.correct {
  background: rgba(40, 167, 69, 0.1);
  border-color: #28a745;
}

.option-button.incorrect {
  background: rgba(220, 53, 69, 0.1);
  border-color: #dc3545;
}

.option-button:disabled {
  cursor: not-allowed;
}

.option-number {
  background: #87ceeb;
  color: white;
  width: 25px;
  height: 25px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.option-button.correct .option-number {
  background: #28a745;
}

.option-button.incorrect .option-number {
  background: #dc3545;
}

.option-text {
  font-size: 1rem;
  color: #2c3e50;
}

.question-footer {
  border-top: 1px solid #e9ecef;
  padding-top: 15px;
}

.correct-answer {
  margin-bottom: 10px;
}

.correct-answer strong {
  color: #28a745;
  font-size: 1.1rem;
}

.explanation {
  background: rgba(135, 206, 235, 0.05);
  padding: 15px;
  border-radius: 10px;
  border-left: 4px solid #87ceeb;
}

.explanation p {
  margin: 0;
  color: #34495e;
  line-height: 1.6;
}

/* Button Styles */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 20px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(135, 206, 235, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  color: #2980b9;
  border: 2px solid #87ceeb;
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.2);
}

.btn-secondary:hover:not(:disabled) {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(135, 206, 235, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .main-title {
    font-size: 2.5rem;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .chapters-grid {
    grid-template-columns: 1fr;
  }
  
  .upload-box {
    padding: 40px 20px;
  }
  
  .section {
    padding: 60px 20px;
  }
  
  .result-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .hamburger-container {
    bottom: 20px;
    left: 20px;
  }
  
  .hamburger-btn {
    width: 50px;
    height: 50px;
  }
  
  .quiz-navigation {
    bottom: 20px;
    left: 20px;
    max-width: 280px;
    padding: 20px;
  }
  
  .nav-buttons {
    max-height: 200px;
  }
  
  .nav-btn {
    font-size: 0.85rem;
    padding: 10px 12px;
  }
}
</style>