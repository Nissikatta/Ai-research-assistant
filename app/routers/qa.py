from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import ConversationSessionModel, ConversationMessageModel
from app.models.pydantic_models import QARequest, QAResponse
from app.services.rag_engine import rag_engine

router = APIRouter(prefix="/api/qa", tags=["AI Question Answering & RAG"])

@router.post("/ask", response_model=QAResponse)
def ask_question(payload: QARequest, db: Session = Depends(get_db)):
    """
    Ask a question to the AI assistant using RAG across uploaded documents.
    Maintains conversational memory when session_id is provided.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    response = rag_engine.answer_question(
        db=db,
        question=payload.question,
        session_id=payload.session_id,
        document_ids=payload.document_ids,
        top_k=payload.top_k
    )
    return response

@router.get("/sessions/{session_id}/messages")
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """
    Get full conversation message history for a given session.
    """
    session = db.query(ConversationSessionModel).filter(ConversationSessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    messages = db.query(ConversationMessageModel).filter(
        ConversationMessageModel.session_id == session_id
    ).order_by(ConversationMessageModel.timestamp.asc()).all()

    return {
        "session_id": session_id,
        "title": session.title,
        "created_at": session.created_at,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
                "citations": m.citations
            }
            for m in messages
        ]
    }
