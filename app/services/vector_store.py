import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from app.config import settings

class VectorStoreService:
    def __init__(self):
        self.index_dir = settings.FAISS_INDEX_DIR
        self.index_file = os.path.join(self.index_dir, "index.faiss")
        self.meta_file = os.path.join(self.index_dir, "metadata.json")
        self.embedding_model = None
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        
        self._init_embedding_model()
        self._load_or_create_index()

    def _init_embedding_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            print(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}...")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            self.dimension = self.embedding_model.get_sentence_embedding_dimension()
            print(f"Embedding model loaded successfully. Dimension: {self.dimension}")
        except Exception as e:
            print(f"Warning: SentenceTransformer failed to load: {e}. Using TF-IDF/fallback vectorizer.")
            self.embedding_model = None

    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        if self.embedding_model is not None:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return embeddings.astype('float32')
        else:
            from sklearn.feature_extraction.text import HashingVectorizer
            vectorizer = HashingVectorizer(n_features=self.dimension, alternate_sign=False)
            X = vectorizer.transform(texts).toarray()
            norms = np.linalg.norm(X, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return (X / norms).astype('float32')

    def _load_or_create_index(self):
        os.makedirs(self.index_dir, exist_ok=True)
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            try:
                self.index = faiss.read_index(self.index_file)
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                print(f"FAISS index loaded. Total vectors: {self.index.ntotal}")
                return
            except Exception as e:
                print(f"Error reading existing FAISS index: {e}. Recreating index.")

        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self._save_index()

    def _save_index(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_file)
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return

        texts = [c["content"] for c in chunks]
        embeddings = self._generate_embeddings(texts)
        
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)
        self.metadata.extend(chunks)
        self._save_index()

    def search(self, query: str, top_k: int = 5, document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not query or self.index.ntotal == 0:
            return []

        query_emb = self._generate_embeddings([query])
        faiss.normalize_L2(query_emb)

        fetch_k = top_k * 4 if document_ids else top_k
        fetch_k = min(fetch_k, self.index.ntotal)

        distances, indices = self.index.search(query_emb, fetch_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            meta = self.metadata[idx]
            if document_ids and meta.get("document_id") not in document_ids:
                continue

            res_item = dict(meta)
            res_item["score"] = float(dist)
            results.append(res_item)

            if len(results) >= top_k:
                break

        return results

    def delete_document(self, document_id: str):
        if not self.metadata:
            return

        keep_indices = [i for i, meta in enumerate(self.metadata) if meta.get("document_id") != document_id]
        if len(keep_indices) == len(self.metadata):
            return

        new_meta = [self.metadata[i] for i in keep_indices]
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []

        if new_meta:
            self.add_chunks(new_meta)
        else:
            self._save_index()

    def get_total_embeddings(self) -> int:
        return self.index.ntotal if self.index else 0

vector_store_service = VectorStoreService()
