import pytest
from app.services.lineage_service import LineageService

@pytest.fixture
def lineage_service():
    return LineageService()

def test_extract_lineage_simple_query():
    query = "SELECT name, email FROM users JOIN orders ON users.id = orders.user_id"
    lineage = LineageService.extract_lineage(query)
    
    # Check tables are extracted
    tables = {table for table, _ in lineage if table is not None}
    assert "users" in tables
    assert "orders" in tables
    
    # Check columns are extracted
    columns = {col for _, col in lineage if col is not None}
    assert "name" in columns
    assert "email" in columns
    assert "id" in columns
    assert "user_id" in columns

def test_extract_lineage_complex_query():
    query = """
    WITH user_orders AS (
        SELECT user_id, COUNT(*) as order_count
        FROM orders
        GROUP BY user_id
    )
    SELECT u.name, uo.order_count
    FROM users u
    JOIN user_orders uo ON u.id = uo.user_id
    WHERE u.status = 'active'
    """
    lineage = LineageService.extract_lineage(query)
    
    # Verify CTE handling
    tables = {table for table, _ in lineage if table is not None}
    assert "users" in tables
    assert "orders" in tables 