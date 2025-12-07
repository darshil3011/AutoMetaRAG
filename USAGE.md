# AutoMetaRAG - Usage Guide

Complete guide for using AutoMetaRAG package for document indexing and querying.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Quick Start](#quick-start)
3. [Using as a Python Package](#using-as-a-python-package)
4. [Using as CLI](#using-as-cli)
5. [Examples](#examples)

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- Qdrant account (cloud or self-hosted)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Package (Optional - for direct command usage)

```bash
# Install in development/editable mode from project root
pip install -e ./AutoMetaRAG
```

Or if you're inside the AutoMetaRAG package directory:
```bash
cd AutoMetaRAG
pip install -e .
```

```bash
AutoMetaRAG --mode query --query "Your question"
```

### Environment Setup

Create a `.env` file in your project root:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Optional
QDRANT_COLLECTION=AutoMetaRAG  # default: AutoMetaRAG
DATA_DIR=./data                # default: ./data
```

### Configuration File

Create a `config.ini` file (required for indexing, optional for querying):

```ini
[Metadata]
probable_questions = "What is attention mechanism?", "How do transformers work?"
document_info = "Research papers on machine learning and neural networks"
```

### Metadata Folder Structure

During indexing, AutoMetaRAG creates a `metadata/` folder with:
- `metadata/metadata_schema.json` - Generated schema (can be modified)
- `metadata/data.json` - Extracted metadata from documents
- `metadata/unique_metadata_values.json` - Pre-computed unique values for querying

---

## Quick Start

### Ingestion (Indexing Documents)

```python
from AutoMetaRAG import AutoMetaRAGPipeline

# Initialize pipeline
pipeline = AutoMetaRAGPipeline('config.ini')

# Step 1: Generate metadata schema
pipeline.get_metadata_schema()

# (Optional: Modify metadata/metadata_schema.json if needed)

# Step 2: Run indexing
pipeline.run_indexing_pipeline(
    schema='metadata/metadata_schema.json',  # or None to auto-load
    data_dir='./data'  # optional override
)
```

### Querying

```python
from AutoMetaRAG import AutoMetaRAGPipeline

# For querying, config.ini is optional - uses environment variables
pipeline = AutoMetaRAGPipeline()  # or AutoMetaRAGPipeline('config.ini')

# Simple query
answer = pipeline.query("What is attention mechanism?")
print(answer)

# Query with filters
answer = pipeline.query(
    user_query="Explain transformer architecture",
    limit=5,
    search_filter=["paper_title", "authors"]
)
```

---

## Using as a Python Package

### AutoMetaRAGPipeline

Main class for orchestrating the workflow.

**Initialization:**
```python
# With config (required for indexing)
pipeline = AutoMetaRAGPipeline('config.ini')

# Without config (for querying only)
pipeline = AutoMetaRAGPipeline()

# With custom data directory
pipeline = AutoMetaRAGPipeline('config.ini', data_dir='./my_documents')
```

**Methods:**

- `get_metadata_schema()` → Generates and saves metadata schema to `metadata/metadata_schema.json`
  - Returns: Path to schema file
  - Requires: `config_path` during initialization

- `run_indexing_pipeline(schema=None, data_dir=None)` → Complete indexing workflow
  - `schema`: Optional path to schema file or dict. If None, auto-loads or generates
  - `data_dir`: Optional override for data directory
  - Creates: `metadata/data.json` and `metadata/unique_metadata_values.json`

- `query(user_query, limit=3, score_threshold=0.3, search_filter=None)` → Execute query
  - `user_query`: Search query string
  - `limit`: Max results (default: 3)
  - `score_threshold`: Min relevance score (default: 0.3)
  - `search_filter`: Optional list of metadata field names to filter by

---

## Using as CLI

### Ingestion

```bash
# Basic ingestion (auto-loads or generates schema, saves to metadata/ folder)
AutoMetaRAG --mode ingest

# With custom config and data directory
AutoMetaRAG --mode ingest --config custom.ini --data-dir ./my_documents

# With custom schema file
AutoMetaRAG --mode ingest --schema metadata/custom_schema.json

# With both custom schema and data directory
AutoMetaRAG --mode ingest --schema metadata/custom_schema.json --data-dir ./my_documents
```

**Note:** During ingestion, all metadata files are saved to the `metadata/` folder:
- `metadata/metadata_schema.json` - Schema (auto-loaded or generated if not provided)
- `metadata/data.json` - Extracted metadata from documents
- `metadata/unique_metadata_values.json` - Pre-computed unique values for querying

### Querying

```bash
# Single query (automatically loads unique_metadata_values.json from metadata/ folder)
AutoMetaRAG --mode query --query "What is attention mechanism?"

# With metadata filter
AutoMetaRAG --mode query --query "Your question" --search-filter "paper_title,authors"

# With custom score threshold
AutoMetaRAG --mode query --query "Your question" --score-threshold 0.5

# Interactive mode
AutoMetaRAG --mode query
```

**Note:** Querying automatically loads `unique_metadata_values.json` from the `metadata/` folder, which was pre-computed during indexing.

## CLI Arguments

### `--mode`
- **Mode:** ingest + query  
- **Required:** Yes  
- **Description:** Must be either `ingest` or `query`.

---

### `--config`
- **Mode:** ingest + query  
- **Optional**  
- **Default:** `config.ini`  
- **Description:** Path to the configuration file.

---

### `--data-dir`
- **Mode:** ingest  
- **Optional**  
- **Default:** `./data`  
- **Description:** Directory containing documents to ingest.

---

### `--schema`
- **Mode:** ingest  
- **Optional**  
- **Default:** none  
- **Description:**  
  - Path to metadata schema JSON file.  
  - If not provided:  
    - Loads `metadata/metadata_schema.json` if available  
    - Otherwise generates a new schema automatically.

---

### `--query`
- **Mode:** query  
- **Optional**  
- **Description:**  
  - Query string to execute.  
  - If absent, tool enters **interactive query mode**.

---

### `--score-threshold`
- **Mode:** query  
- **Optional**  
- **Default:** `0.3`  
- **Description:** Minimum relevance score for search results.

---

### `--search-filter`
- **Mode:** query  
- **Optional**  
- **Description:**  
  - Comma-separated metadata fields to filter search.  
  - Example: `"paper_title,authors"`

---

## Examples

### Example 1: Complete Workflow

```python
from AutoMetaRAG import AutoMetaRAGPipeline

# Initialize
pipeline = AutoMetaRAGPipeline('config.ini')

# Generate schema
pipeline.get_metadata_schema()

# Run indexing
pipeline.run_indexing_pipeline(
    schema='metadata/metadata_schema.json',
    data_dir='./data'
)

# Query
answer = pipeline.query(
    user_query="What is the main contribution of the attention mechanism paper?",
    limit=5,
    search_filter=["paper_title", "authors"]
)
print(answer)
```

### Example 2: Querying Without Config

```python
from AutoMetaRAG import AutoMetaRAGPipeline

# Querying only needs environment variables
pipeline = AutoMetaRAGPipeline()

answer = pipeline.query("What is attention mechanism?")
print(answer)
```

### Example 3: Custom Metadata Schema

```python
from AutoMetaRAG import AutoMetaRAGPipeline

pipeline = AutoMetaRAGPipeline('config.ini')

# Generate schema
pipeline.get_metadata_schema()

# Manually edit metadata/metadata_schema.json, then use it
pipeline.run_indexing_pipeline(
    schema='metadata/metadata_schema.json',
    data_dir='./data'
)
```

### Example 4: Using Schema Dictionary

```python
from AutoMetaRAG import AutoMetaRAGPipeline

pipeline = AutoMetaRAGPipeline('config.ini')

# Define custom schema
custom_schema = {
    "file_level_schema": {"paper_title": "", "authors": ""},
    "chunk_level_schema": {"section_title": "", "section_summary": ""}
}

# Use custom schema
pipeline.run_indexing_pipeline(schema=custom_schema)
```

---

## Troubleshooting

### Common Issues

1. **Environment Variables Not Found**: Ensure `.env` file exists at project root with required keys

2. **Collection Not Found**: Run ingestion mode first to create the collection

3. **Metadata Files Missing**: Run indexing pipeline to create:
   - `metadata/metadata_schema.json`
   - `metadata/data.json`
   - `metadata/unique_metadata_values.json`

4. **Config Required for Schema Generation**: Use `AutoMetaRAGPipeline('config.ini')` when calling `get_metadata_schema()`

### Best Practices

1. Generate metadata schema first and review/modify before indexing
2. Use `search_filter` to narrow results when you have many metadata fields
3. Querying doesn't require `config.ini` - only needs environment variables
4. Unique metadata values are pre-computed during indexing for faster querying

---

## Package Structure

```
project/
├── AutoMetaRAG/          # Package directory
│   ├── __init__.py
│   ├── __main__.py        # CLI entry point
│   ├── pipeline.py        # Main pipeline
│   └── ...
├── metadata/              # Created during indexing
│   ├── metadata_schema.json
│   ├── data.json
│   └── unique_metadata_values.json
├── config.ini             # Configuration (required for indexing)
├── .env                   # Environment variables
└── data/                  # Input documents
```
