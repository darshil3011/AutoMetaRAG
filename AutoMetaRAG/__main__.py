"""
CLI entry point for AutoMetaRAG package.
Enables running via: python -m AutoMetaRAG
"""

import argparse
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .pipeline import AutoMetaRAGPipeline


def main():
    """Main function to run AutoMetaRAG pipeline with CLI arguments."""
    parser = argparse.ArgumentParser(
        description='AutoMetaRAG: Automatic Metadata Generation for RAG Systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run indexing pipeline (auto-loads or generates schema, saves to metadata/ folder)
  AutoMetaRAG --mode ingest
  
  # Run indexing with custom config and data directory
  AutoMetaRAG --mode ingest --config custom.ini --data-dir ./my_data
  
  # Run indexing with custom schema file
  AutoMetaRAG --mode ingest --schema metadata/custom_schema.json
  
  # Run indexing with both custom schema and data directory
  AutoMetaRAG --mode ingest --schema metadata/custom_schema.json --data-dir ./my_data
  
  # Run single query (loads unique_metadata_values.json from metadata/ folder)
  AutoMetaRAG --mode query --query "What is this paper about?"
  
  # Run query with custom score threshold
  AutoMetaRAG --mode query --query "Your question" --score-threshold 0.5
  
  # Run query with specific metadata filters
  AutoMetaRAG --mode query --query "Your question" --search-filter "paper_title,authors"
        '''
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['ingest', 'query'],
        help='Mode to run: "ingest" for indexing documents, "query" for querying (use --query for single query or interactive mode)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.ini',
        help='Path to configuration file (default: config.ini)'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Override data directory from config (for ingest mode)'
    )
    
    parser.add_argument(
        '--schema',
        type=str,
        help='Path to metadata schema JSON file (for ingest mode). If not provided, will load from metadata/metadata_schema.json if it exists, otherwise will generate new schema.'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Query string for query mode (if not provided, enters interactive mode)'
    )
    
    parser.add_argument(
        '--score-threshold',
        type=float,
        default=0.3,
        help='Minimum score threshold for search results (default: 0.3)'
    )
    
    parser.add_argument(
        '--search-filter',
        type=str,
        help='Comma-separated list of metadata fields to use for filtering (e.g., "paper_title,authors"). If not provided, all metadata fields will be used.'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        # print("=" * 80)
        # print("AutoMetaRAG: Automatic Metadata Generation for RAG Systems")
        # print("=" * 80)
        # print(f"Configuration file: {args.config}")
        # print(f"Mode: {args.mode}")
        # print("=" * 80)
        
        pipeline = AutoMetaRAGPipeline(args.config)
        
        # Run based on mode
        if args.mode == 'ingest':
            # Pass schema and data_dir to run_indexing_pipeline
            # If schema is None, it will auto-load from metadata/metadata_schema.json or generate new
            # If data_dir is None, it will use the instance data_directory
            pipeline.run_indexing_pipeline(
                schema=args.schema,
                data_dir=args.data_dir
            )
            
        elif args.mode == 'query':
            # Parse search filter if provided
            search_filter = None
            if args.search_filter:
                # Split by comma and strip whitespace from each field
                search_filter = [field.strip() for field in args.search_filter.split(',')]
            
            # Check if query is provided as argument
            if args.query:
                # Single query mode
                answer = pipeline.query(
                    args.query, 
                    limit=3,
                    score_threshold=args.score_threshold,
                    search_filter=search_filter
                )
                # Print the answer
                print(answer)
            else:
                # Interactive query mode
                print("Interactive query mode. Type 'exit' or 'quit' to end.\n")
                
                while True:
                    try:
                        user_query = input("Enter your query: ").strip()
                        
                        if user_query.lower() in ['exit', 'quit', 'q']:
                            break
                        
                        if not user_query:
                            print("Please enter a valid query.")
                            continue
                        
                        answer = pipeline.query(
                            user_query, 
                            limit=3,
                            score_threshold=args.score_threshold,
                            search_filter=search_filter
                        )
                        # Print the answer
                        print(f"\n{answer}\n")
                        
                    except KeyboardInterrupt:
                        print("\n")
                        break
                    except EOFError:
                        print("\n")
                        break
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: Configuration file not found - {e}")
        print(f"Please ensure '{args.config}' exists in the current directory.")
        sys.exit(1)
    
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease create a .env file with the required environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - QDRANT_URL")
        print("  - QDRANT_API_KEY")
        print("\nOptional environment variables:")
        print("  - QDRANT_COLLECTION (default: AutoMetaRAG)")
        print("  - DATA_DIR (default: ./data)")
        print("\nExample .env file:")
        print('  OPENAI_API_KEY=sk-...')
        print('  QDRANT_URL=https://your-cluster.qdrant.io')
        print('  QDRANT_API_KEY=your-qdrant-key')
        print('\nTip: Copy env.example to .env and fill in your credentials')
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

