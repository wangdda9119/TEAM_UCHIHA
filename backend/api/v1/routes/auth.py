# backend/api/v1/routes/auth.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from backend.db.session import get_db
from backend.db.models import User
from backend.core.auth import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, store_tokens_in_redis, verify_token
)

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "student"  # student 또는 professor
    
    def validate_password(self):
        if len(self.password) > 72:
            raise ValueError("Password too long (max 72 characters)")
        if len(self.password) < 6:
            raise ValueError("Password too short (min 6 characters)")

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    try:
        # 비밀번호 검증
        if len(user_data.password) > 72:
            raise HTTPException(status_code=400, detail="Password too long (max 72 characters)")
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password too short (min 6 characters)")
        
        # 중복 확인
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # role 유효성 검사
        if user_data.role not in ["student", "professor"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'student' or 'professor'")
        
        # 사용자 생성
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
            is_verified=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"message": "User registered successfully", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    try:
        # 사용자 확인
        user = db.query(User).filter(User.username == user_data.username).first()
        if not user or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_verified:
            raise HTTPException(status_code=401, detail="Account not verified")
        
        # 토큰 생성
        token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Redis에 저장 (선택적)
        try:
            store_tokens_in_redis(user.id, access_token, refresh_token)
        except:
            pass  # Redis 없어도 로그인 가능
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout(token: str):
    payload = verify_token(token)
    if payload:
        user_id = int(payload.get("sub"))
        from backend.core.auth import delete_tokens_from_redis
        delete_tokens_from_redis(user_id)
    
    return {"message": "Logged out successfully"}