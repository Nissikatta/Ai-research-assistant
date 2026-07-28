from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "AI Research" in data["app_name"]

def test_list_documents():
    response = client.get("/api/documents/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "documents" in data
    assert isinstance(data["documents"], list)

def test_analytics_endpoint():
    response = client.get("/api/analytics/")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_chunks" in data
    assert "total_embeddings" in data
