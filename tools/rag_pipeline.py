"""
RAG Pipeline for Sarawak Tourism & Culture Synth
Handles PDF loading, text chunking, embedding creation, and vector storage.
"""

import os
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


class RAGPipeline:
    """RAG Pipeline for processing and searching Sarawak tourism documents."""
    
    def __init__(
        self,
        data_dir: str = "data",
        chroma_dir: str = ".chroma",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the RAG Pipeline.
        
        Args:
            data_dir: Directory containing PDF files
            chroma_dir: Directory to store ChromaDB data
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
            embedding_model: Name of the sentence-transformers model
        """
        self.data_dir = Path(data_dir)
        self.chroma_dir = Path(chroma_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vector_store = None
        self.documents = []
    
    def load_pdfs(self) -> List[Any]:
        """Load all PDF files from the data directory."""
        pdf_files = list(self.data_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {self.data_dir}")
            return []
        
        documents = []
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                # Add source metadata
                for doc in docs:
                    doc.metadata['source_file'] = pdf_file.name
                documents.extend(docs)
                print(f"Loaded: {pdf_file.name} ({len(docs)} pages)")
            except Exception as e:
                print(f"Error loading {pdf_file.name}: {e}")
        
        self.documents = documents
        return documents
    
    def split_documents(self, documents: List[Any] = None) -> List[Any]:
        """Split documents into chunks."""
        if documents is None:
            documents = self.documents
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, chunks: List[Any] = None, force_reload: bool = False) -> Chroma:
        """Create or load the ChromaDB vector store."""
        # Check if vector store already exists
        if self.chroma_dir.exists() and not force_reload:
            try:
                self.vector_store = Chroma(
                    persist_directory=str(self.chroma_dir),
                    embedding_function=self.embeddings
                )
                print(f"Loaded existing vector store from {self.chroma_dir}")
                return self.vector_store
            except Exception as e:
                print(f"Error loading existing vector store: {e}")
        
        # Create new vector store
        if chunks is None:
            documents = self.load_pdfs()
            if not documents:
                raise ValueError("No documents to process")
            chunks = self.split_documents(documents)
        
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(self.chroma_dir)
        )
        self.vector_store.persist()
        print(f"Created vector store with {len(chunks)} chunks in {self.chroma_dir}")
        return self.vector_store
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of dictionaries with 'content' and 'metadata' keys
        """
        if self.vector_store is None:
            self.create_vector_store()
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'relevance_score': float(score)
            })
        
        return formatted_results
    
    def get_context_string(self, query: str, k: int = 5) -> str:
        """
        Get a formatted context string from search results.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            Formatted string with relevant context
        """
        results = self.search_documents(query, k=k)
        
        if not results:
            return "No relevant information found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source_file', 'Unknown')
            page = result['metadata'].get('page', 'N/A')
            context_parts.append(
                f"[Source {i}: {source}, Page {page}]\n{result['content']}"
            )
        
        return "\n\n---\n\n".join(context_parts)


def initialize_pipeline(data_dir: str = "data", force_reload: bool = False) -> RAGPipeline:
    """Initialize and return a configured RAG pipeline."""
    pipeline = RAGPipeline(data_dir=data_dir)
    pipeline.create_vector_store(force_reload=force_reload)
    return pipeline


# For testing
if __name__ == "__main__":
    pipeline = initialize_pipeline()
    results = pipeline.search_documents("Bako National Park wildlife")
    for r in results:
        print(f"\n--- Score: {r['relevance_score']:.4f} ---")
        print(r['content'][:200])
