import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    total_pages = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    processing_status = Column(String, default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    category = Column(String, default="Unclassified")
    category_confidence = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)

    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan")

class ChunkModel(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    char_count = Column(Integer, nullable=False)

    document = relationship("DocumentModel", back_populates="chunks")

class QueryLogModel(Base):
    __tablename__ = "query_logs"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=True)
    query_text = Column(Text, nullable=False)
    search_mode = Column(String, default="semantic")  # semantic, keyword, hybrid
    response_text = Column(Text, nullable=True)
    documents_queried = Column(Text, nullable=True)  # JSON array string of doc IDs
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class ConversationSessionModel(Base):
    __tablename__ = "conversation_sessions"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    title = Column(String, default="New Conversation")

    messages = relationship("ConversationMessageModel", back_populates="session", cascade="all, delete-orphan")

class ConversationMessageModel(Base):
    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    citations = Column(Text, nullable=True)  # JSON string of citations

    session = relationship("ConversationSessionModel", back_populates="messages")
