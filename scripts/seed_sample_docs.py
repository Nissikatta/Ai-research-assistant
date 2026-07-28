import os
import sys
from pypdf import PdfWriter
from io import BytesIO

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, init_db
from app.services.document_processor import document_processor
from app.db.models import DocumentModel
import uuid

SAMPLE_PAPERS = [
    {
        "filename": "Transformer_Architectures_in_NLP.pdf",
        "title": "Transformer Architectures in Natural Language Processing",
        "content": """
Abstract:
Transformer language models have revolutionized Natural Language Processing (NLP) through self-attention mechanisms, BERT, GPT models, sequence-to-sequence translation, tokenization, text classification, and named entity recognition (NER).
This paper explores multi-head attention mechanisms, positional encoding, and retrieval-augmented generation (RAG) architectures for enterprise knowledge bases.

1. Introduction
Modern NLP applications rely heavily on transformer models. Large language models (LLMs) utilize sentiment analysis, part-of-speech tagging, and vector embeddings to achieve state-of-the-art results on benchmark tasks.

2. Retrieval-Augmented Generation
RAG systems combine vector similarity search using FAISS with generative LLMs like Ollama (llama3) to reduce hallucination and provide grounded citations with exact page numbers.
"""
    },
    {
        "filename": "Convolutional_Vision_and_YOLO.pdf",
        "title": "Convolutional Neural Networks and Real-Time Object Detection",
        "content": """
Abstract:
Computer vision systems utilize Convolutional Neural Networks (CNNs), ResNet architectures, object detection using YOLO and Faster R-CNN, image segmentation, optical flow, and visual feature extraction in video streams.

1. Object Detection Benchmarks
Vision transformers (ViT) and semantic segmentation models allow precise pixel-level bounding box object tracking. Depth estimation and visual simultaneous localization and mapping (VSLAM) provide spatial awareness for autonomous systems.

2. Conclusion
Experimental results indicate that deep feature maps significantly increase precision and recall across complex visual scenes.
"""
    },
    {
        "filename": "Cyber_Security_and_Zero_Trust.pdf",
        "title": "Enterprise Cyber Security and Zero-Trust Network Architectures",
        "content": """
Abstract:
Network security, intrusion detection systems (IDS), cryptography, AES encryption, RSA public key infrastructure, zero-trust architecture, and vulnerability assessments form the core of enterprise cybersecurity defense.

1. Threat Mitigation
Malware detection, endpoint detection and response (EDR), ransomware mitigation, and penetration testing ensure safe software development lifecycles.

2. Authentication Protocols
Identity Access Management (IAM), firewalls, and zero-day exploit analysis protect against advanced persistent threats (APT).
"""
    }
]

def create_pdf_bytes(text: str) -> bytes:
    """Creates a minimal valid PDF containing the provided text using PyPDF or standard PDF stream formatting."""
    # Build minimal valid PDF stream directly
    content_stream = f"BT /F1 12 Tf 50 700 Td ({text[:500].replace('(', '[').replace(')', ']')}) Tj ET"
    
    pdf_template = f"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj
4 0 obj <</Length {len(content_stream)}>> stream
{content_stream}
endstream endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000062 00000 n 
0000000117 00000 n 
0000000236 00000 n 
0000000300 00000 n 
trailer <</Size 6 /Root 1 0 R>>
startxref
385
%%EOF"""
    return pdf_template.encode('latin1')

def seed_database():
    init_db()
    db = SessionLocal()
    upload_dir = "./data/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    print("Seeding sample PDF research documents...")

    for paper in SAMPLE_PAPERS:
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{paper['filename']}"
        file_path = os.path.join(upload_dir, safe_filename)

        # Write PDF to disk
        pdf_bytes = create_pdf_bytes(f"{paper['title']}\n\n{paper['content']}")
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        # Save to DB
        doc_entry = DocumentModel(
            id=doc_id,
            filename=paper["filename"],
            file_path=file_path,
            processing_status="PENDING"
        )
        db.add(doc_entry)
        db.commit()

        # Process document (extraction, chunking, classification, FAISS indexing)
        try:
            processed_doc = document_processor.process_pdf(file_path, doc_id, db)
            print(f"Successfully processed: '{processed_doc.filename}' -> Category: {processed_doc.category} ({processed_doc.total_chunks} chunks)")
        except Exception as e:
            print(f"Failed to process '{paper['filename']}': {e}")

    db.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    seed_database()
