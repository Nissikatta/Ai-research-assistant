import uuid
import json
import requests
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.db.models import ConversationSessionModel, ConversationMessageModel, QueryLogModel
from app.services.search import search_service
from app.models.pydantic_models import Citation, QAResponse

class RAGEngineService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.model_name = settings.OLLAMA_MODEL

    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Calls local Ollama instance if active."""
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "").strip()
        except Exception:
            pass
        return None

    def _get_or_create_session(self, db: Session, session_id: Optional[str]) -> ConversationSessionModel:
        if session_id:
            sess = db.query(ConversationSessionModel).filter(ConversationSessionModel.id == session_id).first()
            if sess:
                return sess

        new_id = session_id or str(uuid.uuid4())
        sess = ConversationSessionModel(id=new_id, title="Research Conversation")
        db.add(sess)
        db.commit()
        db.refresh(sess)
        return sess

    def _get_history(self, db: Session, session_id: str, limit: int = 6) -> List[Dict[str, str]]:
        messages = db.query(ConversationMessageModel).filter(
            ConversationMessageModel.session_id == session_id
        ).order_by(ConversationMessageModel.timestamp.desc()).limit(limit).all()
        
        history = []
        for m in reversed(messages):
            history.append({"role": m.role, "content": m.content})
        return history

    def answer_question(
        self,
        db: Session,
        question: str,
        session_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        top_k: int = 4
    ) -> QAResponse:
        session = self._get_or_create_session(db, session_id)
        history = self._get_history(db, session.id)

        # 1. Expand query with conversation history if context contains implicit references ("its", "that paper")
        expanded_query = question
        if history:
            prev_user_msgs = [m["content"] for m in history if m["role"] == "user"]
            if prev_user_msgs:
                expanded_query = f"{prev_user_msgs[-1]} {question}"

        # 2. Retrieve relevant chunks using Hybrid Search
        retrieved_chunks = search_service.hybrid_search(
            db=db,
            query=expanded_query,
            top_k=top_k,
            document_ids=document_ids
        )

        # Grounding check: if top retrieval score is very low or no chunks returned
        if not retrieved_chunks or (retrieved_chunks and retrieved_chunks[0]["score"] < 0.001):
            unresolved_answer = "Answer could not be determined from the available documents."
            
            # Save message to session memory
            user_msg = ConversationMessageModel(id=str(uuid.uuid4()), session_id=session.id, role="user", content=question)
            assistant_msg = ConversationMessageModel(id=str(uuid.uuid4()), session_id=session.id, role="assistant", content=unresolved_answer)
            db.add_all([user_msg, assistant_msg])
            db.commit()

            return QAResponse(
                question=question,
                session_id=session.id,
                answer=unresolved_answer,
                sources=[],
                confidence_score=0.0,
                context_retrieved=[]
            )

        # 3. Format Context and Citations
        citations = []
        context_snippets = []
        context_text_block = ""

        for idx, chunk in enumerate(retrieved_chunks, start=1):
            c_info = Citation(
                document_id=chunk["document_id"],
                document_name=chunk["document_name"],
                page_number=chunk["page_number"],
                snippet=chunk["content"][:200] + "..."
            )
            citations.append(c_info)
            snippet = f"[Doc: {chunk['document_name']}, Page: {chunk['page_number']}]\n{chunk['content']}"
            context_snippets.append(snippet)
            context_text_block += f"\n--- Context Block {idx} ---\n{snippet}\n"

        # 4. Calculate Confidence Score
        top_score = retrieved_chunks[0]["score"]
        confidence_score = round(min(1.0, max(0.1, float(top_score) * 25.0 if top_score < 0.1 else float(top_score))), 2)

        # 5. Construct RAG Prompt
        history_str = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in history])
        
        prompt = f"""You are an AI Research & Knowledge Assistant. Answer the user's question based strictly on the retrieved document context provided below.
If the information is not present in the context, reply exactly with: "Answer could not be determined from the available documents."

Conversation History:
{history_str}

Retrieved Document Context:
{context_text_block}

User Question: {question}

Instructions:
- Provide a clear, grounded, and comprehensive response.
- Reference specific document names and page numbers in your text.
- Do not make up facts or extrapolate beyond the provided text.

Answer:"""

        # 6. Generate Response via Ollama or Synthesis Fallback
        generated_answer = self._call_ollama(prompt)

        if not generated_answer:
            # Smart deterministic RAG response synthesis if Ollama is offline
            top_content = "\n\n".join([f"From '{c['document_name']}' (Page {c['page_number']}): {c['content']}" for c in retrieved_chunks[:2]])
            generated_answer = (
                f"Based on the retrieved research documents:\n\n{top_content}\n\n"
                f"[Source Documents: {', '.join(set([c['document_name'] for c in retrieved_chunks]))}]"
            )

        # 7. Record to Database (Session Memory & Query Log)
        user_msg = ConversationMessageModel(id=str(uuid.uuid4()), session_id=session.id, role="user", content=question)
        assistant_msg = ConversationMessageModel(
            id=str(uuid.uuid4()),
            session_id=session.id,
            role="assistant",
            content=generated_answer,
            citations=json.dumps([c.model_dump() for c in citations])
        )
        query_log = QueryLogModel(
            id=str(uuid.uuid4()),
            session_id=session.id,
            query_text=question,
            search_mode="hybrid",
            response_text=generated_answer,
            documents_queried=json.dumps(list(set([c["document_id"] for c in retrieved_chunks])))
        )
        db.add_all([user_msg, assistant_msg, query_log])
        db.commit()

        return QAResponse(
            question=question,
            session_id=session.id,
            answer=generated_answer,
            sources=citations,
            confidence_score=confidence_score,
            context_retrieved=context_snippets
        )

rag_engine = RAGEngineService()
