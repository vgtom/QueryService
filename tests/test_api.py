import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    # Create a test token
    from app.auth import create_access_token
    token = create_access_token({"sub": "test_user"})
    return {"Authorization": f"Bearer {token}"}

def test_end_to_end_flow(client, auth_headers):
    # Store a query
    response = client.post(
        "/api/v1/queries/",
        json={"query_text": "SELECT * FROM users"},
        headers=auth_headers
    )
    assert response.status_code == 200
    query_id = response.json()["id"]
    
    # Get lineage
    lineage = client.get(f"/api/v1/queries/{query_id}/lineage", headers=auth_headers)
    assert lineage.status_code == 200
    
    # Get AI suggestions
    suggestions = client.post(
        "/api/v1/queries/analyze",
        json={"query_text": "SELECT * FROM users"},
        headers=auth_headers
    )
    assert suggestions.status_code == 200 