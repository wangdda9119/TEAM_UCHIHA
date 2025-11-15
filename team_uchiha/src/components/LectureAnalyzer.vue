<template>
  <div class="lecture-analyzer">
    <h2>📚 강의 PDF 분석기</h2>
    
    <!-- PDF 업로드 -->
    <div class="upload-section">
      <input 
        type="file" 
        @change="handleFileUpload" 
        accept=".pdf"
        :disabled="uploading"
        ref="fileInput"
      />
      <button @click="uploadPdf" :disabled="!selectedFile || uploading" class="btn btn-primary">
        {{ uploading ? '업로드 중...' : 'PDF 업로드' }}
      </button>
    </div>

    <!-- 업로드 완료 후 버튼들 -->
    <div v-if="sessionId" class="action-buttons">
      <button 
        @click="generateSummary" 
        :disabled="summaryLoading"
        class="btn summary-btn"
      >
        {{ summaryLoading ? '요약 생성 중...' : '📝 단원별 요약' }}
      </button>
      
      <button 
        @click="generateQuiz" 
        :disabled="quizLoading || !hasSummary"
        class="btn quiz-btn"
      >
        {{ quizLoading ? '퀴즈 생성 중...' : '🎯 퀴즈 생성' }}
      </button>
    </div>

    <!-- 요약 결과 -->
    <div v-if="summaryData" class="summary-results">
      <h3>📋 단원별 요약</h3>
      <div v-for="(chapter, idx) in summaryData.chapters" :key="idx" class="chapter">
        <h4>{{ chapter.단원제목 }}</h4>
        <p>{{ chapter.요약 }}</p>
        <div class="keywords">
          <span v-for="keyword in chapter.핵심키워드" :key="keyword" class="keyword">
            {{ keyword }}
          </span>
        </div>
      </div>
    </div>

    <!-- 퀴즈 결과 -->
    <div v-if="quizData" class="quiz-results">
      <h3>🎯 생성된 퀴즈</h3>
      <div v-for="(chapter, idx) in quizData" :key="idx" class="quiz-chapter">
        <h4>{{ chapter.chapter_title }}</h4>
        <div v-for="(question, qIdx) in chapter.questions" :key="qIdx" class="question">
          <p><strong>Q{{ qIdx + 1 }}:</strong> {{ question.문제 }}</p>
          <div class="options">
            <div v-for="(option, optKey) in question.선택지" :key="optKey">
              {{ optKey }}. {{ option }}
            </div>
          </div>
          <p class="answer"><strong>정답:</strong> {{ question.정답 }}</p>
          <p class="explanation">{{ question.해설 }}</p>
        </div>
      </div>
    </div>
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
      hasSummary: false
    }
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0]
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

<style src="../assets/lecture.css" scoped></style>