from dotenv import load_dotenv
load_dotenv()

import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader


# ============================================
# 📌 1. 단원 분리 프롬프트
# ============================================
chapter_llm_prompt = PromptTemplate(
    input_variables=["content"],
    template="""
당신은 강의 PDF 내용을 분석하여 단원을 자동으로 분리하는 AI입니다.

다음 PDF 텍스트를 읽고 단원을 구조적으로 나누세요.
각 단원은 반드시 "단원제목", "요약", "핵심키워드"를 포함해야 하며  
JSON 형식으로만 출력하세요.

출력 형식 예시:

{{
  "chapters": [
    {{
      "단원제목": "단원 제목",
      "요약": "요약 내용",
      "핵심키워드": ["키워드1", "키워드2"]
    }}
  ]
}}

PDF 내용:
{content}
"""
)

# ============================================
# 📌 2. 강의 PDF 로더
# ============================================
class LectureProcessor:

    def __init__(self, pdf_path):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 없음: {pdf_path}")

        self.pdf_path = pdf_path
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2
        )

    # -----------------------------
    # 📄 PDF → 텍스트 로딩
    # -----------------------------
    def load_pdf(self):
        print("📄 PDF 로딩 중…")
        loader = PyPDFLoader(self.pdf_path)
        pages = loader.load()
        return "\n".join([p.page_content for p in pages])

    # -----------------------------
    # 📚 단원 자동 분리
    # -----------------------------
    def split_chapters(self, text):
        print("📚 단원 자동 분리 중...")

        response = self.llm.invoke(
            chapter_llm_prompt.format(content=text)
        )

        raw = response.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            raw = raw.replace("json", "").strip()

        try:
            return json.loads(raw)
        except Exception:
            print("❌ JSON 파싱 실패. 원본 출력:")
            print(raw)
            raise

    # -----------------------------
    # 📝 단원별 문제 생성 (선택지 + 해설 추가)
    # -----------------------------
    def generate_questions(self, chapters):

        print("📝 단원별 문제 생성 중…")

        question_prompt = PromptTemplate(
            input_variables=["chapter_title", "summary"],
            template="""
당신은 대학 강의 평가 문제 생성 AI입니다.

아래 단원의 요약을 기반으로 정확한 객관식 문제 3개를 생성하세요.
아래 JSON 구조를 **절대 변경하지 마세요.**

반드시 이 JSON 형식으로 출력해야 합니다:

{{
  "chapter_title": "{chapter_title}",
  "questions": [
    {{
      "문제": "문장을 여기에 생성",
      "선택지": {{
        "1": "선택지1",
        "2": "선택지2",
        "3": "선택지3",
        "4": "선택지4"
      }},
      "정답": "정답번호(1~4)",
      "해설": "정답 이유를 여기에 작성"
    }},
    ...
  ]
}}

단원 요약:
{summary}
"""
        )

        results = []

        for chap in chapters["chapters"]:
            title = chap["단원제목"]
            summary = chap["요약"]

            # LLM 호출
            response = self.llm.invoke(
                question_prompt.format(
                    chapter_title=title,
                    summary=summary
                )
            )

            raw = response.content.strip()

            # 코드블록 제거
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                raw = raw.replace("json", "").strip()

            try:
                data = json.loads(raw)   # chapter_title 포함 JSON
                results.append(data)
            except Exception:
                print("⚠️ 문제 JSON 파싱 실패:")
                print(raw)

        return results


    # -----------------------------
    # ✅ 자동 채점 기능
    # -----------------------------
    def check_answer(self, question_obj, user_answer):
        correct = question_obj["정답"].strip().upper()
        user = user_answer.strip().upper()

        if user == correct:
            return {
                "결과": "정답입니다! 🎉",
                "정답": correct,
                "해설": question_obj.get("해설", "해설 없음")
            }
        else:
            return {
                "결과": "오답입니다 ❌",
                "당신의 답": user,
                "정답": correct,
                "해설": question_obj.get("해설", "해설 없음")
            }


# ============================================
# 📌 실행 테스트
# ============================================
if __name__ == "__main__":

    pdf_path = "../vector/pdfs/고급인공지능 - 5 (10주차).pdf"

    processor = LectureProcessor(pdf_path)

    text = processor.load_pdf()

    chapters_json = processor.split_chapters(text)
    print("\n=== 📌 단원 분리 결과 ===")
    print(json.dumps(chapters_json, ensure_ascii=False, indent=2))

    questions = processor.generate_questions(chapters_json)
    print("\n=== 📝 단원별 문제 ===")
    print(json.dumps(questions, ensure_ascii=False, indent=2))

    
    # 테스트용 문제 풀이 (선택적)
    if questions:
        chapter = questions[0]   
        print(f"\n[단원] {chapter['chapter_title']}\n")
        
        print("📘 이제부터 문제를 풀어보세요!\n")
        
        # 문제 하나씩 풀기
        for idx, q in enumerate(chapter["questions"], start=1):
            print(f"\n문제 {idx}: {q['문제']}\n")
            
            # 선택지 출력
            for opt, txt in q["선택지"].items():
                print(f"{opt}. {txt}")
            
            # 사용자 입력
            user_answer = input("\n당신의 답(1/2/3/4): ").strip()
            
            while user_answer not in ["1", "2", "3", "4"]:
                user_answer = input("1/2/3/4 중에서 선택하세요: ").strip()
            
            # 채점
            result = processor.check_answer(q, user_answer)
            
            print("\n=== 채점 결과 ===")
            print(result["결과"])
            print(f"정답: {result['정답']}")
            print(f"해설: {result['해설']}")
            print("------------------------------------")
        
        print("\n🎉 모든 문제 풀이 완료! 고생했어!")
