"""
Environment Setup Module
환경 변수를 안정적으로 로드하는 모듈
어디서든지 실행되어도 프로젝트 루트의 .env 파일을 찾음
"""

import os
from pathlib import Path
import dotenv
from loguru import logger

def setup_environment():
    """
    프로젝트 루트의 .env 파일을 찾아 환경 변수 로드
    다양한 실행 경로를 지원하는 일반화된 함수
    """
    
    # 현재 파일 위치 (backend/core/env_setup.py)
    current_file = Path(__file__).resolve()
    
    # 프로젝트 루트 찾기 (여러 경로 시도)
    possible_roots = [
        current_file.parent.parent.parent,  # backend/core/env_setup.py -> root
        Path.cwd(),  # 현재 작업 디렉토리
        Path.home(),  # 홈 디렉토리
    ]
    
    env_file = None
    
    for root in possible_roots:
        candidate = root / ".env"
        if candidate.exists():
            env_file = candidate
            break
    
    if env_file:
        logger.info(f"✅ .env 파일 찾음: {env_file}")
        dotenv.load_dotenv(str(env_file))
        
        # 환경 변수 로드 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info(f"✅ OPENAI_API_KEY 로드됨 (길이: {len(api_key)}자)")
        else:
            logger.warning("⚠️  OPENAI_API_KEY를 찾을 수 없습니다")
        
        return True
    else:
        logger.warning(f"⚠️  .env 파일을 찾을 수 없습니다")
        logger.info(f"   검색한 경로: {[str(p) for p in possible_roots]}")
        
        # 현재 디렉토리에서 시도
        logger.info("   현재 디렉토리에서 .env 파일 검색 중...")
        dotenv.load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            logger.info(f"✅ OPENAI_API_KEY 로드됨 (길이: {len(api_key)}자)")
            return True
        else:
            logger.error("❌ OPENAI_API_KEY를 로드할 수 없습니다")
            return False

# 모듈 임포트 시 자동 실행
setup_environment()
