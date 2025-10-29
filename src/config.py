"""
Configuration for RAG system
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "gpt-3.5-turbo"
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Retrieval Settings
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 10
    TOP_K_RERANK: int = 5

    # Hybrid Search Weights
    DENSE_WEIGHT: float = 0.7
    SPARSE_WEIGHT: float = 0.3

    # Vector Store
    VECTOR_STORE_TYPE: str = "chroma"  # chroma or faiss
    VECTOR_STORE_PATH: str = "data/processed/vector_store"

    # Processing
    BATCH_SIZE: int = 32
    MAX_CONTEXT_LENGTH: int = 4096

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
