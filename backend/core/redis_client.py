# backend/core/redis_client.py

import redis
from backend.core.config import settings

# Redis 클라이언트 초기화
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def get_redis():
    return redis_client

def get_redis_client():
    return redis_client