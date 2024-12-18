import pytest
from datetime import datetime
from app.services.query_service import QueryService
from app.models import Query

@pytest.fixture
def query_service():
    return QueryService()

@pytest.fixture
def sample_query():
    return "SELECT * FROM users WHERE id = 1"

def test_store_query(query_service, db_session, sample_query):
    # Test storing a query
    query = query_service.store_query(db_session, "user123", sample_query)
    assert query.user_id == "user123"
    assert query.query_text == sample_query
    
def test_get_queries_with_filters(query_service, db_session):
    # Test query retrieval with filters
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    queries = query_service.get_queries(
        db_session,
        user_id="user123",
        start_date=start_date,
        end_date=end_date
    )
    assert isinstance(queries, list) 