#!/bin/bash
# Quick Start Script for STT/TTS Testing

echo "=========================================="
echo "🎤 TEAM_UCHIHA STT/TTS 테스트 환경 설정"
echo "=========================================="

# 1. 백엔드 설정
echo ""
echo "1️⃣  백엔드 의존성 설치 중..."
pip install -r requirements.txt

# 2. 프론트엔드 설정
echo ""
echo "2️⃣  프론트엔드 의존성 설치 중..."
cd team_uchiha
npm install
cd ..

# 3. 환경 변수 확인
echo ""
echo "3️⃣  환경 설정 확인..."
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY" .env; then
        echo "✅ OPENAI_API_KEY가 설정되어 있습니다"
    else
        echo "⚠️  OPENAI_API_KEY가 설정되지 않았습니다"
        echo "   .env 파일에 OPENAI_API_KEY를 추가하세요"
    fi
else
    echo "⚠️  .env 파일이 없습니다"
fi

# 4. 실행 안내
echo ""
echo "=========================================="
echo "✅ 설정 완료!"
echo "=========================================="
echo ""
echo "다음 명령어로 서버를 실행하세요:"
echo ""
echo "📌 백엔드 실행:"
echo "   python -m backend.app.main"
echo ""
echo "📌 프론트엔드 실행 (새 터미널):"
echo "   cd team_uchiha && npm run dev"
echo ""
echo "📌 또는 Docker로 실행:"
echo "   docker-compose up"
echo ""
echo "🌐 프론트엔드: http://localhost:5173"
echo "⚙️  백엔드:   http://localhost:8000"
echo "📚 Swagger:  http://localhost:8000/docs"
echo ""
