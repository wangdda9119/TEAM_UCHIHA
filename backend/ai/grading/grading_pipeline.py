import os
import zipfile
import tempfile
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader

class GradingPipeline:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
    def extract_zip(self, zip_path: str) -> List[str]:
        """ZIP 파일에서 PDF 추출"""
        print(f"🔍 ZIP 파일 추출 시작: {zip_path}")
        temp_dir = tempfile.mkdtemp()
        pdf_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print(f"📁 ZIP 내부 파일 목록: {[f.filename for f in zip_ref.filelist]}")
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('.pdf'):
                    zip_ref.extract(file_info, temp_dir)
                    extracted_path = os.path.join(temp_dir, file_info.filename)
                    pdf_files.append(extracted_path)
                    print(f"✅ PDF 추출: {file_info.filename} -> {extracted_path}")
        
        print(f"📊 총 {len(pdf_files)}개 PDF 파일 추출 완료")
        return pdf_files
    
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """파일명에서 학번, 과제명, 이름 추출"""
        basename = os.path.basename(filename).replace('.pdf', '')
        parts = basename.split('_')
        print(f"📝 파일명 파싱: {basename} -> {parts}")
        
        if len(parts) >= 3:
            result = {
                "student_id": parts[0],
                "assignment": parts[1], 
                "name": parts[2]
            }
            print(f"✅ 파싱 성공: {result}")
            return result
        
        result = {"student_id": "", "assignment": "", "name": basename}
        print(f"⚠️ 파싱 실패 (형식 불일치): {result}")
        return result
    
    def load_pdf_content(self, pdf_path: str) -> str:
        """PDF 내용 로드"""
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            return "\n".join([p.page_content for p in pages])
        except Exception as e:
            return f"PDF 로드 실패: {str(e)}"
    
    def grade_single_assignment(self, pdf_path: str, rubric: Dict) -> Dict:
        """단일 과제 채점"""
        print(f"📝 채점 시작: {os.path.basename(pdf_path)}")
        
        file_info = self.parse_filename(pdf_path)
        print(f"📄 PDF 내용 로드 시작...")
        content = self.load_pdf_content(pdf_path)
        print(f"📄 PDF 내용 로드 완료: {len(content)}자")
        
        # 채점 프롬프트
        prompt = PromptTemplate(
            input_variables=["content", "rubric"],
            template="""
당신은 대학교 과제 채점 AI입니다.

다음 Rubric에 따라 과제를 채점하세요:
{rubric}

과제 내용:
{content}

반드시 다음 JSON 형식으로만 응답하세요:
{{
  "scores": {{
    "항목1": 점수,
    "항목2": 점수
  }},
  "total_score": 총점,
  "feedback": "상세한 피드백"
}}
"""
        )
        
        try:
            print(f"🤖 LLM 채점 요청 시작...")
            response = self.llm.invoke(prompt.format(content=content, rubric=json.dumps(rubric, ensure_ascii=False)))
            print(f"🤖 LLM 응답 수신: {response.content[:200]}...")
            
            result = json.loads(response.content.strip())
            print(f"✅ 채점 성공: {file_info['name']} - 총점 {result.get('total_score', 0)}")
            
            return {
                "filename": os.path.basename(pdf_path),
                "student_id": file_info["student_id"],
                "name": file_info["name"],
                "assignment": file_info["assignment"],
                **result
            }
        except Exception as e:
            print(f"❌ 채점 실패: {file_info['name']} - {str(e)}")
            return {
                "filename": os.path.basename(pdf_path),
                "student_id": file_info["student_id"],
                "name": file_info["name"],
                "assignment": file_info["assignment"],
                "scores": {},
                "total_score": 0,
                "feedback": f"채점 실패: {str(e)}"
            }
    
    async def grade_assignments_parallel(self, pdf_files: List[str], rubric: Dict) -> List[Dict]:
        """병렬 채점 처리"""
        print(f"🚀 병렬 채점 시작: {len(pdf_files)}개 파일, 5개 워커")
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [
                loop.run_in_executor(executor, self.grade_single_assignment, pdf_file, rubric)
                for pdf_file in pdf_files
            ]
            print(f"🔄 {len(tasks)}개 작업 생성 완료, 대기 중...")
            results = await asyncio.gather(*tasks)
            print(f"✅ 병렬 채점 완료: {len(results)}개 결과")
        
        return results
    
    def create_excel_report(self, results: List[Dict], rubric: Dict) -> str:
        """Excel 보고서 생성"""
        print(f"📈 Excel 보고서 생성 시작: {len(results)}개 결과")
        
        # 데이터 정리
        rows = []
        for i, result in enumerate(results):
            row = {
                "파일명": result["filename"],
                "학번": result["student_id"],
                "이름": result["name"],
                "과제명": result["assignment"]
            }
            
            # Rubric 항목별 점수
            for item in rubric.keys():
                score = result["scores"].get(item, 0)
                row[f"{item}_점수"] = score
                print(f"📊 {result['name']}: {item} = {score}")
            
            row["총점"] = result["total_score"]
            row["피드백"] = result["feedback"]
            rows.append(row)
            print(f"✅ 데이터 정리 완료: {i+1}/{len(results)}")
        
        # DataFrame 생성
        print(f"📈 DataFrame 생성 중...")
        df = pd.DataFrame(rows)
        print(f"📈 DataFrame 생성 완료: {df.shape}")
        
        # Excel 파일 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        print(f"💾 Excel 파일 저장 중: {temp_file.name}")
        df.to_excel(temp_file.name, index=False, engine='openpyxl')
        print(f"✅ Excel 파일 생성 완료: {temp_file.name}")
        
        return temp_file.name