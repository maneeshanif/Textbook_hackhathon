#!/usr/bin/env python3
"""
Ingest textbook content into Qdrant vector database.
Usage: python ingest_textbook.py [--language en|ur] [--content-dir /path/to/docs]
"""

import asyncio
import argparse
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.parse_mdx import parse_directory, MDXParser
from app.services.ingestion import ingestion_service
from app.qdrant_client import qdrant_client
from app.gemini_client import gemini_client
from app.config import settings


async def main():
    """Main ingestion script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Ingest textbook content into Qdrant vector database"
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["en", "ur"],
        default="en",
        help="Language of the content (default: en)"
    )
    parser.add_argument(
        "--content-dir",
        type=str,
        help="Path to content directory (default: auto-detect based on language)"
    )
    parser.add_argument(
        "--create-collection",
        action="store_true",
        help="Create Qdrant collection if it doesn't exist"
    )
    
    args = parser.parse_args()
    
    # Determine content directory
    if args.content_dir:
        content_dir = Path(args.content_dir)
    else:
        # Auto-detect based on language
        repo_root = Path(__file__).parent.parent.parent
        if args.language == "en":
            content_dir = repo_root / "book" / "docs"
        else:  # ur
            content_dir = repo_root / "book" / "i18n" / "ur" / "docusaurus-plugin-content-docs" / "current"
    
    # Verify content directory exists
    if not content_dir.exists():
        print(f"❌ Error: Content directory not found: {content_dir}")
        sys.exit(1)
    
    print(f"🚀 Starting ingestion pipeline")
    print(f"   Language: {args.language}")
    print(f"   Content directory: {content_dir}")
    print()
    
    # Initialize clients
    print("🔧 Initializing clients...")
    await qdrant_client.connect()
    gemini_client.connect()
    print("✅ Clients initialized")
    print()
    
    # Create collection if requested
    if args.create_collection:
        print(f"🗂️  Creating Qdrant collection for language: {args.language}")
        try:
            await qdrant_client.create_collection(language=args.language)
            print("✅ Collection created")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
        print()
    
    # Step 1: Parse MDX files
    print("📖 Parsing MDX files...")
    mdx_parser = MDXParser(chunk_size=500, chunk_overlap=50)
    chunks = parse_directory(content_dir, language=args.language, parser=mdx_parser)
    
    if not chunks:
        print("❌ Error: No chunks extracted from content")
        sys.exit(1)
    
    print(f"✅ Extracted {len(chunks)} chunks")
    print()
    
    # Step 2: Generate embeddings and upload
    print("🧠 Generating embeddings and uploading to Qdrant...")
    try:
        await ingestion_service.ingest_content(chunks, language=args.language)
        print("✅ Content ingestion completed successfully")
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        sys.exit(1)
    
    # Cleanup
    await qdrant_client.disconnect()
    gemini_client.disconnect()
    
    print()
    print("🎉 Ingestion pipeline completed!")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Collection: textbook_chunks_{args.language}")


if __name__ == "__main__":
    asyncio.run(main())
