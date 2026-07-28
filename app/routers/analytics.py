from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.pydantic_models import AnalyticsResponse
from app.services.analytics import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Knowledge Base Analytics"])

@router.get("/", response_model=AnalyticsResponse)
def get_knowledge_base_analytics(db: Session = Depends(get_db)):
    """
    Get comprehensive statistics and analytics about uploaded documents, total chunks, embeddings, category distributions, and top queried documents.
    """
    return analytics_service.get_analytics(db=db)
