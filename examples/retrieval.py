import sys
import os

# Add parent directory to path to allow importing AutoMetaRAG
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from AutoMetaRAG import AutoMetaRAGPipeline

# Initialize pipeline (can specify custom paths for metadata files)
# If not specified, defaults to metadata/ directory
pipeline = AutoMetaRAGPipeline(
    unique_metadata_values_file='metadata/unique_metadata_values.json'  # Optional: custom path
)

print("\nQuerying...")
answer = pipeline.query(
    user_query="What are values clarification methods and how are they defined?",
    limit=5,
    search_filter=["document_title"],
    unique_metadata_values_file='metadata/unique_metadata_values.json'  # Optional: override per query
)
print(f"\nAnswer: {answer}")