"""
Document processing for AutoMetaRAG package.
"""

import json
import re
from typing import Dict, List, Tuple

import openai

from .constants import DEFAULT_GPT_MODEL, DEFAULT_TEMPERATURE


class DocumentProcessor:
    """Processes documents and extracts metadata using LLM."""
    
    def __init__(self, openai_api_key: str, model: str = DEFAULT_GPT_MODEL):
        """
        Initialize DocumentProcessor.
        
        Args:
            openai_api_key: OpenAI API key
            model: GPT model to use for extraction
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
    
    def process_documents(self, documents: List, json_formats: Tuple[str, str]) -> Dict[str, str]:
        """
        Process documents and extract metadata based on provided JSON schemas.
        
        Args:
            documents: List of LlamaIndex Document objects
            json_formats: Tuple of (file-level schema, chunk-level schema)
            
        Returns:
            Dictionary mapping document IDs to extracted metadata JSON strings
        """
        results = {}
        previous_file_name = None
        last_json1 = None
        
        for doc in documents:
            try:
                # Determine which metadata to extract based on file continuity
                if doc.metadata.get('file_name') == previous_file_name:
                    json_to_extract = json_formats[1]  # Chunk-level only
                else:
                    json_to_extract = f"{json_formats[0]}\n\n{json_formats[1]}"  # Both
                
                # Extract metadata from document
                extracted_metadata = self._extract_metadata_from_document(doc.text, json_to_extract)
                
                # Merge with file-level metadata if needed
                if doc.metadata.get('file_name') == previous_file_name and last_json1:
                    merged_json = {**json.loads(last_json1), **extracted_metadata}
                else:
                    last_json1 = json.dumps(extracted_metadata)
                    merged_json = extracted_metadata
                
                results[doc.id_] = json.dumps(merged_json)
                # print(f"Processed document {doc.id_}: {merged_json}")
                
                previous_file_name = doc.metadata.get('file_name')
                
            except Exception as e:
                print(f"Error processing document {doc.id_}: {e}")
                continue
        
        return results
    
    def _extract_metadata_from_document(self, text: str, json_schema: str) -> Dict:
        """
        Extract metadata from document text using LLM.
        
        Args:
            text: Document text
            json_schema: JSON schema to extract
            
        Returns:
            Extracted metadata dictionary
        """
        prompt = f"Extract the following JSON structures from the text. Don't respond with anything extra. Just the json / jsons given: {json_schema}\n\nText:\n{text}"
        
        messages = [
            {"role": "system", "content": "You are an expert JSON extractor and data analyst."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=DEFAULT_TEMPERATURE
        )
        
        # Extract JSON from response
        json_pattern = r'\{.*?\}'
        matches = re.findall(json_pattern, response.choices[0].message.content)
        
        if matches:
            return json.loads(matches[0])
        else:
            raise ValueError("No valid JSON found in LLM response")

