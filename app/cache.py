from typing import Optional, Any
import redis
import json
from datetime import timedelta

class CacheService:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        
    def get(self, key: str) -> Optional[Any]:
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
        
    def set(self, key: str, value: Any, expire_in: int = 3600):
        self.redis.setex(
            key,
            timedelta(seconds=expire_in),
            json.dumps(value)
        )
        
    def invalidate(self, key: str):
        self.redis.delete(key) 