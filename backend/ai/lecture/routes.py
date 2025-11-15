from fastapi import APIRouter, UploadFile, File
from .lecture_pipeline import process_lecture_pdf

router = APIRouter(prefix="/lecture", tags=["Lecture Analysis"])

@router.post("/upload")
async def upload_lecture_pdf(file: UploadFile = File(...)):
    """
    교수님 수업 PDF 업로드 → 단원별 요약 + 문제 생성
    """
    try:
        # PDF 파일 저장
        save_path = f"temp/{file.filename}"
        with open(save_path, "wb") as f:
            f.write(await file.read())

        # 분석 실행
        result = process_lecture_pdf(save_path)

        return {
            "status": "success",
            "filename": file.filename,
            "result": result,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
