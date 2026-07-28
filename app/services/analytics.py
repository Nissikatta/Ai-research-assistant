import json
from typing import Dict, Any, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import DocumentModel, ChunkModel, QueryLogModel, ConversationMessageModel
from app.services.vector_store import vector_store_service
from app.models.pydantic_models import AnalyticsResponse

class AnalyticsService:
    def get_analytics(self, db: Session) -> AnalyticsResponse:
        total_docs = db.query(func.count(DocumentModel.id)).scalar() or 0
        total_chunks = db.query(func.count(ChunkModel.id)).scalar() or 0
        total_embeddings = vector_store_service.get_total_embeddings()
        
        # Total questions answered (assistant messages or query logs)
        total_questions = db.query(func.count(QueryLogModel.id)).scalar() or 0
        
        # Categories breakdown
        cat_counts = db.query(
            DocumentModel.category, func.count(DocumentModel.id)
        ).group_by(DocumentModel.category).all()
        
        categories_map = {cat: count for cat, count in cat_counts}

        # Most queried documents calculation from QueryLogModel
        logs = db.query(QueryLogModel.documents_queried).filter(
            QueryLogModel.documents_queried.isnot(None)
        ).all()

        doc_query_counts: Dict[str, int] = {}
        for (doc_json,) in logs:
            if not doc_json:
                continue
            try:
                doc_ids = json.loads(doc_json)
                for did in doc_ids:
                    doc_query_counts[did] = doc_query_counts.get(did, 0) + 1
            except Exception:
                pass

        # Map document IDs to filenames
        most_queried = []
        if doc_query_counts:
            sorted_dids = sorted(doc_query_counts.keys(), key=lambda d: doc_query_counts[d], reverse=True)[:5]
            docs_map = {
                d.id: d.filename for d in db.query(DocumentModel).filter(DocumentModel.id.in_(sorted_dids)).all()
            }
            for did in sorted_dids:
                most_queried.append({
                    "document_id": did,
                    "filename": docs_map.get(did, "Unknown Document"),
                    "query_count": doc_query_counts[did]
                })

        return AnalyticsResponse(
            total_documents=total_docs,
            total_chunks=total_chunks,
            total_embeddings=total_embeddings,
            total_questions_answered=total_questions,
            categories_breakdown=categories_map,
            most_queried_documents=most_queried
        )

analytics_service = AnalyticsService()
