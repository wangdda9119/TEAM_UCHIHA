#!/usr/bin/env python3
# backend/db/create_test_users.py

from backend.db.session import SessionLocal
from backend.db.models import User
from backend.core.auth import get_password_hash

def create_test_users():
    db = SessionLocal()
    try:
        # 기존 테스트 사용자 삭제
        db.query(User).filter(User.username.in_(["professor", "student"])).delete(synchronize_session=False)
        
        # 교수 계정 생성
        professor = User(
            username="professor",
            email="professor@test.com",
            password_hash=get_password_hash("prof123"),
            role="professor",
            is_verified=True
        )
        
        # 학생 계정 생성
        student = User(
            username="student",
            email="student@test.com",
            password_hash=get_password_hash("stud123"),
            role="student",
            is_verified=True
        )
        
        db.add(professor)
        db.add(student)
        db.commit()
        
        print("✅ 테스트 사용자 생성 완료:")
        print("   교수: professor / prof123")
        print("   학생: student / stud123")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()