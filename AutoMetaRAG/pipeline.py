"""
Main pipeline for AutoMetaRAG package.
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Union

from llama_index.core import SimpleDirectoryReader

from .config import AutoMetaRAGConfig
from .constants import (
    METADATA_CACHE_FILE,
    METADATA_DIR,
    METADATA_SCHEMA_FILE,
    UNIQUE_METADATA_VALUES_FILE
)
from .document import DocumentProcessor
from .indexer import QdrantIndexer
from .metadata import MetadataExtractor, MetadataGenerator
from .query import RAGQueryEngine
from .utils import load_json_from_file, save_json_to_file


class AutoMetaRAGPipeline:
    """Main pipeline orchestrating the entire AutoMetaRAG workflow."""
    
    def __init__(self, config_path: Optional[str] = None, data_dir: Optional[str] = None,
                 metadata_schema_file: Optional[str] = None,
                 metadata_cache_file: Optional[str] = None,
                 unique_metadata_values_file: Optional[str] = None):
        """
        Initialize pipeline with configuration.
        
        Args:
            config_path: Optional path to configuration file. If None, uses environment variables only.
                        Required for schema generation and indexing, optional for querying.
            data_dir: Optional data directory path. If None, uses config value or environment variable.
            metadata_schema_file: Optional path to metadata schema JSON file. Default: metadata/metadata_schema.json
            metadata_cache_file: Optional path to metadata cache JSON file. Default: metadata/data.json
            unique_metadata_values_file: Optional path to unique metadata values JSON file. Default: metadata/unique_metadata_values.json
        """
        # Load from config if provided, otherwise use environment variables directly
        if config_path:
            self.config = AutoMetaRAGConfig(config_path)
            self.openai_key = self.config.get_openai_key()
            self.qdrant_url = self.config.get_qdrant_url()
            self.qdrant_key = self.config.get_qdrant_key()
            self.collection_name = self.config.get_collection_name()
            self.data_directory = data_dir if data_dir is not None else self.config.get_data_directory()
        else:
            # Use environment variables directly (for querying without config.ini)
            self.config = None
            self.openai_key = os.getenv('OPENAI_API_KEY', '')
            if not self.openai_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
            
            self.qdrant_url = os.getenv('QDRANT_URL', '')
            if not self.qdrant_url:
                raise ValueError("QDRANT_URL environment variable is not set. Please check your .env file.")
            
            self.qdrant_key = os.getenv('QDRANT_API_KEY', '')
            if not self.qdrant_key:
                raise ValueError("QDRANT_API_KEY environment variable is not set. Please check your .env file.")
            
            self.collection_name = os.getenv('QDRANT_COLLECTION', 'AutoMetaRAG')
            self.data_directory = data_dir if data_dir is not None else os.getenv('DATA_DIR', './data')
        
        # Set metadata file paths (use provided or defaults)
        self.metadata_schema_file = metadata_schema_file or METADATA_SCHEMA_FILE
        self.metadata_cache_file = metadata_cache_file or METADATA_CACHE_FILE
        self.unique_metadata_values_file = unique_metadata_values_file or UNIQUE_METADATA_VALUES_FILE
        
        # Initialize components
        self.metadata_generator = MetadataGenerator(self.openai_key)
        self.document_processor = DocumentProcessor(self.openai_key)
        self.indexer = QdrantIndexer(self.qdrant_url, self.qdrant_key, self.collection_name)
        self.metadata_extractor = MetadataExtractor(self.openai_key)
        self.query_engine = RAGQueryEngine(
            self.qdrant_url, self.qdrant_key, self.collection_name, self.openai_key
        )
    
    def get_metadata_schema(self, schema_output_path: Optional[str] = None) -> str:
        """
        Generate and save metadata schema to file.
        
        Args:
            schema_output_path: Optional path to save the schema file. If None, uses instance metadata_schema_file.
        
        Returns:
            Path to the saved metadata schema file
            
        Raises:
            ValueError: If config_path was not provided during initialization
        """
        if self.config is None:
            raise ValueError("config_path is required for schema generation. Please initialize with AutoMetaRAGPipeline('config.ini')")
        
        # Use provided path or instance default
        schema_file = schema_output_path or self.metadata_schema_file
        
        # print("=" * 80)
        print("GENERATING METADATA SCHEMA")
        # print("=" * 80)
        
        # Generate metadata schema
        document_info = self.config.get_document_info()
        probable_questions = self.config.get_probable_questions()
        
        file_schema, chunk_schema = self.metadata_generator.generate_metadata_schema(
            document_info, probable_questions
        )
        
        # Create directory if it doesn't exist
        schema_dir = os.path.dirname(schema_file)
        if schema_dir:
            os.makedirs(schema_dir, exist_ok=True)
        
        # Save schema to file
        try:
            if isinstance(file_schema, str):
                file_schema_parsed = json.loads(file_schema)
            else:
                file_schema_parsed = file_schema
        except json.JSONDecodeError as e:
            raise ValueError(f"Generated file_schema is not valid JSON: {e}")
        
        try:
            if isinstance(chunk_schema, str):
                chunk_schema_parsed = json.loads(chunk_schema) if chunk_schema else {}
            else:
                chunk_schema_parsed = chunk_schema if chunk_schema else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Generated chunk_schema is not valid JSON: {e}")
        
        schema_dict = {
            "file_level_schema": file_schema_parsed,
            "chunk_level_schema": chunk_schema_parsed
        }
        
        save_json_to_file(schema_dict, schema_file)
        # print(f"\nMetadata schema saved to {schema_file}")
        # print("You can modify this file before running indexing pipeline.")
        
        return schema_file
    
    def run_indexing_pipeline(self, schema: Optional[Union[str, Dict]] = None, 
                             data_dir: Optional[str] = None,
                             schema_file: Optional[str] = None,
                             metadata_cache_file: Optional[str] = None,
                             unique_metadata_values_file: Optional[str] = None) -> None:
        """
        Run the complete document indexing pipeline.
        
        Args:
            schema: Optional path to metadata schema JSON file or schema dictionary.
                   If None, will load from schema_file (or instance default) if it exists,
                   otherwise will generate new schema.
            data_dir: Optional data directory path to override. If None, uses instance data_directory.
            schema_file: Optional path to metadata schema file. If None, uses instance metadata_schema_file.
            metadata_cache_file: Optional path to save metadata cache. If None, uses instance metadata_cache_file.
            unique_metadata_values_file: Optional path to save unique metadata values. If None, uses instance unique_metadata_values_file.
        """
        # Override data directory if provided
        if data_dir is not None:
            self.data_directory = data_dir
            # print(f"Using data directory: {self.data_directory}")
        
        # Use provided paths or instance defaults
        schema_file_path = schema_file or self.metadata_schema_file
        cache_file_path = metadata_cache_file or self.metadata_cache_file
        unique_values_file_path = unique_metadata_values_file or self.unique_metadata_values_file
        
        # print("=" * 80)
        print("STEP 1: Loading Metadata Schema")
        # print("=" * 80)
        
        # Load or generate schema
        if schema is not None:
            if isinstance(schema, str):
                # Load from file
                schema_data = load_json_from_file(schema)
                if not schema_data:
                    raise ValueError(f"Could not load schema from {schema}")
                file_schema = json.dumps(schema_data.get("file_level_schema", {}))
                chunk_schema = json.dumps(schema_data.get("chunk_level_schema", {}))
                # print(f"Loaded schema from: {schema}")
            elif isinstance(schema, dict):
                # Use provided dictionary
                file_schema = json.dumps(schema.get("file_level_schema", {}))
                chunk_schema = json.dumps(schema.get("chunk_level_schema", {}))
                # print("Using provided schema dictionary")
            else:
                raise ValueError("Schema must be a file path (str) or dictionary")
        else:
            # Try to load existing schema file, otherwise generate new
            if os.path.exists(schema_file_path):
                schema_data = load_json_from_file(schema_file_path)
                if schema_data:
                    file_schema = json.dumps(schema_data.get("file_level_schema", {}))
                    chunk_schema = json.dumps(schema_data.get("chunk_level_schema", {}))
                    # print(f"Loaded existing schema from: {schema_file_path}")
                else:
                    # Generate new schema (requires config)
                    if self.config is None:
                        raise ValueError("config_path is required for schema generation. Please initialize with AutoMetaRAGPipeline('config.ini') or provide schema parameter")
                    # print("Existing schema file not valid, generating new schema...")
                    document_info = self.config.get_document_info()
                    probable_questions = self.config.get_probable_questions()
                    file_schema, chunk_schema = self.metadata_generator.generate_metadata_schema(
                        document_info, probable_questions
                    )
            else:
                # Generate new schema (requires config)
                if self.config is None:
                    raise ValueError("config_path is required for schema generation. Please initialize with AutoMetaRAGPipeline('config.ini') or provide schema parameter")
                # print("No existing schema found, generating new schema...")
                document_info = self.config.get_document_info()
                probable_questions = self.config.get_probable_questions()
                file_schema, chunk_schema = self.metadata_generator.generate_metadata_schema(
                    document_info, probable_questions
                )
        
        # print("\n" + "=" * 80)
        print("STEP 2: Loading Documents")
        # print("=" * 80)
        
        # Load documents
        documents = SimpleDirectoryReader(
            self.data_directory, filename_as_id=True
        ).load_data()
        print(f"Loaded {len(documents)} documents")
        
        # print("\n" + "=" * 80)
        print("STEP 3: Processing Documents and Extracting Metadata")
        # print("=" * 80)
        
        # Process documents
        json_formats = (file_schema, chunk_schema)
        extracted_metadata = self.document_processor.process_documents(documents, json_formats)
        
        # Create directory for cache file if it doesn't exist
        cache_dir = os.path.dirname(cache_file_path)
        if cache_dir:
            os.makedirs(cache_dir, exist_ok=True)
        
        # Save metadata cache
        save_json_to_file(extracted_metadata, cache_file_path)
        
        # print("\n" + "=" * 80)
        print("STEP 4: Generating Unique Metadata Values")
        # print("=" * 80)
        
        # Generate unique metadata values
        unique_metadata = self.metadata_extractor.extract_unique_metadata_values(extracted_metadata)
        print(f"Generated unique metadata values for {len(unique_metadata)} fields")
        
        # Create directory for unique values file if it doesn't exist
        unique_values_dir = os.path.dirname(unique_values_file_path)
        if unique_values_dir:
            os.makedirs(unique_values_dir, exist_ok=True)
        
        # Save unique metadata values
        save_json_to_file(unique_metadata, unique_values_file_path)
        # print(f"Unique metadata values saved to {unique_values_file_path}")
        
        # print("\n" + "=" * 80)
        print("STEP 5: Indexing Documents in Qdrant")
        # print("=" * 80)
        
        # Index documents
        num_indexed = self.indexer.index_documents(documents, extracted_metadata)
        print(f"Indexing complete: {num_indexed} documents indexed")
    
    def query(self, user_query: str, limit: int = 3, score_threshold: float = 0.3,
              search_filter: Optional[List[str]] = None,
              unique_metadata_values_file: Optional[str] = None) -> str:
        """
        Execute a query against the indexed documents.
        
        Args:
            user_query: User's search query
            limit: Maximum number of results to retrieve (default: 3)
            score_threshold: Minimum score threshold for results (default: 0.3)
            search_filter: Optional list of metadata field names to use for filtering
            unique_metadata_values_file: Optional path to unique metadata values file. If None, uses instance unique_metadata_values_file.
            
        Returns:
            Generated answer
        """
        # Use provided path or instance default
        unique_values_file = unique_metadata_values_file or self.unique_metadata_values_file
        
        # print("=" * 80)
        # print("QUERY PROCESSING")
        # print("=" * 80)
        # print(f"Query: {user_query}\n")
        # Load unique metadata values from pre-computed file
        unique_metadata = load_json_from_file(unique_values_file)
        if not unique_metadata:
            print("Error: Unique metadata values file not found. Please run indexing pipeline first.")
            return ""
        
        # Apply search filter if provided
        if search_filter:
            # print(f"Search Filter Fields: {', '.join(search_filter)}\n")
            filtered_metadata = {
                key: value for key, value in unique_metadata.items()
                if key in search_filter
            }
            unique_metadata = filtered_metadata
        
        # print(f"Unique Metadata Values:\n{json.dumps(unique_metadata, indent=2)}\n")
        
        # Filter metadata based on query
        metadata_filter = self.metadata_extractor.filter_metadata_by_query(
            unique_metadata, user_query
        )
        # print(f"Applied Metadata Filter: {metadata_filter}\n")
        
        # Search with filter using query_points
        hits = self.query_engine.search_with_filter(
            user_query, 
            metadata_filter, 
            limit=limit
        )
        # print(f"Hits: {hits}\n")
        
        # Generate answer
        answer = self.query_engine.generate_answer(user_query, hits)
        # print("\n" + "=" * 80)
        # print("ANSWER:")
        # print("=" * 80)
        # print(answer)
        
        return answer

