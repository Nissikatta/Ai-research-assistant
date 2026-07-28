from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.pydantic_models import SearchRequest, SearchResponse, SearchResultItem
from app.services.search import search_service

router = APIRouter(prefix="/api/search", tags=["Semantic & Hybrid Search"])

@router.post("/", response_model=SearchResponse)
def execute_search(payload: SearchRequest, db: Session = Depends(get_db)):
    """
    Search documents using Semantic, Keyword, or Hybrid search strategies across uploaded files.
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    mode = payload.search_mode.lower()
    
    if mode == "semantic":
        raw_results = search_service.semantic_search(
            query=payload.query,
            top_k=payload.top_k,
            document_ids=payload.document_ids
        )
    elif mode == "keyword":
        raw_results = search_service.keyword_search(
            db=db,
            query=payload.query,
            top_k=payload.top_k,
            document_ids=payload.document_ids
        )
    elif mode == "hybrid":
        raw_results = search_service.hybrid_search(
            db=db,
            query=payload.query,
            top_k=payload.top_k,
            document_ids=payload.document_ids
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search mode '{payload.search_mode}'. Choose 'semantic', 'keyword', or 'hybrid'."
        )

    results = [
        SearchResultItem(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            document_name=r["document_name"],
            page_number=r["page_number"],
            content=r["content"],
            score=r["score"],
            search_mode=r["search_mode"]
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=payload.query,
        search_mode=mode,
        results_count=len(results),
        results=results
    )
