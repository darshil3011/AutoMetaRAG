"""
Metadata generation and extraction for AutoMetaRAG package.
"""

import json
import re
from typing import Dict, List, Tuple, Optional

import openai

from .constants import DEFAULT_GPT_MODEL, DEFAULT_TEMPERATURE
from .utils import extract_json


class MetadataGenerator:
    """Generates metadata schemas using LLM based on dataset characteristics."""
    
    def __init__(self, openai_api_key: str, model: str = DEFAULT_GPT_MODEL):
        """
        Initialize MetadataGenerator.
        
        Args:
            openai_api_key: OpenAI API key
            model: GPT model to use
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
    
    def generate_metadata_schema(self, document_info: str, probable_questions: str) -> Tuple[str, str]:
        """
        Generate metadata schema based on document characteristics and expected queries.
        
        Args:
            document_info: Description of the dataset
            probable_questions: Example questions users might ask
            
        Returns:
            Tuple of two JSON schema strings (file-level, chunk-level)
        """
        prompt = self._build_schema_generation_prompt(document_info, probable_questions)
        
        messages = [
            {"role": "system", "content": "You are an expert LLM Engineer and Consultant."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=DEFAULT_TEMPERATURE
            )
            
            metadata_suggestion = response.choices[0].message.content
            # print("Metadata Schema Suggestion:")
            # print(metadata_suggestion)
            
            extracted_json = extract_json(metadata_suggestion)
            if len(extracted_json) >= 2:
                return json.dumps(extracted_json[0]), json.dumps(extracted_json[1])
            else:
                # print("Warning: Could not extract two JSON schemas. Using raw response.")
                return metadata_suggestion, ""
                
        except Exception as e:
            print(f"Error generating metadata schema: {e}")
            return "{}", "{}"
    
    def _build_schema_generation_prompt(self, document_info: str, probable_questions: str) -> str:
        """Build the prompt for metadata schema generation."""
        return f'''I am indexing a large dataset for better retrieval. I want to break the data into chunks and index the chunks of data and store metadata of each chunk for better and accurate retrieval.

I will give you information about my dataset and list of probable questions that user may ask. It's not exact questions but just a set of examples. Analyse the data and type of probable questions and give me two lists of metadata that I should extract from each chunk of data for better retrieval.

One list will have metadata that can be extracted from first chunk such as file name, library name, date of file creation etc. Understand that this metadata will remain same for chunks within same file but will change when we index another file.

Another list will have metadata that are specific to that chunk of data like keywords, details or something specific depending upon dataset. But it should be metadata version of entire data chunk.

Your response should only contain two jsons of metadata to be extracted.

For example:

Dataset information: Documentation of python libraries like OpenCV and many others
List of probable questions: What is the use of cv2.imshow, How to install opencv-python, What are the keyword arguments for cv2.imread, how to use np.array ?

Analysis: since there are many libraries, one json will have library name, library version and last updated date. Since these data can be extracted from first chunk of each file. Another json will be specific to the data inside each library documentation so it should have function name and function utility summary.

Your response: {{"library_name":"", "library_version":"", "last_updated_date":""}}, {{"function_name": "", "function_utility_summary":""}}

<example over>

Dataset information: {document_info}
Probable questions: {probable_questions}'''


class MetadataExtractor:
    """Extracts relevant metadata values from master data based on user queries."""
    
    def __init__(self, openai_api_key: str, model: str = DEFAULT_GPT_MODEL):
        """
        Initialize MetadataExtractor.
        
        Args:
            openai_api_key: OpenAI API key
            model: GPT model to use
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
    
    def extract_unique_metadata_values(self, metadata_dict: Dict[str, str], 
                                      filter_fields: Optional[List[str]] = None) -> Dict[str, List]:
        """
        Extract all unique values for each metadata key across documents.
        
        Args:
            metadata_dict: Dictionary of document metadata
            filter_fields: Optional list of metadata fields to include. If None, includes all fields.
            
        Returns:
            Dictionary mapping metadata keys to lists of unique values
        """
        unique_values = {}
        
        for document_metadata in metadata_dict.values():
            try:
                nested_data = json.loads(document_metadata)
                
                for key, value in nested_data.items():
                    # Skip this field if filter_fields is specified and key is not in the list
                    if filter_fields is not None and key not in filter_fields:
                        continue
                    
                    if key not in unique_values:
                        unique_values[key] = set()
                    unique_values[key].add(value)
                    
            except json.JSONDecodeError as e:
                # print(f"Error parsing metadata: {e}")
                continue
        
        # Convert sets to lists for JSON serialization
        return {key: list(values) for key, values in unique_values.items()}
    
    def filter_metadata_by_query(self, unique_values_json: Dict, user_query: str) -> Dict:
        """
        Use LLM to identify relevant metadata filters based on user query.
        
        Args:
            unique_values_json: Dictionary of metadata keys and their unique values
            user_query: User's search query
            
        Returns:
            Filtered metadata dictionary for database query
        """
        prompt = self._build_filter_prompt(unique_values_json, user_query)
        
        messages = [
            {"role": "system", "content": "You are an expert JSON extractor and data analyst designed to output JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=DEFAULT_TEMPERATURE
            )
            
            response_content = response.choices[0].message.content
            # print(f"Metadata Filter Response: {response_content}")
            
            # Extract JSON from response
            json_pattern = r'\{.*?\}'
            matches = re.findall(json_pattern, response_content, re.DOTALL)
            
            if matches:
                return json.loads(matches[0])
            else:
                return {}
                
        except Exception as e:
            print(f"Error filtering metadata: {e}")
            return {}
    
    def _build_filter_prompt(self, unique_values_json: Dict, user_query: str) -> str:
        """Build prompt for metadata filtering."""
        return f'''You will be given a query and master data JSON. The query is to be used for performing hybrid search on a vector database.
Your job is to analyse the query and respond with key-value pairs that you can find out from the master data JSON. Don't focus on answering the query. Just find out which key-value pairs matches the master data.

For example: Master json is {{'price': ['0$-100$', '100$-500$', '500$-1000$', '1000$+'], 'product_category': ['clothes, accessories', 'mobiles, laptops', 'grocery, essentials']}}

Query is "What are some good options for Mens black Tshirt"

Your response should be {{'product_category': 'clothes, accessories'}}

Here is the master data json: {json.dumps(unique_values_json)}
User Query: {user_query}
Your response: '''

