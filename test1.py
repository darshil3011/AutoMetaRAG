from AutoMetaRAG import AutoMetaRAGPipeline

pipeline = AutoMetaRAGPipeline()
print("\nQuerying...")
answer = pipeline.query(
    user_query="What are values clarification methods and how are they defined?",
    limit=5,
    search_filter=["document_title"]
)
print(f"\nAnswer: {answer}")