"""
AutoMetaRAG: Automatic Metadata Generation for RAG Systems

This package provides functionality to automatically generate metadata for documents,
index them in a vector database (Qdrant), and perform intelligent retrieval with
metadata filtering.
"""

from dotenv import load_dotenv

# Load environment variables from .env file
# This ensures .env is loaded when the package is imported
load_dotenv()

__version__ = "1.0.0"

# Import all public classes and functions
from .config import AutoMetaRAGConfig
from .constants import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_GPT_MODEL,
    DEFAULT_TEMPERATURE,
    METADATA_CACHE_FILE
)
from .document import DocumentProcessor
from .indexer import QdrantIndexer
from .metadata import MetadataExtractor, MetadataGenerator
from .pipeline import AutoMetaRAGPipeline
from .query import RAGQueryEngine
from .utils import extract_json, load_json_from_file, save_json_to_file

# Define public API
__all__ = [
    # Main pipeline
    'AutoMetaRAGPipeline',
    
    # Configuration
    'AutoMetaRAGConfig',
    
    # Core components
    'MetadataGenerator',
    'MetadataExtractor',
    'DocumentProcessor',
    'QdrantIndexer',
    'RAGQueryEngine',
    
    # Utilities
    'extract_json',
    'save_json_to_file',
    'load_json_from_file',
    
    # Constants
    'DEFAULT_EMBEDDING_MODEL',
    'DEFAULT_GPT_MODEL',
    'DEFAULT_TEMPERATURE',
    'METADATA_CACHE_FILE',
    
    # Version
    '__version__',
]

