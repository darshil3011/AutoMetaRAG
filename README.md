# AutoMetaRAG

Automatic Metadata-based Retrieval Augmented Generation framework for optimized document retrieval using hybrid search (semantic + metadata filtering).

## Features

- **LLM-Powered Metadata Extraction**: Automatically extracts structured metadata from documents
- **Hybrid Search**: Combines semantic similarity search with metadata filtering
- **Qdrant Vector Database**: Efficient vector storage and retrieval
- **Configurable Pipeline**: Easy configuration through environment variables

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables using `.env` file:
```bash
# Copy the example file
cp env.example .env

# Edit .env with your actual credentials
```

Your `.env` file should contain:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Optional
QDRANT_COLLECTION=AutoMetaRAG  # default: AutoMetaRAG
DATA_DIR=./data                # default: ./data
```

3. Configure metadata settings in `config.ini`:
```ini
[Metadata]
probable_questions = "Your example questions"
document_info = "Description of your dataset"
```

## Usage

### 1. Ingestion Pipeline

Process documents, extract metadata, and create vector database:

```bash
python -m AutoMetaRAG --mode ingest
```

Optional arguments:
```bash
python -m AutoMetaRAG --mode ingest --config custom.ini --data-dir ./my_docs
```

**Available CLI Arguments:**

| Argument | Mode | Type | Default | Description |
|----------|------|------|---------|-------------|
| `--mode` | Both | Required | - | `ingest` or `query` |
| `--config` | Both | Optional | `config.ini` | Path to config file |
| `--data-dir` | ingest | Optional | `./data` | Data directory path |
| `--query` | query | Optional | - | Query string (if not provided, enters interactive mode) |
| `--score-threshold` | query | Optional | `0.3` | Minimum relevance score (0.0-1.0) |
| `--vector-name` | query | Optional | `""` | Vector name for multi-vector search |

### 2. Query Pipeline

**Option A: Single query (direct)**
```bash
python -m AutoMetaRAG --mode query --query "What is this paper about?"
```

**With custom score threshold:**
```bash
python -m AutoMetaRAG --mode query --query "Your question" --score-threshold 0.5
```

**With multi-vector approach:**
```bash
python -m AutoMetaRAG --mode query --query "Your question" --vector-name my_vector
```

**Option B: Interactive session**
```bash
python -m AutoMetaRAG --mode query
```
Then enter your questions interactively. Type 'exit' to quit.

**Interactive with custom threshold:**
```bash
python -m AutoMetaRAG --mode query --score-threshold 0.5
```

## Configuration

### Environment Variables (.env file)

AutoMetaRAG uses `python-dotenv` to load environment variables from a `.env` file.

**Required variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_URL`: Qdrant server URL (e.g., https://your-cluster.qdrant.io)
- `QDRANT_API_KEY`: Qdrant API key

**Optional variables:**
- `QDRANT_COLLECTION`: Collection name (default: "AutoMetaRAG")
- `DATA_DIR`: Directory containing documents (default: "./data")

**Setup:**
1. Copy `env.example` to `.env`
2. Fill in your actual credentials
3. The `.env` file is automatically loaded when running AutoMetaRAG

### config.ini File

The `config.ini` file contains metadata configuration for schema generation:

```ini
[Metadata]
probable_questions = "Question 1?", "Question 2?", "Question 3?"
document_info = "Description of your dataset"
```

## Project Structure

```
.
├── AutoMetaRAG/        # Main package directory
│   ├── __init__.py
│   ├── __main__.py     # CLI entry point
│   ├── pipeline.py     # Main pipeline class
│   ├── config.py       # Configuration management
│   ├── metadata.py     # Metadata generation/extraction
│   ├── document.py     # Document processing
│   ├── indexer.py      # Qdrant indexing
│   ├── query.py        # Query engine
│   └── utils.py         # Utility functions
├── examples/           # Example scripts
│   ├── test1.py        # Query example
│   └── test2.py        # Ingestion example
├── requirements.txt    # Python dependencies
├── env.example         # Environment variables template
├── README.md           # This file
└── USAGE.md            # Detailed usage guide
```

## How It Works

1. **Environment Setup**: Loads API keys and configuration from `.env` file using python-dotenv
2. **Metadata Schema Generation**: LLM analyzes your data and suggests metadata schemas
3. **Document Processing**: Documents are loaded and metadata is extracted using LLM
4. **Vector Database Creation**: Documents are embedded and stored in Qdrant with metadata
5. **Query Processing**: User queries are analyzed to extract metadata filters
6. **Hybrid Search**: Uses Qdrant's `query_points` method with:
   - Semantic similarity search
   - Metadata filtering
   - Score threshold filtering (minimum relevance score: 0.3)
   - Multi-vector support (optional)
7. **Response Generation**: LLM generates answers from retrieved context

## Example

```python
from AutoMetaRAG import AutoMetaRAGPipeline

# Initialize pipeline
pipeline = AutoMetaRAGPipeline('config.ini')

# Run ingestion
pipeline.run_indexing_pipeline()

# Query
answer = pipeline.query("What did the paper discuss about transformers?")
print(answer)
```
