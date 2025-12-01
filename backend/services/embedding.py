"""Embedding service for converting text to vectors."""
import numpy as np
from typing import List, Optional
from backend.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.use_local = settings.use_local_embeddings
        self.model = None
        
        if self.use_local:
            self._init_local_model()
        else:
            self._init_openai()
    
    def _init_local_model(self):
        """Initialize local sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.embedding_model)
            print(f"Loaded local embedding model: {settings.embedding_model}")
        except Exception as e:
            print(f"Failed to load local embedding model: {e}")
            print("Falling back to OpenAI embeddings")
            self.use_local = False
            self._init_openai()
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
            print("Initialized OpenAI embeddings")
        except Exception as e:
            print(f"Failed to initialize OpenAI: {e}")
            self.client = None
    
    def embed(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            return None
        
        if self.use_local and self.model:
            return self._embed_local(text)
        else:
            return self._embed_openai(text)
    
    def _embed_local(self, text: str) -> List[float]:
        """Generate embedding using local model."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def _embed_openai(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI."""
        if not self.client:
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=384  # Match local model dimension
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.use_local and self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        else:
            return [self.embed(text) for text in texts]


# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

