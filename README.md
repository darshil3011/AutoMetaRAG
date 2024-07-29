# AutoMetaRAG

![Diagram]([https://github.com/darshil3011/AutoMetaRAG/blob/main/autometaRAG.png])

This repository presents a Automatic Metadata based Retriever-Augmented Generator (AutoMeta RAG) framework designed to optimize the retrieval of data chunks from a large dataset by leveraging dynamic metadata schemas. The framework initiates by analyzing the dataset and anticipated user queries to suggest two types of metadata schemas: file-level and chunk-level. File-level metadata remains constant across all data chunks within a single file, providing a macro-view of the data attributes. Conversely, chunk-level metadata is unique for each data chunk, allowing for fine-grained indexing and retrieval.

Following the schema suggestion, the framework automates the extraction of metadata for each data chunk according to the defined schemas and stores these, along with the data vectors, into the VectorDB Qdrant. This storage method enhances the efficiency and accuracy of data retrieval processes.

On the inference side, the framework extracts metadata from incoming user queries based on the pre-determined schemas. It utilizes this metadata to perform targeted searches within the vector database, ensuring that the retrieved data chunks are the most relevant to the user's request. This method significantly improves the precision and speed of data retrieval, making it particularly useful for applications requiring rapid access to specific data segments within a large dataset
