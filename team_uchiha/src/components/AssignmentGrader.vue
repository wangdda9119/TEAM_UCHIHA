<template>
  <div class="assignment-grader">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="main-title">⚡ 대용량 과제 자동 채점</h1>
        <p class="sub-title">수십 개의 과제를 한 번에 채점하고 결과를 시각화합니다</p>
        <p class="description">AI가 채점 기준에 따라 정확하게 채점하고 상세한 피드백을 제공합니다</p>
      </div>
    </section>

    <!-- Upload Section -->
    <section class="section upload-section">
      <div class="section-content">
        <div class="section-header">
          <h2>📁 1단계: 과제 ZIP 파일 업로드</h2>
          <p>{{학번}}_{과제명}_{이름}.pdf 형식의 파일들을 ZIP으로 묶어 업로드하세요</p>
        </div>
        
        <div class="upload-area">
          <div class="upload-box" :class="{ 'dragover': isDragOver, 'uploaded': selectedZip }" 
               @dragover.prevent="isDragOver = true" 
               @dragleave.prevent="isDragOver = false"
               @drop.prevent="handleZipDrop">
            <div v-if="!selectedZip" class="upload-placeholder">
              <div class="upload-icon">📁</div>
              <p class="upload-text">클릭하거나 ZIP 파일을 드래그하여 업로드</p>
              <p class="upload-hint">ZIP 파일만 지원됩니다</p>
            </div>
            <div v-else class="file-info">
              <div class="file-icon">🗃️</div>
              <div class="file-details">
                <p class="file-name">{{ selectedZip.name }}</p>
                <p class="file-size">{{ formatFileSize(selectedZip.size) }}</p>
              </div>
              <button @click="removeZipFile" class="remove-btn">×</button>
            </div>
          </div>
          
          <input 
            type="file" 
            @change="handleZipUpload" 
            accept=".zip"
            :disabled="uploading"
            ref="zipInput"
            class="file-input"
          />
          
          <div class="upload-actions">
            <button @click="triggerZipInput" :disabled="uploading" class="btn btn-secondary">
              📁 ZIP 파일 선택
            </button>
            <button @click="uploadZip" :disabled="!selectedZip || uploading" class="btn btn-primary">
              {{ uploading ? '업로드 중...' : '🚀 업로드 시작' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Rubric Section -->
    <section v-if="sessionId" class="section rubric-section">
      <div class="section-content">
        <div class="section-header">
          <h2>📋 2단계: 채점 기준 (Rubric) 설정</h2>
          <p>각 평가 항목과 배점을 설정하여 정확한 채점 기준을 만드세요</p>
        </div>
        
        <div class="rubric-container">
          <div class="rubric-grid">
            <div v-for="(item, index) in rubricItems" :key="index" class="rubric-card">
              <div class="rubric-number">{{ index + 1 }}</div>
              <div class="rubric-content">
                <input 
                  v-model="rubricItems[index].name" 
                  placeholder="평가 항목"
                  class="rubric-name-input"
                />
                <div class="score-section">
                  <input 
                    v-model.number="rubricItems[index].maxScore" 
                    type="number" 
                    placeholder="만점"
                    class="score-input"
                    min="1"
                    max="100"
                  />
                  <span>점</span>
                </div>
              </div>
              <button @click="removeRubricItem(index)" class="remove-btn">×</button>
            </div>
          </div>
          
          <div class="rubric-actions">
            <button @click="addRubricItem" class="btn btn-secondary">
              ➕ 항목 추가
            </button>
            
            <div class="total-score">
              <strong>총 배점: {{ totalScore }}점</strong>
            </div>
          </div>
          
          <div class="grading-action">
            <button 
              @click="startGrading" 
              :disabled="gradingLoading || rubricItems.length === 0 || !isRubricValid"
              class="btn btn-primary-large"
            >
              {{ gradingLoading ? '채점 중...' : '🎯 채점 시작' }}
            </button>
            <p v-if="!isRubricValid" class="validation-text">모든 항목에 이름과 배점을 입력해주세요</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Results Section -->
    <section v-if="gradingResults" class="section results-section">
      <div class="section-content">
        <div class="section-header">
          <h2>🎆 3단계: 채점 결과</h2>
          <p>AI가 채점한 결과를 확인하고 Excel로 다운로드하세요</p>
        </div>
        
        <div class="results-summary">
          <div class="summary-stats">
            <div class="stat-item">
              <div class="stat-number">{{ gradingResults.total_files }}</div>
              <div class="stat-label">채점 완료</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ getAverageScore() }}</div>
              <div class="stat-label">평균 점수</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ rubricItems.length }}</div>
              <div class="stat-label">평가 항목</div>
            </div>
          </div>
          
          <button @click="downloadExcel" class="btn btn-primary-large">
            📊 Excel 다운로드
          </button>
        </div>
        
        <!-- 랭킹 리스트 -->
        <div class="ranking-list">
          <h3>🏆 점수 랭킹</h3>
          <div class="ranking-items">
            <div v-for="(result, index) in getSortedResults()" :key="result.filename" class="ranking-item">
              <div class="rank-number" :class="getRankClass(index)">
                {{ index + 1 }}
              </div>
              <div class="rank-info">
                <span class="rank-name">{{ result.name || '이름 없음' }}</span>
                <span class="rank-id">({{ result.student_id || '학번 없음' }})</span>
              </div>
              <div class="rank-score">{{ result.total_score }}/{{ totalScore }}</div>
            </div>
          </div>
        </div>
        
        <div class="results-grid">
          <div v-for="result in gradingResults.results" :key="result.filename" class="result-card">
            <div class="result-header">
              <div class="student-info">
                <h4 class="student-name">{{ result.name || '이름 없음' }}</h4>
                <p class="student-id">{{ result.student_id || '학번 없음' }}</p>
                <p class="file-name">{{ result.filename }}</p>
              </div>
              <div class="total-score">
                <div class="score-circle" :class="getScoreClass(result.total_score)">
                  <span class="score-number">{{ result.total_score }}</span>
                  <span class="score-total">/{{ totalScore }}</span>
                </div>
              </div>
            </div>
            
            <div class="score-breakdown">
              <div v-for="item in rubricItems" :key="item.name" class="score-item">
                <div class="score-label">{{ item.name }}</div>
                <div class="score-bar">
                  <div class="score-bar-bg">
                    <div class="score-fill" :style="{ width: (result.scores[item.name] / item.maxScore) * 100 + '%' }"></div>
                  </div>
                  <span class="score-text">{{ result.scores[item.name] || 0 }}/{{ item.maxScore }}</span>
                </div>
              </div>
            </div>
            
            <div class="feedback-section">
              <h5>피드백</h5>
              <p class="feedback-text">{{ result.feedback }}</p>
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
  name: 'AssignmentGrader',
  data() {
    return {
      selectedZip: null,
      uploading: false,
      sessionId: null,
      rubricItems: [
        { name: '내용 완성도', maxScore: 30 },
        { name: '논리성', maxScore: 25 },
        { name: '창의성', maxScore: 25 },
        { name: '형식', maxScore: 20 }
      ],
      gradingLoading: false,
      gradingResults: null,
      isDragOver: false
    }
  },
  computed: {
    rubric() {
      const result = {}
      this.rubricItems.forEach(item => {
        if (item.name) {
          result[item.name] = item.maxScore
        }
      })
      return result
    },
    
    totalScore() {
      return this.rubricItems.reduce((sum, item) => sum + (item.maxScore || 0), 0)
    },
    
    isRubricValid() {
      return this.rubricItems.every(item => item.name && item.maxScore > 0)
    }
  },
  methods: {
    handleZipUpload(event) {
      this.selectedZip = event.target.files[0]
    },
    
    handleZipDrop(event) {
      this.isDragOver = false
      const files = event.dataTransfer.files
      if (files.length > 0 && files[0].name.endsWith('.zip')) {
        this.selectedZip = files[0]
      }
    },
    
    triggerZipInput() {
      this.$refs.zipInput.click()
    },
    
    removeZipFile() {
      this.selectedZip = null
      this.$refs.zipInput.value = ''
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    getAverageScore() {
      if (!this.gradingResults || !this.gradingResults.results.length) return 0
      const total = this.gradingResults.results.reduce((sum, result) => sum + result.total_score, 0)
      return Math.round(total / this.gradingResults.results.length)
    },
    
    getScoreClass(score) {
      const percentage = (score / this.totalScore) * 100
      if (percentage >= 90) return 'excellent'
      if (percentage >= 80) return 'good'
      if (percentage >= 70) return 'average'
      return 'poor'
    },
    
    getSortedResults() {
      if (!this.gradingResults || !this.gradingResults.results) return []
      return [...this.gradingResults.results].sort((a, b) => b.total_score - a.total_score)
    },
    
    getRankClass(index) {
      if (index === 0) return 'gold'
      if (index === 1) return 'silver'
      if (index === 2) return 'bronze'
      return 'normal'
    },
    
    async uploadZip() {
      if (!this.selectedZip) return
      
      console.log('📦 ZIP 업로드 시작:', this.selectedZip.name)
      this.uploading = true
      const formData = new FormData()
      formData.append('file', this.selectedZip)
      
      try {
        console.log('🚀 API 요청 전송 중...')
        const response = await axios.post('/api/v1/grading/upload-assignments', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        console.log('✅ 업로드 성공:', response.data)
        this.sessionId = response.data.session_id
        alert(`업로드 완료: ${response.data.filename}`)
      } catch (error) {
        console.error('❌ 업로드 실패:', error)
        alert('업로드 실패: ' + error.response?.data?.detail)
      } finally {
        this.uploading = false
      }
    },
    
    addRubricItem() {
      this.rubricItems.push({ name: '', maxScore: 10 })
    },
    
    removeRubricItem(index) {
      this.rubricItems.splice(index, 1)
    },
    
    async startGrading() {
      console.log('🎯 채점 시작:', this.sessionId)
      console.log('📋 Rubric:', this.rubric)
      
      this.gradingLoading = true
      
      const formData = new FormData()
      formData.append('rubric', JSON.stringify(this.rubric))
      
      try {
        console.log('🚀 채점 API 요청 전송...')
        const response = await axios.post(`/api/v1/grading/grade/${this.sessionId}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        console.log('✅ 채점 완료:', response.data)
        this.gradingResults = response.data
        alert('채점 완료!')
      } catch (error) {
        console.error('❌ 채점 실패:', error)
        alert('채점 실패: ' + error.response?.data?.detail)
      } finally {
        this.gradingLoading = false
      }
    },
    
    async downloadExcel() {
      console.log('📈 Excel 다운로드 시작:', this.sessionId)
      
      try {
        console.log('🚀 다운로드 API 요청...')
        const response = await axios.get(`/api/v1/grading/download-excel/${this.sessionId}`, {
          responseType: 'blob'
        })
        
        console.log('✅ 파일 다운로드 완료')
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'grading_results.xlsx')
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('❌ 다운로드 실패:', error)
        alert('다운로드 실패: ' + error.response?.data?.detail)
      }
    }
  },
  
  beforeUnmount() {
    if (this.sessionId) {
      axios.delete(`/api/v1/grading/cleanup/${this.sessionId}`)
    }
  }
}
</script>

<style scoped>
/* Assignment Grader - 심플·와이드 디자인 */
.assignment-grader {
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
  max-width: 900px;
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
  max-width: 700px;
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

/* Rubric Section */
.rubric-section {
  background: rgba(135, 206, 235, 0.1);
}

.rubric-container {
  max-width: 800px;
  margin: 0 auto;
  text-align: left;
}

.rubric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

@media (max-width: 1024px) {
  .rubric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .rubric-grid {
    grid-template-columns: 1fr;
  }
}

.rubric-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
  transition: all 0.3s ease;
  border: 2px solid #e0f2fe;
  text-align: center;
}

.rubric-card:hover {
  transform: translateY(-2px);
  border-color: #87ceeb;
  box-shadow: 0 8px 25px rgba(135, 206, 235, 0.15);
}

.rubric-number {
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

.rubric-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rubric-name-input {
  padding: 12px 16px;
  border: 2px solid #e0f2fe;
  border-radius: 10px;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.9);
}

.rubric-name-input:focus {
  outline: none;
  border-color: #87ceeb;
  box-shadow: 0 0 0 3px rgba(135, 206, 235, 0.1);
}

.score-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-section {
  justify-content: center;
}

.score-section label {
  font-weight: 600;
  color: #2c3e50;
}

.score-input {
  width: 80px;
  padding: 8px 12px;
  border: 2px solid #e0f2fe;
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
}

.score-input:focus {
  outline: none;
  border-color: #87ceeb;
}

.rubric-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 15px;
}

.total-score {
  font-size: 1.3rem;
  color: #2c3e50;
}

.grading-action {
  text-align: center;
}

.validation-text {
  color: #e74c3c;
  font-size: 1rem;
  margin-top: 10px;
  font-style: italic;
}

/* Results Section */
.results-section {
  background: rgba(255, 255, 255, 0.7);
}

.results-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  border: 2px solid #e0f2fe;
}

.summary-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: #2980b9;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 1rem;
  color: #7f8c8d;
  font-weight: 600;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.result-card {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 25px;
  border: 2px solid #e0f2fe;
  transition: all 0.3s ease;
}

.result-card:hover {
  transform: translateY(-3px);
  border-color: #87ceeb;
  box-shadow: 0 10px 30px rgba(135, 206, 235, 0.15);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.student-info {
  flex: 1;
}

.student-name {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 5px;
  font-weight: 700;
}

.student-id {
  font-size: 1rem;
  color: #7f8c8d;
  margin-bottom: 3px;
}

.file-name {
  font-size: 0.9rem;
  color: #95a5a6;
  font-style: italic;
}

.total-score {
  text-align: center;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  border: 4px solid;
}

.score-circle.excellent {
  background: rgba(40, 167, 69, 0.1);
  border-color: #28a745;
  color: #28a745;
}

.score-circle.good {
  background: rgba(23, 162, 184, 0.1);
  border-color: #17a2b8;
  color: #17a2b8;
}

.score-circle.average {
  background: rgba(255, 193, 7, 0.1);
  border-color: #ffc107;
  color: #ffc107;
}

.score-circle.poor {
  background: rgba(220, 53, 69, 0.1);
  border-color: #dc3545;
  color: #dc3545;
}

.score-number {
  font-size: 1.5rem;
}

.score-total {
  font-size: 0.9rem;
  opacity: 0.8;
}

.score-breakdown {
  margin-bottom: 20px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.score-label {
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.score-bar {
  flex: 2;
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-bar-bg {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.score-fill {
  height: 100%;
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.score-text {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2980b9;
  min-width: 50px;
}

.feedback-section {
  background: rgba(135, 206, 235, 0.05);
  padding: 15px;
  border-radius: 10px;
  border-left: 4px solid #87ceeb;
}

.feedback-section h5 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-weight: 600;
}

.feedback-text {
  color: #34495e;
  line-height: 1.6;
  margin: 0;
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

.btn-primary-large {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
  padding: 18px 36px;
  font-size: 1.2rem;
  box-shadow: 0 6px 25px rgba(135, 206, 235, 0.4);
}

.btn-primary-large:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(135, 206, 235, 0.5);
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

/* 랭킹 리스트 */
.ranking-list {
  margin-bottom: 40px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 25px;
  border: 2px solid #e0f2fe;
}

.ranking-list h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
  font-size: 1.5rem;
}

.ranking-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  background: rgba(248, 249, 250, 0.8);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.ranking-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(135, 206, 235, 0.2);
}

.rank-number {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.rank-number.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #b8860b;
}

.rank-number.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #696969;
}

.rank-number.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #daa520 100%);
  color: #8b4513;
}

.rank-number.normal {
  background: linear-gradient(135deg, #87ceeb 0%, #5dade2 100%);
  color: white;
}

.rank-info {
  flex: 1;
  text-align: left;
}

.rank-name {
  font-weight: 600;
  color: #2c3e50;
  margin-right: 8px;
}

.rank-id {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.rank-score {
  font-weight: 700;
  color: #2980b9;
  font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .main-title {
    font-size: 2.5rem;
  }
  
  .results-summary {
    flex-direction: column;
    gap: 20px;
  }
  
  .summary-stats {
    gap: 20px;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .ranking-items {
    grid-template-columns: 1fr;
  }
  
  .rubric-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .section {
    padding: 60px 20px;
  }
}
</style>