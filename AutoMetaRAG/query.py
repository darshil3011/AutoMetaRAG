"""
Query processing for AutoMetaRAG package.
"""

from typing import Dict, List

import openai
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Filter, FieldCondition
from sentence_transformers import SentenceTransformer

from .constants import DEFAULT_EMBEDDING_MODEL, DEFAULT_GPT_MODEL, DEFAULT_TEMPERATURE


class RAGQueryEngine:
    """Handles RAG queries with metadata filtering."""
    
    def __init__(self, qdrant_url: str, api_key: str, collection_name: str,
                 openai_api_key: str, embedding_model: str = DEFAULT_EMBEDDING_MODEL):
        """
        Initialize RAGQueryEngine.
        
        Args:
            qdrant_url: Qdrant instance URL
            api_key: Qdrant API key
            collection_name: Collection name
            openai_api_key: OpenAI API key
            embedding_model: Sentence transformer model name
        """
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        self.collection_name = collection_name
        self.encoder = SentenceTransformer(embedding_model)
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        
        # Verify collection exists
        self._verify_collection_exists()
    
    def _verify_collection_exists(self) -> None:
        """Verify that the collection exists before querying."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                print(f"⚠️  Warning: Collection '{self.collection_name}' does not exist.")
                print(f"Please run ingestion mode first: python -m AutoMetaRAG --mode ingest")
            # else:
            #     print(f"✓ Connected to collection '{self.collection_name}'")
                
        except Exception as e:
            print(f"Warning: Could not verify collection existence: {e}")
    
    def search_with_filter(self, query: str, metadata_filter: Dict, limit: int = 3) -> List:
        """
        Search Qdrant with metadata filtering using query_points method.
        
        Args:
            query: Search query
            metadata_filter: Metadata filter dictionary
            limit: Maximum number of results (default: 3)
            
        Returns:
            List of search hits
        """
        # Build Qdrant filter
        filter_obj = None
        if metadata_filter and len(metadata_filter) > 0:
            key = list(metadata_filter.keys())[0]
            value = list(metadata_filter.values())[0]
            filter_obj = Filter(
                should=[
                    FieldCondition(key=key,
                                match=models.MatchValue(value=value))
                ]
            )
        
        # Encode query and search using query_points
        query_vector = self.encoder.encode(str(query)).tolist()

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=filter_obj,
            with_payload=True
        )
    
        return results.points if hasattr(results, 'points') else results
    
    def generate_answer(self, query: str, hits: List, model: str = DEFAULT_GPT_MODEL) -> str:
        """
        Generate answer using retrieved context and LLM.
        
        Args:
            query: User query
            hits: Search results from Qdrant
            model: GPT model to use
            
        Returns:
            Generated answer
        """
        # Extract context from hits
        context = []
        for hit in hits:
            # print(f"Hit ID: {hit.id}, Score: {hit.score}")
            if 'section_summary' in hit.payload:
                context.append(hit.payload['section_summary'])
                # print(f"Paper: {hit.payload.get('paper_title', 'N/A')}")
                # print(f"Summary: {hit.payload['section_summary']}")
            # print('-------------------------------------')
        
        # Build prompt
        prompt = f'''Based on the provided context information from the dataset, generate a comprehensive answer for the user query.
Context: {context}
User Query: {query}'''
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        # Generate answer
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE
        )
        
        return response.choices[0].message.content

