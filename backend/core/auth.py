# backend/core/auth.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.core.config import settings
from backend.core.redis_client import get_redis

# 비밀번호 해싱 - pbkdf2_sha256 사용 (길이 제한 없음)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT 설정
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def store_tokens_in_redis(user_id: int, access_token: str, refresh_token: str):
    redis_client = get_redis()
    # Access token (30분)
    redis_client.setex(f"access_token:{user_id}", ACCESS_TOKEN_EXPIRE_MINUTES * 60, access_token)
    # Refresh token (7일)
    redis_client.setex(f"refresh_token:{user_id}", REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, refresh_token)

def get_token_from_redis(user_id: int, token_type: str) -> Optional[str]:
    redis_client = get_redis()
    return redis_client.get(f"{token_type}:{user_id}")

def delete_tokens_from_redis(user_id: int):
    redis_client = get_redis()
    redis_client.delete(f"access_token:{user_id}")
    redis_client.delete(f"refresh_token:{user_id}")