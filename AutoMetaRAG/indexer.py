"""
Vector database indexing for AutoMetaRAG package.
"""

import json
from typing import Dict, List

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer

from .constants import DEFAULT_EMBEDDING_MODEL


class QdrantIndexer:
    """Handles indexing documents into Qdrant vector database."""
    
    def __init__(self, qdrant_url: str, api_key: str, collection_name: str,
                 embedding_model: str = DEFAULT_EMBEDDING_MODEL):
        """
        Initialize QdrantIndexer.
        
        Args:
            qdrant_url: Qdrant instance URL
            api_key: Qdrant API key
            collection_name: Name of the collection
            embedding_model: Sentence transformer model name
        """
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        self.collection_name = collection_name
        self.encoder = SentenceTransformer(embedding_model)
        self.vector_size = 384  # Default size for all-MiniLM-L6-v2
        
        # Create collection if it doesn't exist
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self) -> None:
        """
        Check if collection exists, create it if it doesn't.
        Collection name defaults to 'AutoMetaRAG'.
        """
        from qdrant_client.http import models
        
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                # print(f"Collection '{self.collection_name}' does not exist. Creating it...")
                
                # Create collection with vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                # print(f"✓ Collection '{self.collection_name}' created successfully!")
            else:
                # print(f"✓ Collection '{self.collection_name}' already exists.")
                pass
                
        except Exception as e:
            print(f"Warning: Could not verify/create collection: {e}")
            # print("Proceeding anyway - collection may be created automatically on first insert.")
    
    def create_payload_indexes(self, metadata_dict: Dict[str, str]) -> None:
        """
        Create payload indexes for all metadata fields to enable filtering.
        
        Args:
            metadata_dict: Dictionary of document metadata to extract field names
        """
        from qdrant_client.http import models
        
        try:
            # Extract all unique metadata field names
            field_names = set()
            for metadata_json in metadata_dict.values():
                try:
                    metadata = json.loads(metadata_json)
                    field_names.update(metadata.keys())
                except json.JSONDecodeError:
                    continue
            
            if not field_names:
                # print("No metadata fields found to index.")
                return
            
            # print(f"\nCreating payload indexes for fields: {', '.join(field_names)}")
            
            # Create index for each field
            for field_name in field_names:
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=models.PayloadSchemaType.KEYWORD
                    )
                    # print(f"✓ Created index for field: {field_name}")
                except Exception as e:
                    # Index might already exist or other error
                    # if "already exists" in str(e).lower():
                    #     print(f"  Index for '{field_name}' already exists")
                    # else:
                    #     print(f"  Warning: Could not create index for '{field_name}': {e}")
                    pass
            
            # print("✓ Payload indexes created successfully!\n")
            
        except Exception as e:
            print(f"Warning: Error creating payload indexes: {e}")
            # print("You may need to create indexes manually for filtering to work.")
    
    def index_documents(self, documents: List, metadata_dict: Dict[str, str]) -> int:
        """
        Index documents with metadata into Qdrant.
        Creates payload indexes for all metadata fields to enable filtering.
        
        Args:
            documents: List of documents to index
            metadata_dict: Dictionary mapping document IDs to metadata JSON strings
            
        Returns:
            Number of documents successfully indexed
        """
        points = []
        
        for idx, document in enumerate(documents):
            if document.id_ not in metadata_dict:
                continue
            
            try:
                metadata = json.loads(metadata_dict[document.id_])
                vector = self.encoder.encode(document.text).tolist()
                
                point = PointStruct(
                    id=idx,
                    payload=metadata,
                    vector=vector
                )
                points.append(point)
                
            except Exception as e:
                print(f"Error creating point for document {document.id_}: {e}")
                continue
        
        # Batch upload to Qdrant
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"Successfully ingested {len(points)} documents into Qdrant collection '{self.collection_name}'")
            
            # Create payload indexes for all metadata fields
            self.create_payload_indexes(metadata_dict)
        
        return len(points)

