import sys
import os

# Add parent directory to path to allow importing AutoMetaRAG
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from AutoMetaRAG import AutoMetaRAGPipeline

# Initialize pipeline with custom metadata file paths (all optional)
pipeline = AutoMetaRAGPipeline(
    config_path='../sample_data/medical_data/config.ini',
    metadata_schema_file='metadata/metadata_schema.json',  # Optional: custom schema path
    metadata_cache_file='metadata/data.json',  # Optional: custom cache path
    unique_metadata_values_file='metadata/unique_metadata_values.json'  # Optional: custom unique values path
)


schema_path = pipeline.get_metadata_schema(
    schema_output_path='metadata/metadata_schema.json'  # Optional: override default
)

pipeline.run_indexing_pipeline(
    schema='metadata/metadata_schema.json',  # or None to auto-load
    data_dir='../sample_data/medical_data',  # optional override
    schema_file='metadata/metadata_schema.json',  # Optional: custom schema file path
    metadata_cache_file='metadata/data.json',  # Optional: custom cache file path
    unique_metadata_values_file='metadata/unique_metadata_values.json'  # Optional: custom unique values path
)
