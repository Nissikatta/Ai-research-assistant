import sys
import os

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.services.classifier import classifier_service

def run_tests():
    print("==========================================")
    print("   RUNNING PROJECT INTEGRATION TEST SUITE ")
    print("==========================================")
    
    client = TestClient(app)

    # Test 1: Health Check Endpoint
    print("\n[Test 1] Health Check GET /")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert data["status"] == "online"
    print("  -> SUCCESS: Health Check OK")

    # Test 2: TensorFlow Classifier Service
    print("\n[Test 2] TensorFlow Document Classifier Service")
    text = "Convolutional Neural Networks and YOLO object detection models."
    cat, conf, probs = classifier_service.predict(text)
    print(f"  -> Predicted Category: '{cat}' (Confidence: {conf})")
    assert cat is not None
    print("  -> SUCCESS: Classifier Prediction OK")

    # Test 3: List Documents Endpoint
    print("\n[Test 3] List Documents GET /api/documents/")
    res = client.get("/api/documents/")
    assert res.status_code == 200
    docs = res.json()
    print(f"  -> Total Uploaded Documents: {docs['total']}")
    print("  -> SUCCESS: List Documents OK")

    # Test 4: Semantic Search Endpoint
    print("\n[Test 4] Semantic Search POST /api/search/")
    res = client.post("/api/search/", json={
        "query": "transformer architectures for natural language processing",
        "search_mode": "semantic",
        "top_k": 3
    })
    assert res.status_code == 200
    search_data = res.json()
    print(f"  -> Found {search_data['results_count']} results for query: '{search_data['query']}'")
    print("  -> SUCCESS: Semantic Search OK")

    # Test 5: Hybrid Search Endpoint
    print("\n[Test 5] Hybrid Search POST /api/search/")
    res = client.post("/api/search/", json={
        "query": "cyber security zero trust architecture",
        "search_mode": "hybrid",
        "top_k": 3
    })
    assert res.status_code == 200
    search_data = res.json()
    print(f"  -> Found {search_data['results_count']} hybrid search results")
    print("  -> SUCCESS: Hybrid Search OK")

    # Test 6: AI Question Answering & Citation Endpoint
    print("\n[Test 6] AI Question Answering POST /api/qa/ask")
    res = client.post("/api/qa/ask", json={
        "question": "What is Retrieval-Augmented Generation?",
        "top_k": 2
    })
    assert res.status_code == 200
    qa_data = res.json()
    print(f"  -> QA Session ID: {qa_data['session_id']}")
    print(f"  -> Confidence Score: {qa_data['confidence_score']}")
    print(f"  -> Citations Count: {len(qa_data['sources'])}")
    print("  -> SUCCESS: RAG Question Answering OK")

    # Test 7: Analytics Endpoint
    print("\n[Test 7] Knowledge Base Analytics GET /api/analytics/")
    res = client.get("/api/analytics/")
    assert res.status_code == 200
    analytics = res.json()
    print(f"  -> Total Docs: {analytics['total_documents']}, Total Chunks: {analytics['total_chunks']}, Total Embeddings: {analytics['total_embeddings']}")
    print("  -> SUCCESS: Knowledge Base Analytics OK")

    print("\n==========================================")
    print(" ALL 7 INTEGRATION TESTS PASSED CLEANLY!  ")
    print("==========================================")

if __name__ == "__main__":
    run_tests()
