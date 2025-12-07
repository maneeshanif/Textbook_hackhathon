"""
MDX parser for textbook content ingestion.
Extracts text content, excludes code blocks, and chunks for vector embedding.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
import tiktoken


class MDXParser:
    """Parser for MDX textbook files."""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base"
    ):
        """
        Initialize MDX parser.
        
        Args:
            chunk_size: Target size for each chunk in tokens
            chunk_overlap: Number of tokens to overlap between chunks
            encoding_name: Tokenizer encoding name
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def parse_file(self, file_path: Path, language: str = "en") -> List[Dict[str, Any]]:
        """
        Parse an MDX file and extract metadata and content.
        
        Args:
            file_path: Path to MDX file
            language: Language code ('en' or 'ur')
        
        Returns:
            List of chunks with metadata
        """
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter metadata
        metadata = self._extract_frontmatter(content)
        
        # Remove frontmatter
        content = self._remove_frontmatter(content)
        
        # Remove code blocks (per spec: exclude from embeddings)
        content = self._remove_code_blocks(content)
        
        # Remove MDX/JSX components
        content = self._remove_jsx_components(content)
        
        # Clean up markdown formatting
        content = self._clean_markdown(content)
        
        # Extract chapter ID from file path
        chapter_id = self._extract_chapter_id(file_path)
        
        # Chunk the content
        chunks = self._chunk_text(content)
        
        # Build chunk metadata
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk_meta = {
                "text": chunk_text,
                "metadata": {
                    "chapter_id": chapter_id,
                    "chapter_title": metadata.get("title", ""),
                    "chunk_index": i,
                    "file_path": str(file_path),
                    "language": language
                }
            }
            result.append(chunk_meta)
        
        return result
    
    def _extract_frontmatter(self, content: str) -> Dict[str, str]:
        """Extract YAML frontmatter from MDX content."""
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        
        if not frontmatter_match:
            return {}
        
        frontmatter = frontmatter_match.group(1)
        metadata = {}
        
        # Simple YAML parsing (title and sidebar_label)
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
    
    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from MDX content."""
        return re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
    
    def _remove_code_blocks(self, content: str) -> str:
        """Remove code blocks from content (triple backticks)."""
        # Remove fenced code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        
        # Remove inline code
        content = re.sub(r'`[^`]+`', '', content)
        
        return content
    
    def _remove_jsx_components(self, content: str) -> str:
        """Remove JSX/MDX components from content."""
        # Remove import statements
        content = re.sub(r'^import\s+.*?;?\n', '', content, flags=re.MULTILINE)
        
        # Remove self-closing tags like <ComponentName />
        content = re.sub(r'<\w+[^>]*?/>', '', content)
        
        # Remove paired tags like <ComponentName>...</ComponentName>
        content = re.sub(r'<\w+[^>]*?>.*?</\w+>', '', content, flags=re.DOTALL)
        
        return content
    
    def _clean_markdown(self, content: str) -> str:
        """Clean up markdown formatting for better embedding quality."""
        # Remove markdown links but keep link text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # Remove bold/italic markers
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)
        
        # Remove heading markers
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        
        # Remove list markers
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s+', '', content, flags=re.MULTILINE)
        
        # Normalize whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        return content.strip()
    
    def _extract_chapter_id(self, file_path: Path) -> str:
        """
        Extract chapter ID from file path.
        
        Example: docs/module-1/week-1-2/1.1-introduction.mdx -> "1.1"
        """
        # Try to extract from filename
        filename = file_path.stem
        
        # Look for pattern like "1.1" or "2.3.4"
        match = re.search(r'(\d+\.[\d.]+)', filename)
        if match:
            return match.group(1)
        
        # Fallback to parent directory structure
        parts = file_path.parts
        for part in parts:
            match = re.search(r'(\d+\.[\d.]+)', part)
            if match:
                return match.group(1)
        
        # Last resort: use filename
        return filename
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into overlapping segments of target token size.
        
        Args:
            text: Text to chunk
        
        Returns:
            List of text chunks
        """
        # Tokenize the text
        tokens = self.encoding.encode(text)
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(tokens):
            # Get chunk of tokens
            end_idx = start_idx + self.chunk_size
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Only add non-empty chunks
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
            
            # Move to next chunk with overlap
            start_idx += self.chunk_size - self.chunk_overlap
        
        return chunks


def parse_directory(
    directory: Path,
    language: str = "en",
    parser: MDXParser | None = None
) -> List[Dict[str, Any]]:
    """
    Parse all MDX files in a directory recursively.
    
    Args:
        directory: Root directory to parse
        language: Language code ('en' or 'ur')
        parser: Optional parser instance (creates new one if None)
    
    Returns:
        List of all chunks from all files with metadata
    """
    if parser is None:
        parser = MDXParser()
    
    all_chunks = []
    
    # Find all .mdx files recursively
    mdx_files = list(directory.rglob("*.mdx"))
    
    print(f"Found {len(mdx_files)} MDX files in {directory}")
    
    for mdx_file in mdx_files:
        print(f"Parsing {mdx_file}...")
        try:
            chunks = parser.parse_file(mdx_file, language=language)
            all_chunks.extend(chunks)
            print(f"  -> Extracted {len(chunks)} chunks")
        except Exception as e:
            print(f"  -> Error: {e}")
    
    print(f"\nTotal chunks extracted: {len(all_chunks)}")
    return all_chunks
