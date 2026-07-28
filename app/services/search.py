from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import ChunkModel, DocumentModel
from app.services.vector_store import vector_store_service

class SearchService:
    def keyword_search(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        query_terms = [t.strip().lower() for t in query.split() if len(t.strip()) > 2]
        if not query_terms:
            query_terms = [query.lower()]

        db_query = db.query(ChunkModel, DocumentModel.filename).join(
            DocumentModel, ChunkModel.document_id == DocumentModel.id
        )

        if document_ids:
            db_query = db_query.filter(ChunkModel.document_id.in_(document_ids))

        all_chunks = db_query.all()
        scored_results = []

        for chunk, filename in all_chunks:
            content_lower = chunk.content.lower()
            score = 0
            for term in query_terms:
                count = content_lower.count(term)
                score += count * 1.0

            if score > 0:
                scored_results.append({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_name": filename,
                    "page_number": chunk.page_number,
                    "content": chunk.content,
                    "score": round(score, 4),
                    "search_mode": "keyword"
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        raw_results = vector_store_service.search(query, top_k=top_k, document_ids=document_ids)
        for r in raw_results:
            r["search_mode"] = "semantic"
        return raw_results

    def hybrid_search(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        rrf_k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF) combining Keyword and Semantic Search.
        Score = 1 / (rrf_k + rank_semantic) + 1 / (rrf_k + rank_keyword)
        """
        sem_results = self.semantic_search(query, top_k=top_k * 2, document_ids=document_ids)
        kw_results = self.keyword_search(db, query, top_k=top_k * 2, document_ids=document_ids)

        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(sem_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            chunk_map[cid] = item

        for rank, item in enumerate(kw_results, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (rrf_k + rank))
            if cid not in chunk_map:
                chunk_map[cid] = item

        sorted_cids = sorted(rrf_scores.keys(), key=lambda c: rrf_scores[c], reverse=True)

        final_results = []
        for cid in sorted_cids[:top_k]:
            item = dict(chunk_map[cid])
            item["score"] = round(rrf_scores[cid], 5)
            item["search_mode"] = "hybrid"
            final_results.append(item)

        return final_results

search_service = SearchService()
