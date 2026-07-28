import os
import uuid
import re
from pypdf import PdfReader
from sqlalchemy.orm import Session
from app.db.models import DocumentModel, ChunkModel

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessorService:
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.replace('\x00', '')
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def process_pdf(self, file_path: str, document_id: str, db: Session) -> DocumentModel:
        doc = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID {document_id} not found")

        doc.processing_status = "PROCESSING"
        db.commit()

        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            doc.total_pages = total_pages

            # Clear existing chunks if reprocessing
            db.query(ChunkModel).filter(ChunkModel.document_id == document_id).delete()
            db.commit()

            chunks_to_insert = []
            chunk_idx = 0
            full_text_for_classification = []

            for page_num, page in enumerate(reader.pages, start=1):
                extracted = page.extract_text() or ""
                cleaned = self.clean_text(extracted)
                if not cleaned:
                    continue
                
                full_text_for_classification.append(cleaned)
                
                # Split page text into chunks
                page_chunks = self.splitter.split_text(cleaned)
                for chunk_text in page_chunks:
                    c_model = ChunkModel(
                        id=f"{document_id}_c{chunk_idx}",
                        document_id=document_id,
                        chunk_index=chunk_idx,
                        page_number=page_num,
                        content=chunk_text,
                        char_count=len(chunk_text)
                    )
                    chunks_to_insert.append(c_model)
                    chunk_idx += 1

            db.bulk_save_objects(chunks_to_insert)
            doc.total_chunks = len(chunks_to_insert)
            doc.processing_status = "COMPLETED"
            db.commit()
            db.refresh(doc)

            # Classify document using TensorFlow / heuristic classifier
            try:
                from app.services.classifier import classifier_service
                full_doc_text = " ".join(full_text_for_classification[:5])
                cat, conf, _ = classifier_service.predict(full_doc_text)
                doc.category = cat
                doc.category_confidence = conf
                db.commit()
            except Exception as e:
                doc.category = "Unclassified"
                doc.category_confidence = 0.0
                db.commit()

            # Index chunks in vector store
            try:
                from app.services.vector_store import vector_store_service
                chunks_data = [
                    {
                        "chunk_id": c.id,
                        "document_id": c.document_id,
                        "document_name": doc.filename,
                        "page_number": c.page_number,
                        "content": c.content
                    }
                    for c in chunks_to_insert
                ]
                vector_store_service.add_chunks(chunks_data)
            except Exception as e:
                print(f"Vector store indexing notice: {e}")

            return doc

        except Exception as err:
            doc.processing_status = "FAILED"
            doc.error_message = str(err)
            db.commit()
            raise err

document_processor = DocumentProcessorService()
