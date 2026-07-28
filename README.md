# AI Research & Knowledge Assistant

## Overview
AI Research & Knowledge Assistant is a Retrieval-Augmented Generation (RAG) based document analysis system built with FastAPI. It allows users to upload PDF documents, perform semantic search, ask questions using AI, generate summaries, classify documents, and manage document analytics.

## Features
- PDF Upload
- Text Extraction
- Document Chunking
- Embedding Generation
- Semantic Search
- Hybrid Search
- AI Question Answering (RAG)
- Document Summarization
- Document Classification
- Conversation History
- Analytics

## Technologies
- Python
- FastAPI
- SQLAlchemy
- SQLite
- FAISS
- Sentence Transformers
- TensorFlow
- LangChain
- PyPDF
- Uvicorn

## Installation

bash
pip install -r requirements.txt


## Run

bash
uvicorn app.main:app --reload


Open:


http://127.0.0.1:8000/docs


## Project Structure


app/
 ├── db/
 ├── models/
 ├── routers/
 ├── services/
 ├── utils/
 ├── main.py


## API Endpoints

- POST /api/documents/upload
- GET /api/documents
- GET /api/documents/{document_id}
- GET /api/documents/{document_id}/chunks
- POST /api/documents/{document_id}/reprocess
- DELETE /api/documents/{document_id}
- POST /api/qa/ask

## Author

Nissi Katta# AI Research & Knowledge Assistant

## Overview
AI Research & Knowledge Assistant is a Retrieval-Augmented Generation (RAG) based document analysis system built with FastAPI. It allows users to upload PDF documents, perform semantic search, ask questions using AI, generate summaries, classify documents, and manage document analytics.

## Features
- PDF Upload
- Text Extraction
- Document Chunking
- Embedding Generation
- Semantic Search
- Hybrid Search
- AI Question Answering (RAG)
- Document Summarization
- Document Classification
- Conversation History
- Analytics

## Technologies
- Python
- FastAPI
- SQLAlchemy
- SQLite
- FAISS
- Sentence Transformers
- TensorFlow
- LangChain
- PyPDF
- Uvicorn

## Installation

bash
pip install -r requirements.txt


## Run

bash
uvicorn app.main:app --reload


Open:


http://127.0.0.1:8000/docs


## Project Structure

text
ai-research-assistant/
│
├── app/
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── models/
│   │   └── pydantic_models.py
│   │
│   ├── routers/
│   │   ├── documents.py
│   │   ├── qa.py
│   │   ├── search.py
│   │   ├── analytics.py
│   │   └── summarizer.py
│   │
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── vector_store.py
│   │   ├── rag_engine.py
│   │   ├── classifier.py
│   │   ├── search.py
│   │   ├── analytics.py
│   │   └── summarizer.py
│   │
│   ├── config.py
│   └── main.py
│
├── data/
├── ml/
├── postman/
├── scripts/
├── uploads/
├── requirements.txt
├── README.md
└── .env

## API Endpoints

- POST /api/documents/upload
- GET /api/documents
- GET /api/documents/{document_id}
- GET /api/documents/{document_id}/chunks
- POST /api/documents/{document_id}/reprocess
- DELETE /api/documents/{document_id}
- POST /api/qa/ask

## Author

Nissi Katta