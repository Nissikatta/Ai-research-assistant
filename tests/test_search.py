from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_semantic_search():
    response = client.post("/api/search/", json={
        "query": "transformer architectures for natural language processing",
        "search_mode": "semantic",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "transformer architectures for natural language processing"
    assert data["search_mode"] == "semantic"
    assert isinstance(data["results"], list)

def test_hybrid_search():
    response = client.post("/api/search/", json={
        "query": "cyber security and zero trust network",
        "search_mode": "hybrid",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert data["search_mode"] == "hybrid"
    assert isinstance(data["results"], list)
