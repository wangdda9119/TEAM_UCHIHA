from dotenv import load_dotenv
load_dotenv()

import os
import pickle
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class FaissStoreBuilder:

    def __init__(self):
        """OpenAI 1024차원 한국어 임베딩 초기화"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

        # 🔹 최신 OpenAI 임베딩 (1024차원, 한국어 강함)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            api_key=api_key
        )

        # 🔹 리커시브 시멘틱 청킹 (600자 / 100자 오버랩)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # 🔹 PDF 목록 (여기 6개 맞음)
        self.pdf_files = [
            "pdfs/장학제도.pdf",
            "pdfs/수강신청 안내.pdf",
            "pdfs/수강신청 매뉴얼.pdf",
            "pdfs/2024_uhs.pdf",
            "pdfs/협성대학칙.pdf",
            "pdfs/통학버스 이용안내.pdf",
            "pdfs/개설시간표.pdf"
        ]


 


    # -------------------------------------------------
    # 1) PDF 로딩 + 청크 분할 + 메타데이터 부여
    # -------------------------------------------------
    def load_documents(self):
        documents = []

        for pdf_path in self.pdf_files:
            if not os.path.exists(pdf_path):
                print(f"❌ 파일 없음: {pdf_path}")
                continue

            pdf_name = os.path.basename(pdf_path)

            # 1) PDF 페이지 단위 로딩
            pages = PyPDFLoader(pdf_path).load()
            print(f"📄 {pdf_name} 페이지 수: {len(pages)}")

            # 2) Recursive Text Splitter로 청크 분할
            chunks = self.text_splitter.split_documents(pages)

            # 3) 각 청크에 메타데이터 부여 + 전체 리스트에 추가
            for idx, chunk in enumerate(chunks):
                chunk.metadata = {
                    "type": "pdf",
                    "pdf_name": pdf_name,
                    "source": pdf_path,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                }
                documents.append(chunk)

        print(f"🧩 총 청크 수: {len(documents)}개 생성")
        return documents


    


    # -------------------------------------------------
    # 2) 임베딩 → FAISS 저장
    # -------------------------------------------------
    def build_faiss_store(self):
        print("\n🔄 PDF → 임베딩 → FAISS 생성 중...\n")

        documents = self.load_documents()
        if len(documents) == 0:
            raise ValueError("❌ 로드된 문서가 없습니다. PDF 경로를 확인하세요.")

        # 벡터 DB 생성
        vectorstore = FAISS.from_documents(documents, self.embeddings)

        # 저장 폴더 생성
        os.makedirs("vectorstore", exist_ok=True)

        # FAISS 인덱스 저장
        vectorstore.save_local("vectorstore/index")

        # 메타데이터 저장
        metadata = [doc.metadata for doc in documents]
        with open("vectorstore/metadata.pkl", "wb") as f:
            pickle.dump(metadata, f)

        print("🎉 성공! FAISS VectorStore 저장 완료!\n")


# -------------------------------------------------
# 실행 진입점
# -------------------------------------------------
if __name__ == "__main__":
    store = FaissStoreBuilder()
    store.build_faiss_store()
    print("FAISS 구축 완료")
