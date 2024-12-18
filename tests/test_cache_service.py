import pytest
from app.cache import CacheService

def test_cache_set_get(redis_service):
    # Test basic set/get operations
    redis_service.set("test_key", {"data": "value"})
    result = redis_service.get("test_key")
    assert result == {"data": "value"}

def test_cache_invalidation(redis_service):
    # Test cache invalidation
    redis_service.set("test_key", {"data": "value"})
    redis_service.invalidate("test_key")
    result = redis_service.get("test_key")
    assert result is None

def test_cache_expiration(redis_service):
    # Test cache expiration
    redis_service.set("test_key", {"data": "value"}, expire_in=1)
    import time
    time.sleep(2)
    result = redis_service.get("test_key")
    assert result is None 