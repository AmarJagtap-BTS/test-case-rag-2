"""
RAG Engine for test case retrieval using ChromaDB
"""
import os
import sys
import json
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings
from core.models import TestCase
from engines.embeddings import EmbeddingGenerator
from config.config import Config


class RAGEngine:
    """RAG engine for test case storage and retrieval"""
    
    def __init__(self):
        """Initialize ChromaDB and embedding generator"""
        self.embedding_generator = EmbeddingGenerator()
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=Config.CHROMA_COLLECTION_NAME,
            metadata={"description": "Test case knowledge base"}
        )
    
    def add_test_case(self, test_case: TestCase):
        """
        Add a test case to the knowledge base
        
        Args:
            test_case: TestCase to add
        """
        # Convert test case to searchable text
        text = test_case.to_text()
        
        # Generate embedding
        embedding = self.embedding_generator.generate_embedding(text)
        
        # Prepare metadata
        metadata = {
            "id": test_case.id,
            "title": test_case.title,
            "business_rule": test_case.business_rule,
            "priority": test_case.priority,
            "test_type": test_case.test_type,
            "tags": ",".join(test_case.tags),
            "version": test_case.version,
            "created_at": str(test_case.created_at),
            "updated_at": str(test_case.updated_at)
        }
        
        # Add to collection
        self.collection.add(
            ids=[test_case.id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )
    
    def add_test_cases_batch(self, test_cases: List[TestCase]):
        """
        Add multiple test cases to the knowledge base
        
        Args:
            test_cases: List of TestCases to add
        """
        if not test_cases:
            return
        
        # Convert all test cases to text
        texts = [tc.to_text() for tc in test_cases]
        
        # Generate embeddings in batch
        embeddings = self.embedding_generator.generate_embeddings_batch(texts)
        
        # Prepare data
        ids = [tc.id for tc in test_cases]
        metadatas = []
        
        for tc in test_cases:
            metadata = {
                "id": tc.id,
                "title": tc.title,
                "business_rule": tc.business_rule,
                "priority": tc.priority,
                "test_type": tc.test_type,
                "tags": ",".join(tc.tags),
                "version": tc.version,
                "created_at": str(tc.created_at),
                "updated_at": str(tc.updated_at)
            }
            metadatas.append(metadata)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,  # type: ignore
            documents=texts,
            metadatas=metadatas
        )
    
    def search_similar_test_cases(
        self, 
        test_case: TestCase, 
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar test cases
        
        Args:
            test_case: TestCase to search for
            top_k: Number of results to return (defaults to Config.RAG_TOP_K)
            
        Returns:
            List of similar test cases with similarity scores
        """
        # Use config default if not specified
        if top_k is None:
            top_k = Config.RAG_TOP_K
        
        # Check if collection is empty
        collection_count = self.collection.count()
        if collection_count == 0:
            return []  # No test cases in knowledge base yet
        
        # Convert to text and generate embedding
        text = test_case.to_text()
        embedding = self.embedding_generator.generate_embedding(text)
        
        # Query the collection with safe n_results
        n_results = min(top_k, collection_count)
        
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        
        # Format results
        similar_cases = []
        
        if (results['ids'] and len(results['ids'][0]) > 0 and 
            results['documents'] and results['metadatas'] and results['distances']):
            for i in range(len(results['ids'][0])):
                similar_cases.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity": 1 - results['distances'][0][i]  # Convert distance to similarity
                })
        
        return similar_cases
    
    def get_test_case_by_id(self, test_case_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a test case by ID
        
        Args:
            test_case_id: ID of the test case
            
        Returns:
            Test case data or None if not found
        """
        try:
            results = self.collection.get(
                ids=[test_case_id]
            )
            
            if results['ids'] and results['documents'] and results['metadatas']:
                return {
                    "id": results['ids'][0],
                    "document": results['documents'][0],
                    "metadata": results['metadatas'][0]
                }
            return None
            
        except Exception:
            return None
    
    def update_test_case(self, test_case: TestCase):
        """
        Update an existing test case
        
        Args:
            test_case: Updated TestCase
        """
        # Delete old version
        try:
            self.collection.delete(ids=[test_case.id])
        except Exception:
            pass
        
        # Add new version
        self.add_test_case(test_case)
    
    def delete_test_case(self, test_case_id: str):
        """
        Delete a test case from the knowledge base
        
        Args:
            test_case_id: ID of the test case to delete
        """
        self.collection.delete(ids=[test_case_id])
    
    def get_all_test_cases(self) -> List[Dict[str, Any]]:
        """
        Get all test cases from the knowledge base
        
        Returns:
            List of all test cases
        """
        results = self.collection.get()
        
        test_cases = []
        if results['ids'] and results['documents'] and results['metadatas']:
            for i in range(len(results['ids'])):
                test_cases.append({
                    "id": results['ids'][i],
                    "document": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })
        
        return test_cases
    
    def count(self) -> int:
        """Get the number of test cases in the knowledge base"""
        return self.collection.count()
    
    def reset(self):
        """Reset the knowledge base (delete all test cases)"""
        self.client.delete_collection(Config.CHROMA_COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=Config.CHROMA_COLLECTION_NAME,
            metadata={"description": "Test case knowledge base"}
        )
