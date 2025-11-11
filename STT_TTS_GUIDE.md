# STT/TTS 통합 가이드

OpenAI의 Whisper (음성 인식)와 TTS (음성 합성) 기능을 사용한 테스트 예시입니다.

## 📋 프로젝트 구조

### 백엔드 (Python/FastAPI)

```
backend/
├── services/
│   ├── stt.py          # STT 서비스 (OpenAI Whisper)
│   └── tts.py          # TTS 서비스 (OpenAI TTS)
├── api/v1/routes/
│   └── stt_tts.py      # API 엔드포인트
└── core/
    └── config.py       # 설정 관리
```

### 프론트엔드 (Vue.js)

```
team_uchiha/src/
├── components/
│   └── SpeechInterface.vue    # STT/TTS 통합 UI
├── api/
│   └── speechClient.js        # API 클라이언트
└── utils/
    └── audioUtils.js          # 오디오 처리 유틸리티
```

## 🚀 설치 및 실행

### 1. OpenAI API 키 설정

**.env 파일에 다음을 추가하세요:**

```env
OPENAI_API_KEY=sk-proj-xxxxxx...
```

### 2. 백엔드 의존성 설치

```bash
pip install -r requirements.txt
```

**주요 패키지:**
- `openai>=1.51` - OpenAI API 클라이언트
- `fastapi>=0.115` - 웹 서버
- `python-multipart>=0.0.9` - 파일 업로드 처리

### 3. 백엔드 실행

```bash
python -m backend.app.main
# 또는
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

서버는 `http://localhost:8000`에서 실행됩니다.

### 4. 프론트엔드 실행

```bash
cd team_uchiha
npm install
npm run dev
```

프론트엔드는 `http://localhost:5173`에서 실행됩니다.

## 📡 API 엔드포인트

### 1. 음성 인식 (STT)

**엔드포인트:** `POST /api/v1/speech/transcribe`

**요청:**
```bash
curl -X POST http://localhost:8000/api/v1/speech/transcribe \
  -F "file=@audio.webm"
```

**응답:**
```json
{
  "text": "안녕하세요, 반갑습니다",
  "status": "success"
}
```

### 2. 음성 합성 (TTS)

**엔드포인트:** `POST /api/v1/speech/synthesize`

**요청:**
```bash
curl -X POST http://localhost:8000/api/v1/speech/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "안녕하세요",
    "voice": "alloy"
  }'
```

**응답:**
```json
{
  "status": "success",
  "audio": "4d5a9000...",  // 16진수 형식의 MP3 데이터
  "format": "mp3",
  "text": "안녕하세요"
}
```

### 3. 헬스 체크

**엔드포인트:** `GET /api/v1/speech/health`

## 🎯 주요 기능

### STT (음성 인식)

```javascript
import SpeechAPIClient from '@/api/speechClient.js';

// 오디오 파일 업로드 및 텍스트 변환
const text = await SpeechAPIClient.transcribeAudio(audioBlob);
console.log(text);  // "안녕하세요"
```

### TTS (음성 합성)

```javascript
import SpeechAPIClient from '@/api/speechClient.js';

// 텍스트를 오디오로 변환
const audioBlob = await SpeechAPIClient.synthesizeText(
  "안녕하세요",
  "alloy"  // 음성 선택
);

// 재생
const audio = new Audio(URL.createObjectURL(audioBlob));
audio.play();
```

### 오디오 녹음

```javascript
import AudioRecorder from '@/utils/audioUtils.js';

const recorder = new AudioRecorder();

// 녹음 시작
await recorder.startRecording();

// 녹음 중지 및 Blob 얻기
const audioBlob = await recorder.stopRecording();
```

## 🎨 UI/UX 특징

- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **리얼타임 피드백**: 녹음 중 애니메이션 표시
- **빠른 테스트**: 미리 정의된 테스트 문구
- **변환 이력**: 최근 10개의 변환 기록 유지
- **음성 선택**: alloy, echo, fable, onyx, nova, shimmer 중 선택
- **에러 핸들링**: 명확한 오류 메시지 표시

## 🔧 고급 사용

### 커스텀 음성 선택

SpeechInterface.vue에서 `voices` 배열 수정:

```javascript
voices: ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
```

### API 기본 URL 변경

speechClient.js에서 수정:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1/speech';
```

### 녹음 옵션 커스터마이징

audioUtils.js의 `getUserMedia` 옵션 수정:

```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,      // 에코 제거
    noiseSuppression: true,      // 노이즈 제거
    autoGainControl: true,       // 자동 게인 조절
  }
});
```

## 📝 모듈화 구조

### Backend

**STTService (backend/services/stt.py)**
- `transcribe(audio_data, format)`: 오디오를 텍스트로 변환
- OpenAI Whisper API 사용
- 한국어 지원

**TTSService (backend/services/tts.py)**
- `synthesize(text, voice)`: 텍스트를 오디오로 변환
- OpenAI TTS API 사용
- 6개의 음성 옵션 지원

### Frontend

**AudioRecorder (team_uchiha/src/utils/audioUtils.js)**
- `startRecording()`: 마이크 접근 및 녹음 시작
- `stopRecording()`: 녹음 중지 및 Blob 반환
- `playAudio(audioData)`: 오디오 재생

**SpeechAPIClient (team_uchiha/src/api/speechClient.js)**
- `transcribeAudio(audioBlob)`: STT 호출
- `synthesizeText(text, voice)`: TTS 호출
- `healthCheck()`: 서버 연결 확인

## ⚙️ 환경 변수

**.env 파일 설정:**

```env
# 필수
OPENAI_API_KEY=sk-proj-xxxxx

# 선택사항
DB_HOST=localhost
DB_PORT=5433
DB_NAME=uchiha_db
DB_USER=uchiha_itachi
DB_PASSWORD=sharingan
```

## 🐛 트러블슈팅

### 마이크 접근 실패

- 브라우저에서 마이크 권한 확인
- HTTPS 또는 localhost에서만 작동

### API 연결 실패

- 백엔드 서버 실행 확인: `http://localhost:8000/api/v1/speech/health`
- CORS 설정 확인 (FastAPI에 cors 미들웨어 추가 필요)

### OpenAI API 에러

- API 키 유효성 확인
- API 할당량 확인
- 계정 크레딧 확인

## 📚 참고 자료

- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [MediaRecorder API](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)

## 📄 라이선스

MIT License

## 💡 향후 개선 사항

- [ ] 실시간 스트리밍 (OpenAI Realtime API)
- [ ] 음성 이모션 감지
- [ ] 자동 언어 감지
- [ ] 다중 언어 지원
- [ ] 음성 파일 저장
- [ ] 배치 처리 지원
