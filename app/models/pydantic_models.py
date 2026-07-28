from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    upload_timestamp: datetime
    total_pages: int
    total_chunks: int
    processing_status: str
    category: str
    category_confidence: float
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentMetadata

class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentMetadata]

class ChunkDetail(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    page_number: int
    content: str
    char_count: int

    class Config:
        from_attributes = True

# Search models
class SearchRequest(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    search_mode: str = "semantic"  # semantic, keyword, hybrid
    top_k: int = 5

class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    content: str
    score: float
    search_mode: str

class SearchResponse(BaseModel):
    query: str
    search_mode: str
    results_count: int
    results: List[SearchResultItem]

# QA models
class QARequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    top_k: int = 4

class Citation(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    snippet: str

class QAResponse(BaseModel):
    question: str
    session_id: str
    answer: str
    sources: List[Citation]
    confidence_score: float
    context_retrieved: List[str]

# Summary & Comparison models
class SummaryRequest(BaseModel):
    document_id: str
    summary_type: str = "all"  # executive, technical, bullet, takeaways, all

class SummaryResponse(BaseModel):
    document_id: str
    document_name: str
    executive_summary: Optional[str] = None
    technical_summary: Optional[str] = None
    bullet_point_summary: Optional[List[str]] = None
    key_takeaways: Optional[List[str]] = None

class ComparisonRequest(BaseModel):
    document_ids: List[str]

class ComparisonResponse(BaseModel):
    document_ids: List[str]
    document_names: List[str]
    similarities: str
    differences: str
    methodologies: str
    conclusions: str
    comparison_matrix: Dict[str, Any]

# Analytics models
class AnalyticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_embeddings: int
    total_questions_answered: int
    categories_breakdown: Dict[str, int]
    most_queried_documents: List[Dict[str, Any]]

# ML Classifier models
class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    predicted_category: str
    confidence: float
    probabilities: Dict[str, float]
