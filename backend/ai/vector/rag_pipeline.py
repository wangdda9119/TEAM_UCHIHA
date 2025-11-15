import os
import pickle
from pathlib import Path
import traceback

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()


class RAGPipeline:
    def __init__(self):
        print("\n[RAG] ================== RAGPipeline 초기화 시작 ==================")

        # 1) API KEY
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"[RAG] OPENAI_API_KEY 존재 여부: {bool(api_key)}")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY 환경변수가 없습니다.")

        # 2) LLM / Embedding
        print("[RAG] ChatOpenAI / OpenAIEmbeddings 초기화 중...")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large"
        )

        # 3) 이 파일(rag_pipeline.py) 기준으로 경로 잡기
        base_dir = Path(__file__).resolve().parent  # backend/ai/vector
        index_dir = base_dir / "vectorstore" / "index"
        metadata_path = base_dir / "vectorstore" / "metadata.pkl"

        print(f"[RAG] base_dir      : {base_dir}")
        print(f"[RAG] index_dir     : {index_dir}")
        print(f"[RAG] metadata_path : {metadata_path}")
        print(f"[RAG] index_dir 존재?  {index_dir.exists()}")
        if index_dir.exists():
            print("[RAG] index_dir 내부 파일 목록:")
            for p in index_dir.iterdir():
                print(f"    - {p.name}")
        else:
            print("[RAG] ⚠️ index_dir 가 존재하지 않습니다. 경로를 확인하세요.")

        print(f"[RAG] metadata 존재?  {metadata_path.exists()}")

        # 4) FAISS 벡터스토어 로드
        try:
            print("📂 FAISS VectorStore 로드 시도...")
            self.vectorstore = FAISS.load_local(
                str(index_dir),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            print("✅ FAISS VectorStore 로드 성공")
        except Exception as e:
            print("❌ FAISS VectorStore 로드 중 예외 발생")
            print(f"   타입: {type(e).__name__}")
            print(f"   메시지: {e}")
            traceback.print_exc()
            raise

        # 5) 메타데이터 로드
        try:
            print("[RAG] 메타데이터(metadata.pkl) 로드 시도...")
            with metadata_path.open("rb") as f:
                self.metadata = pickle.load(f)
            print("✅ 메타데이터 로드 성공")
            # 메타데이터 타입과 대략적 크기 출력
            print(f"[RAG] metadata 타입: {type(self.metadata)}")
            if isinstance(self.metadata, dict):
                print(f"[RAG] metadata key 개수: {len(self.metadata)}")
                sample_keys = list(self.metadata.keys())[:5]
                print(f"[RAG] metadata 샘플 키: {sample_keys}")
        except Exception as e:
            print("❌ 메타데이터 로드 중 예외 발생")
            print(f"   타입: {type(e).__name__}")
            print(f"   메시지: {e}")
            traceback.print_exc()
            raise

        print("[RAG] ================== RAGPipeline 초기화 완료 ==================\n")

    # ----------------------------------------------------
    # 1) 검색 함수
    # ----------------------------------------------------
    def search(self, query: str, top_k: int = 4):
        print("\n[RAG.search] ================== 검색 시작 ==================")
        print(f"[RAG.search] query  : {query}")
        print(f"[RAG.search] top_k  : {top_k}")

        try:
            results = self.vectorstore.similarity_search(query, k=top_k)
            print(f"[RAG.search] 검색 결과 개수: {len(results)}")
            for i, doc in enumerate(results[:3]):
                meta = getattr(doc, "metadata", {})
                print(f"[RAG.search]  #{i+1} 메타: {meta}")
                print(f"[RAG.search]  #{i+1} 내용 앞 120자: {doc.page_content[:120].replace(os.linesep, ' ')}")
        except Exception as e:
            print("❌ [RAG.search] similarity_search 중 예외 발생")
            print(f"   타입: {type(e).__name__}")
            print(f"   메시지: {e}")
            traceback.print_exc()
            raise

        print("[RAG.search] ================== 검색 종료 ==================\n")
        return results

    # ----------------------------------------------------
    # 2) 최종 답변 생성
    # ----------------------------------------------------
    def answer(self, query: str) -> str:
        print("\n[RAG.answer] ================== answer 호출 ==================")
        print(f"[RAG.answer] 사용자 질문: {query}")

        # 1) 검색
        results = self.search(query)

        # 2) 컨텍스트 구성
        context_text = ""
        if not results:
            print("[RAG.answer] ⚠️ 검색 결과가 없습니다. 빈 컨텍스트로 진행합니다.")
        else:
            print(f"[RAG.answer] 컨텍스트용 문서 {len(results)}개 합치기...")
        for i, doc in enumerate(results):
            pdf_name = doc.metadata.get("pdf_name", "unknown")
            page = doc.metadata.get("page", "?")
            snippet = doc.page_content[:150].replace("\n", " ")
            print(f"[RAG.answer]  #{i+1} [{pdf_name} / p.{page}] snippet: {snippet}")
            context_text += f"[{pdf_name} / p.{page}]\n{doc.page_content}\n\n"

        # 3) 프롬프트 구성
        prompt_text = f"""
당신은 협성대학교 안내 AI입니다.
아래 문서를 참고하여 질문에 정확히 답변하세요.
문서에 없는 내용은 '해당 정보를 찾을 수 없습니다'라고 답하세요.

[검색된 문서]
{context_text}

[질문]
{query}

[답변]
"""
        print("[RAG.answer] 최종 프롬프트 앞 400자:")
        print(prompt_text[:400])

        # 4) LLM 호출
        try:
            response = self.llm.invoke(prompt_text)
        except Exception as e:
            print("❌ [RAG.answer] LLM 호출 중 예외 발생")
            print(f"   타입: {type(e).__name__}")
            print(f"   메시지: {e}")
            traceback.print_exc()
            raise

        print("\n[RAG.answer] 📝 생성된 답변:")
        print(response.content.strip())
        print("[RAG.answer] ================== answer 종료 ==================\n")
        return response.content


if __name__ == "__main__":
    rag = RAGPipeline()
    while True:
        q = input("\n질문하세요 (종료: q): ")
        if q == "q":
            break
        print("\n📘 최종 답변:")
        print(rag.answer(q))
