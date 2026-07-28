from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.pydantic_models import SummaryRequest, SummaryResponse, ComparisonRequest, ComparisonResponse
from app.services.summarizer import summarizer_service

router = APIRouter(prefix="/api/analysis", tags=["Summarization & Document Comparison"])

@router.post("/summarize", response_model=SummaryResponse)
def generate_summary(payload: SummaryRequest, db: Session = Depends(get_db)):
    """
    Generate multi-format document summaries (Executive Summary, Technical Summary, Bullet Points, Key Takeaways).
    """
    try:
        res = summarizer_service.summarize_document(
            db=db,
            document_id=payload.document_id,
            summary_type=payload.summary_type
        )
        return res
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(exc)}")

@router.post("/compare", response_model=ComparisonResponse)
def compare_documents(payload: ComparisonRequest, db: Session = Depends(get_db)):
    """
    Perform comparative analysis across 2 or more uploaded documents.
    """
    if not payload.document_ids or len(payload.document_ids) < 2:
        raise HTTPException(status_code=400, detail="Must provide at least two document IDs for comparison.")

    try:
        res = summarizer_service.compare_documents(db=db, document_ids=payload.document_ids)
        return res
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comparative analysis failed: {str(exc)}")
