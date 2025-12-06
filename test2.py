from AutoMetaRAG import AutoMetaRAGPipeline

# Initialize pipeline
pipeline = AutoMetaRAGPipeline('./medical_data/config.ini')

# Step 1: Generate metadata schema
# print("Generating metadata schema...")
# schema_path = pipeline.get_metadata_schema()
# print(f"Schema saved to: {schema_path}")

# (Optional: Modify metadata/metadata_schema.json if needed)
# # Step 2: Run indexing with schema
print("\nStarting ingestion...")
pipeline.run_indexing_pipeline(
    schema='metadata/metadata_schema.json',  # or None to auto-load
    data_dir='./medical_data'  # optional override
)
print("Ingestion complete!")