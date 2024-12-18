import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Query, QueryLineage
from app.cache import CacheService

# Use SQLite in-memory database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_db():
    # Set test database URL
    # os.environ["DATABASE_URL"] = TEST_DATABASE_URL.strip('"')

    # Use the testing engine
    test_engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_db):
    Session = sessionmaker(bind=create_engine(TEST_DATABASE_URL))
    session = Session()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def redis_service():
    # Use environment variables for Redis configuration
    cache = CacheService(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=1  # Use different DB for tests
    )
    
    # Clear test database before each test
    cache.redis.flushdb()
    return cache 