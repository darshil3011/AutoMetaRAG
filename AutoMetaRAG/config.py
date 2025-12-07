"""
Configuration management for AutoMetaRAG package.
"""

import os
from configparser import ConfigParser


class AutoMetaRAGConfig:
    """Configuration manager for AutoMetaRAG system."""
    
    def __init__(self, config_path: str):
        """
        Initialize configuration from INI file and environment variables.
        
        API keys and Qdrant configuration are read from environment variables (.env file).
        Metadata configuration is read from the INI file.
        
        Args:
            config_path: Path to configuration file
            
        Raises:
            FileNotFoundError: If config file does not exist
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        self.config = ConfigParser()
        self.config.read(config_path)
        
    def get_openai_key(self) -> str:
        """Get OpenAI API key from environment variable (.env file)."""
        key = os.getenv('OPENAI_API_KEY', '')
        if not key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
        return key
    
    def get_qdrant_url(self) -> str:
        """Get Qdrant URL from environment variable (.env file)."""
        url = os.getenv('QDRANT_URL', '')
        if not url:
            raise ValueError("QDRANT_URL environment variable is not set. Please check your .env file.")
        return url
    
    def get_qdrant_key(self) -> str:
        """Get Qdrant API key from environment variable (.env file)."""
        key = os.getenv('QDRANT_API_KEY', '')
        if not key:
            raise ValueError("QDRANT_API_KEY environment variable is not set. Please check your .env file.")
        return key
    
    def get_collection_name(self) -> str:
        """Get Qdrant collection name from environment variable or use default."""
        return os.getenv('QDRANT_COLLECTION', 'AutoMetaRAG')
    
    def get_data_directory(self) -> str:
        """Get data directory path from environment variable or use default."""
        return os.getenv('DATA_DIR', './data')
    
    def get_probable_questions(self) -> str:
        """Get probable user questions from config file."""
        return self.config.get('Metadata', 'probable_questions', fallback='')
    
    def get_document_info(self) -> str:
        """Get document information from config file."""
        return self.config.get('Metadata', 'document_info', fallback='')

