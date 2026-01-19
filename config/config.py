"""
Configuration management for RAG-based test case system
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the application"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "https://bts-poc-openai.openai.azure.com")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1-mini")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    
    # Vector Database Configuration
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Similarity Thresholds
    THRESHOLD_SAME: float = float(os.getenv("THRESHOLD_SAME", "0.85"))
    THRESHOLD_ADDON_MIN: float = float(os.getenv("THRESHOLD_ADDON_MIN", "0.60"))
    THRESHOLD_ADDON_MAX: float = float(os.getenv("THRESHOLD_ADDON_MAX", "0.85"))
    
    # Hybrid Scoring Weights (Semantic + LLM)
    # Semantic weight: Embedding-based similarity (fast, reliable for exact matches)
    # LLM weight: Context-based similarity (catches semantic equivalence)
    SEMANTIC_WEIGHT: float = float(os.getenv("SEMANTIC_WEIGHT", "0.60"))  # 60%
    LLM_WEIGHT: float = float(os.getenv("LLM_WEIGHT", "0.40"))  # 40%
    
    # RAG Configuration
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "10"))  # Number of similar cases to retrieve
    
    # Test Case Generation Configuration
    USE_PARALLEL_GENERATION: bool = os.getenv("USE_PARALLEL_GENERATION", "false").lower() == "true"
    PARALLEL_BATCH_SIZE: int = 15  # Number of parallel batches
    BATCH_TIMEOUT_SECONDS: int = 60  # Timeout per batch
    
    # Test Case Generation Limits
    MIN_TEST_CASES: int = int(os.getenv("MIN_TEST_CASES", "8"))
    MAX_TEST_CASES: int = int(os.getenv("MAX_TEST_CASES", "25"))
    DEFAULT_TEST_CASES: int = int(os.getenv("DEFAULT_TEST_CASES", "12"))
    
    # Test Case Type Distribution (as percentages 0.0-1.0)
    POSITIVE_MIN_PERCENT: float = float(os.getenv("POSITIVE_MIN_PERCENT", "0.20"))
    POSITIVE_MAX_PERCENT: float = float(os.getenv("POSITIVE_MAX_PERCENT", "0.30"))
    
    NEGATIVE_MIN_PERCENT: float = float(os.getenv("NEGATIVE_MIN_PERCENT", "0.30"))
    NEGATIVE_MAX_PERCENT: float = float(os.getenv("NEGATIVE_MAX_PERCENT", "0.40"))
    
    UI_MIN_PERCENT: float = float(os.getenv("UI_MIN_PERCENT", "0.20"))
    UI_MAX_PERCENT: float = float(os.getenv("UI_MAX_PERCENT", "0.30"))
    
    SECURITY_MIN_PERCENT: float = float(os.getenv("SECURITY_MIN_PERCENT", "0.10"))
    SECURITY_MAX_PERCENT: float = float(os.getenv("SECURITY_MAX_PERCENT", "0.20"))
    
    EDGE_CASE_MIN_PERCENT: float = float(os.getenv("EDGE_CASE_MIN_PERCENT", "0.10"))
    EDGE_CASE_MAX_PERCENT: float = float(os.getenv("EDGE_CASE_MAX_PERCENT", "0.20"))
    
    # Storage Paths
    KNOWLEDGE_BASE_PATH: str = os.getenv("KNOWLEDGE_BASE_PATH", "./knowledge_base")
    TEST_SUITE_OUTPUT: str = os.getenv("TEST_SUITE_OUTPUT", "./output")
    
    # Collection Names
    CHROMA_COLLECTION_NAME: str = "test_cases"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required = [
            cls.AZURE_OPENAI_API_KEY,
            cls.AZURE_OPENAI_ENDPOINT,
        ]
        return all(required)
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        os.makedirs(cls.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        os.makedirs(cls.KNOWLEDGE_BASE_PATH, exist_ok=True)
        os.makedirs(cls.TEST_SUITE_OUTPUT, exist_ok=True)


# Initialize directories on import
Config.create_directories()
