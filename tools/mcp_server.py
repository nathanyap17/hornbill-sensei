"""
MCP Server for Sarawak Tourism & Culture Synth
Provides RAG search capabilities via FastMCP.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.rag_pipeline import RAGPipeline, initialize_pipeline

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("Sarawak Tourism RAG Server")

# Global pipeline instance
_pipeline: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    """Get or initialize the RAG pipeline."""
    global _pipeline
    if _pipeline is None:
        data_dir = os.getenv("DATA_DIR", "data")
        _pipeline = initialize_pipeline(data_dir=data_dir)
    return _pipeline


@mcp.tool()
def search_sarawak_documents(query: str, num_results: int = 5) -> str:
    """
    Search Sarawak tourism documents for relevant information.
    
    Args:
        query: The search query about Sarawak tourism, culture, or attractions
        num_results: Number of results to return (default: 5)
    
    Returns:
        Formatted string with relevant document excerpts
    """
    try:
        pipeline = get_pipeline()
        results = pipeline.search_documents(query, k=num_results)
        
        if not results:
            return "No relevant information found in the Sarawak tourism documents."
        
        formatted = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source_file', 'Unknown')
            page = result['metadata'].get('page', 'N/A')
            score = result['relevance_score']
            formatted.append(
                f"[Result {i} | Source: {source} | Page: {page} | Relevance: {score:.2f}]\n"
                f"{result['content']}"
            )
        
        return "\n\n" + "="*50 + "\n\n".join(formatted)
    
    except Exception as e:
        return f"Error searching documents: {str(e)}"


@mcp.tool()
def get_sarawak_context(query: str, num_results: int = 3) -> str:
    """
    Get formatted context from Sarawak tourism documents for answering questions.
    
    Args:
        query: The question or topic about Sarawak
        num_results: Number of context chunks to retrieve (default: 3)
    
    Returns:
        Formatted context string ready for LLM consumption
    """
    try:
        pipeline = get_pipeline()
        return pipeline.get_context_string(query, k=num_results)
    
    except Exception as e:
        return f"Error retrieving context: {str(e)}"


@mcp.tool()
def list_available_documents() -> str:
    """
    List all available Sarawak tourism documents in the knowledge base.
    
    Returns:
        List of document filenames
    """
    try:
        data_dir = Path(os.getenv("DATA_DIR", "data"))
        pdf_files = list(data_dir.glob("*.pdf"))
        
        if not pdf_files:
            return "No documents found in the data directory."
        
        doc_list = "\n".join([f"- {pdf.name}" for pdf in pdf_files])
        return f"Available Sarawak Tourism Documents ({len(pdf_files)}):\n{doc_list}"
    
    except Exception as e:
        return f"Error listing documents: {str(e)}"


@mcp.tool()
def reload_knowledge_base() -> str:
    """
    Reload the knowledge base from PDF documents.
    Use this after adding new documents to the data folder.
    
    Returns:
        Status message
    """
    global _pipeline
    try:
        _pipeline = initialize_pipeline(force_reload=True)
        return "Knowledge base reloaded successfully."
    
    except Exception as e:
        return f"Error reloading knowledge base: {str(e)}"


if __name__ == "__main__":
    print("Starting Sarawak Tourism MCP Server...")
    mcp.run()
