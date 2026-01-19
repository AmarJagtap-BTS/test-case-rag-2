"""
Embedding generation for test cases using Azure OpenAI
"""
import os
import sys
import hashlib
import numpy as np
from typing import List, Dict, Any
from functools import lru_cache

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import AzureOpenAI
from config.config import Config


class EmbeddingGenerator:
    """Generate embeddings for test cases"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        self.cache: Dict[str, List[float]] = {}
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text with caching
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        # Create hash for cache key to handle long texts
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache
        if text_hash in self.cache:
            return self.cache[text_hash]
        
        try:
            response = self.client.embeddings.create(
                input=text[:8000],  # Truncate to avoid token limits
                model=self.deployment
            )
            embedding = response.data[0].embedding
            
            # Cache the result
            self.cache[text_hash] = embedding
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        # Process in batches to avoid rate limits
        batch_size = 16
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Check which texts are not in cache
            uncached_texts = [t for t in batch if t not in self.cache]
            
            if uncached_texts:
                try:
                    response = self.client.embeddings.create(
                        input=uncached_texts,
                        model=self.deployment
                    )
                    
                    # Cache results
                    for j, text in enumerate(uncached_texts):
                        self.cache[text] = response.data[j].embedding
                        
                except Exception as e:
                    print(f"Error generating batch embeddings: {e}")
                    raise
            
            # Get all embeddings (from cache or newly generated)
            batch_embeddings = [self.cache[t] for t in batch]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score between 0 and 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        return (similarity + 1) / 2
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
