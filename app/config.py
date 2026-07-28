import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Research & Knowledge Assistant"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    DATABASE_URL: str = "sqlite:///./data/app.db"
    UPLOAD_DIR: str = "./data/uploads"
    FAISS_INDEX_DIR: str = "./data/faiss_index"

    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    TF_MODEL_PATH: str = "./ml/saved_models/tf_classifier.keras"
    TF_VOCAB_PATH: str = "./ml/saved_models/vocab.json"
    TF_LABELS_PATH: str = "./ml/saved_models/labels.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Ensure target directories exist automatically
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.TF_MODEL_PATH), exist_ok=True)

# Derive local database directory path for SQLite
db_path = settings.DATABASE_URL.replace("sqlite:///", "")
if db_path and "/" in db_path:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
