from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
import json
from backend.core.redis_client import get_redis_client
from backend.ai.lecture.lecture_pipeline import LectureProcessor
import tempfile
import os

router = APIRouter(tags=["Lecture"])

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """PDF 업로드 및 Redis 저장"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "PDF 파일만 업로드 가능합니다")
    
    # 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # Redis에 파일 정보 저장 (1시간 TTL)
    redis_client = get_redis_client()
    redis_client.setex(
        f"pdf:{session_id}",
        3600,  # 1시간
        json.dumps({
            "filename": file.filename,
            "path": tmp_path,
            "status": "uploaded"
        })
    )
    
    return {"session_id": session_id, "filename": file.filename}

@router.post("/summarize/{session_id}")
async def generate_summary(session_id: str):
    """단원별 요약 생성"""
    redis_client = get_redis_client()
    pdf_data = redis_client.get(f"pdf:{session_id}")
    
    if not pdf_data:
        raise HTTPException(404, "세션을 찾을 수 없습니다")
    
    pdf_info = json.loads(pdf_data)
    
    try:
        # 진행상태 업데이트
        redis_client.setex(f"summary:{session_id}", 3600, json.dumps({"status": "processing"}))
        
        processor = LectureProcessor(pdf_info["path"])
        text = processor.load_pdf()
        chapters = processor.split_chapters(text)
        
        # 결과 저장
        redis_client.setex(f"summary:{session_id}", 3600, json.dumps({
            "status": "completed",
            "data": chapters
        }))
        
        return {"status": "completed", "data": chapters}
        
    except Exception as e:
        redis_client.setex(f"summary:{session_id}", 3600, json.dumps({"status": "error", "message": str(e)}))
        raise HTTPException(500, f"요약 생성 실패: {str(e)}")

@router.post("/quiz/{session_id}")
async def generate_quiz(session_id: str):
    """퀴즈 생성"""
    redis_client = get_redis_client()
    
    # 요약 데이터 확인
    summary_data = redis_client.get(f"summary:{session_id}")
    if not summary_data:
        raise HTTPException(404, "먼저 요약을 생성해주세요")
    
    summary_info = json.loads(summary_data)
    if summary_info["status"] != "completed":
        raise HTTPException(400, "요약이 완료되지 않았습니다")
    
    try:
        # 진행상태 업데이트
        redis_client.setex(f"quiz:{session_id}", 3600, json.dumps({"status": "processing"}))
        
        pdf_data = redis_client.get(f"pdf:{session_id}")
        pdf_info = json.loads(pdf_data)
        
        processor = LectureProcessor(pdf_info["path"])
        questions = processor.generate_questions(summary_info["data"])
        
        # 결과 저장
        redis_client.setex(f"quiz:{session_id}", 3600, json.dumps({
            "status": "completed",
            "data": questions
        }))
        
        return {"status": "completed", "data": questions}
        
    except Exception as e:
        redis_client.setex(f"quiz:{session_id}", 3600, json.dumps({"status": "error", "message": str(e)}))
        raise HTTPException(500, f"퀴즈 생성 실패: {str(e)}")

@router.get("/status/{session_id}/{task_type}")
async def get_status(session_id: str, task_type: str):
    """작업 진행상태 확인"""
    redis_client = get_redis_client()
    data = redis_client.get(f"{task_type}:{session_id}")
    
    if not data:
        return {"status": "not_found"}
    
    return json.loads(data)

@router.delete("/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    """세션 정리"""
    redis_client = get_redis_client()
    
    # PDF 파일 삭제
    pdf_data = redis_client.get(f"pdf:{session_id}")
    if pdf_data:
        pdf_info = json.loads(pdf_data)
        if os.path.exists(pdf_info["path"]):
            os.unlink(pdf_info["path"])
    
    # Redis 키 삭제
    redis_client.delete(f"pdf:{session_id}")
    redis_client.delete(f"summary:{session_id}")
    redis_client.delete(f"quiz:{session_id}")
    
    return {"status": "cleaned"}