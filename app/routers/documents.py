import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import DocumentModel, ChunkModel
from app.models.pydantic_models import (
    DocumentMetadata,
    DocumentUploadResponse,
    DocumentListResponse,
    ChunkDetail
)
from app.services.document_processor import document_processor
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["Document Management"])

@router.post("/upload",
response_model=List[DocumentUploadResponse])           
async def upload_documents(
    
    files: List[UploadFile] =  File(...),
    db: Session = Depends(get_db)
):
    """@router.post("/upload
    Upload one or more PDF documents.
    Extracts text, chunks content, generates embeddings, and classifies document.
    """
    responses = []
    
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' is not a valid PDF file."
            )
        
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        doc_entry = DocumentModel(
            id=doc_id,
            filename=file.filename,
            file_path=file_path,
            processing_status="PENDING"
        )
        db.add(doc_entry)
        db.commit()
        db.refresh(doc_entry)

        # Process document (extraction, chunking, classification, indexing)
        try:
            processed_doc = document_processor.process_pdf(file_path, doc_id, db)
            responses.append(
                DocumentUploadResponse(
                    message=f"Document '{file.filename}' uploaded and processed successfully.",
                    document=DocumentMetadata.model_validate(processed_doc)
                )
            )
        except Exception as e:
            responses.append(
                DocumentUploadResponse(
                    message=f"Document '{file.filename}' uploaded but processing failed: {str(e)}",
                    document=DocumentMetadata.model_validate(doc_entry)
                )
            )

    return responses

@router.get("/", response_model=DocumentListResponse)
def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all uploaded documents with optional filtering by category or filename search.
    """
    query = db.query(DocumentModel)
    if category:
        query = query.filter(DocumentModel.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(DocumentModel.filename.ilike(f"%{search}%"))
    
    docs = query.order_by(DocumentModel.upload_timestamp.desc()).all()
    return DocumentListResponse(
        total=len(docs),
        documents=[DocumentMetadata.model_validate(d) for d in docs]
    )

@router.get("/{document_id}", response_model=DocumentMetadata)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """
    Get detailed metadata for a specific document by ID.
    """
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentMetadata.model_validate(doc)

@router.get("/{document_id}/chunks", response_model=List[ChunkDetail])
def get_document_chunks(document_id: str, db: Session = Depends(get_db)):
    """
    Get all processed chunks of a document.
    """
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    chunks = db.query(ChunkModel).filter(ChunkModel.document_id == document_id).order_by(ChunkModel.chunk_index.asc()).all()
    return [ChunkDetail.model_validate(c) for c in chunks]

@router.post("/{document_id}/reprocess", response_model=DocumentMetadata)
def reprocess_document(document_id: str, db: Session = Depends(get_db)):
    """
    Reprocess a document (re-extract, re-chunk, re-classify, and re-index).
    """
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Original PDF file missing on disk.")

    processed_doc = document_processor.process_pdf(doc.file_path, document_id, db)
    return DocumentMetadata.model_validate(processed_doc)

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Delete an uploaded document and its chunks from DB, disk, and FAISS index.
    """
    doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    # Remove file from disk
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    # Remove vectors from FAISS index if vector store service is initialized
    try:
        from app.services.vector_store import vector_store_service
        vector_store_service.delete_document(document_id)
    except Exception as e:
        print(f"Vector delete notice: {e}")

    db.delete(doc)
    db.commit()
    return {"message": f"Document '{doc.filename}' (ID: {document_id}) deleted successfully."}
