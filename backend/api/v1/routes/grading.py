from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
import uuid
import json
import tempfile
import os
from backend.core.redis_client import get_redis_client
from backend.ai.grading.grading_pipeline import GradingPipeline

router = APIRouter(tags=["Grading"])

@router.post("/upload-assignments")
async def upload_assignments(file: UploadFile = File(...)):
    """과제 ZIP 파일 업로드"""
    print(f"📦 ZIP 업로드 시작: {file.filename}")
    
    if not file.filename.endswith('.zip'):
        print(f"❌ 파일 형식 오류: {file.filename}")
        raise HTTPException(400, "ZIP 파일만 업로드 가능합니다")
    
    session_id = str(uuid.uuid4())
    print(f"🎫 세션 ID 생성: {session_id}")
    
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        print(f"💾 임시 파일 저장: {tmp_path} ({len(content)} bytes)")
    
    # Redis에 저장
    redis_client = get_redis_client()
    session_data = {
        "filename": file.filename,
        "zip_path": tmp_path,
        "status": "uploaded"
    }
    redis_client.setex(
        f"grading:{session_id}",
        3600,
        json.dumps(session_data)
    )
    print(f"📊 Redis 저장 완료: grading:{session_id}")
    
    return {"session_id": session_id, "filename": file.filename}

@router.post("/grade/{session_id}")
async def grade_assignments(session_id: str, rubric: str = Form(...)):
    """과제 채점 실행"""
    print(f"🎯 채점 시작: {session_id}")
    
    redis_client = get_redis_client()
    data = redis_client.get(f"grading:{session_id}")
    
    if not data:
        print(f"❌ 세션 데이터 없음: {session_id}")
        raise HTTPException(404, "세션을 찾을 수 없습니다")
    
    session_info = json.loads(data)
    print(f"📊 세션 정보: {session_info}")
    
    try:
        # 진행상태 업데이트
        print(f"🔄 진행상태 업데이트: processing")
        redis_client.setex(f"grading_result:{session_id}", 3600, json.dumps({"status": "processing"}))
        
        # Rubric 파싱
        print(f"📋 Rubric 파싱: {rubric}")
        rubric_dict = json.loads(rubric)
        print(f"📋 Rubric 딕셔너리: {rubric_dict}")
        
        # 채점 파이프라인 실행
        print(f"🚀 채점 파이프라인 시작")
        pipeline = GradingPipeline()
        pdf_files = pipeline.extract_zip(session_info["zip_path"])
        
        if not pdf_files:
            print(f"❌ PDF 파일 없음")
            raise HTTPException(400, "ZIP 파일에 PDF가 없습니다")
        
        print(f"📝 총 {len(pdf_files)}개 PDF 파일 발견")
        
        # 병렬 채점
        print(f"🚀 병렬 채점 시작")
        results = await pipeline.grade_assignments_parallel(pdf_files, rubric_dict)
        print(f"✅ 병렬 채점 완료: {len(results)}개 결과")
        
        # Excel 보고서 생성
        print(f"📈 Excel 보고서 생성 시작")
        excel_path = pipeline.create_excel_report(results, rubric_dict)
        print(f"✅ Excel 보고서 생성 완료: {excel_path}")
        
        # 결과 저장
        result_data = {
            "status": "completed",
            "results": results,
            "excel_path": excel_path,
            "total_files": len(pdf_files)
        }
        redis_client.setex(f"grading_result:{session_id}", 3600, json.dumps(result_data))
        print(f"📊 결과 Redis 저장 완료")
        
        return {
            "status": "completed",
            "results": results,
            "total_files": len(pdf_files)
        }
        
    except Exception as e:
        print(f"❌ 채점 오류: {str(e)}")
        redis_client.setex(f"grading_result:{session_id}", 3600, json.dumps({
            "status": "error", 
            "message": str(e)
        }))
        raise HTTPException(500, f"채점 실패: {str(e)}")

@router.get("/download-excel/{session_id}")
async def download_excel(session_id: str):
    """Excel 보고서 다운로드"""
    print(f"📈 Excel 다운로드 요청: {session_id}")
    
    redis_client = get_redis_client()
    data = redis_client.get(f"grading_result:{session_id}")
    
    if not data:
        print(f"❌ 결과 데이터 없음: {session_id}")
        raise HTTPException(404, "결과를 찾을 수 없습니다")
    
    result_info = json.loads(data)
    print(f"📊 결과 상태: {result_info['status']}")
    
    if result_info["status"] != "completed":
        print(f"❌ 채점 미완료: {result_info['status']}")
        raise HTTPException(400, "채점이 완료되지 않았습니다")
    
    excel_path = result_info["excel_path"]
    print(f"💾 Excel 파일 경로: {excel_path}")
    
    if not os.path.exists(excel_path):
        print(f"❌ Excel 파일 없음: {excel_path}")
        raise HTTPException(404, "Excel 파일을 찾을 수 없습니다")
    
    print(f"✅ Excel 파일 다운로드 준비 완료")
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="grading_results.xlsx"
    )

@router.get("/status/{session_id}")
async def get_grading_status(session_id: str):
    """채점 진행상태 확인"""
    redis_client = get_redis_client()
    data = redis_client.get(f"grading_result:{session_id}")
    
    if not data:
        return {"status": "not_found"}
    
    return json.loads(data)

@router.delete("/cleanup/{session_id}")
async def cleanup_grading_session(session_id: str):
    """세션 정리"""
    redis_client = get_redis_client()
    
    # 파일 삭제
    grading_data = redis_client.get(f"grading:{session_id}")
    if grading_data:
        info = json.loads(grading_data)
        if os.path.exists(info["zip_path"]):
            os.unlink(info["zip_path"])
    
    result_data = redis_client.get(f"grading_result:{session_id}")
    if result_data:
        info = json.loads(result_data)
        if info.get("excel_path") and os.path.exists(info["excel_path"]):
            os.unlink(info["excel_path"])
    
    # Redis 키 삭제
    redis_client.delete(f"grading:{session_id}")
    redis_client.delete(f"grading_result:{session_id}")
    
    return {"status": "cleaned"}