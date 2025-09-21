"""
Pinecone and Gemini integration service for resume relevance system
"""
import os
import requests
import numpy as np
from typing import List, Dict, Any, Optional
from PyPDF2 import PdfReader
from pinecone import Pinecone
import google.generativeai as genai
from io import BytesIO
import re

# Optional import for nomic - handle gracefully if not available
try:
    from nomic import login, embed
    NOMIC_AVAILABLE = True
except ImportError:
    print("Note: Nomic not available - using fallback embeddings")
    NOMIC_AVAILABLE = False
    login = None
    embed = None

from app.config import settings


class SimpleTextSplitter:
    """Simple text splitter to replace langchain's RecursiveCharacterTextSplitter"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if not text.strip():
            return []
        
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Define end position
            end = start + self.chunk_size
            
            # If this would be the last chunk and it's small, extend it
            if end < len(text) and len(text) - end < self.chunk_size * 0.5:
                end = len(text)
            
            # Try to find a good breaking point (sentence end, paragraph, etc.)
            if end < len(text):
                # Look for sentence endings
                for i in range(min(100, end - start), 0, -1):
                    if text[start + i - 1] in '.!?':
                        end = start + i
                        break
                else:
                    # Look for word boundaries
                    while end > start and end < len(text) and text[end] != ' ':
                        end -= 1
                    if end == start:  # Fallback to original end
                        end = start + self.chunk_size
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            if end >= len(text):
                break
            
            start = end - self.chunk_overlap
            if start <= 0:
                start = end
        
        return chunks


class PineconeGeminiService:
    """Service for handling Pinecone vector operations and Gemini AI integration"""
    
    def __init__(self):
        """Initialize Pinecone and Gemini clients"""
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.pc.Index(settings.pinecone_index_name)
        
        # Initialize Nomic for embeddings (optional)
        self.nomic_api_key = settings.nomic_api_key
        self.nomic_available = NOMIC_AVAILABLE
        
        if NOMIC_AVAILABLE and login:
            try:
                login(self.nomic_api_key)
            except Exception as e:
                print(f"Warning: Failed to login to Nomic: {e}")
                self.nomic_available = False
        
        # Initialize Gemini
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(settings.llm_model)
        else:
            self.gemini_model = None
            
        # Text splitter for chunking
        self.text_splitter = SimpleTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
    
    def download_pdf_from_url(self, pdf_url: str) -> Optional[str]:
        """Download PDF from URL and return the content as text"""
        try:
            response = requests.get(pdf_url, stream=True)
            if response.status_code == 200:
                # Read PDF content from memory
                pdf_content = BytesIO(response.content)
                return self._extract_text_from_pdf_bytes(pdf_content)
            else:
                print(f"Failed to download PDF. HTTP Status Code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None
    
    def _extract_text_from_pdf_bytes(self, pdf_content: BytesIO) -> str:
        """Extract text from PDF bytes"""
        try:
            pdf_reader = PdfReader(pdf_content)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
            return extracted_text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_pdf_file(self, file_path: str) -> str:
        """Extract text from local PDF file"""
        try:
            pdf_reader = PdfReader(file_path)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
            return extracted_text
        except Exception as e:
            print(f"Error extracting text from PDF file: {e}")
            return ""
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings using Nomic AI or fallback method"""
        try:
            if self.nomic_available and embed:
                output = embed.text(
                    texts=texts,
                    model=settings.embedding_model,
                    task_type='search_document',
                    dimensionality=settings.embedding_dimensionality
                )
                return np.array(output['embeddings'])
            else:
                # Fallback to simple random embeddings for development
                print("Warning: Using fallback embeddings - Nomic not available")
                return np.random.random((len(texts), settings.embedding_dimensionality))
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            # Fallback to simple random embeddings
            return np.random.random((len(texts), settings.embedding_dimensionality))
    
    def process_and_store_document(self, text: str, document_id: str = None) -> bool:
        """Process document text, create embeddings, and store in Pinecone"""
        try:
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(text)
            
            if not text_chunks:
                return False
            
            # Create embeddings
            embeddings = self.create_embeddings(text_chunks)
            
            if embeddings.size == 0:
                return False
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
                vector_id = f"{document_id}_{i}" if document_id else str(i)
                metadata = {
                    "text": chunk,
                    "document_id": document_id or "default",
                    "chunk_index": i
                }
                vectors_to_upsert.append((vector_id, embedding.tolist(), metadata))
            
            # Upsert vectors into Pinecone
            self.index.upsert(vectors=vectors_to_upsert)
            return True
            
        except Exception as e:
            print(f"Error processing and storing document: {e}")
            return False
    
    def process_pdf_url(self, pdf_url: str, document_id: str = None) -> bool:
        """Download PDF from URL, process, and store in Pinecone"""
        text = self.download_pdf_from_url(pdf_url)
        if text:
            return self.process_and_store_document(text, document_id)
        return False
    
    def process_pdf_file(self, file_path: str, document_id: str = None) -> bool:
        """Process local PDF file and store in Pinecone"""
        text = self.extract_text_from_pdf_file(file_path)
        if text:
            return self.process_and_store_document(text, document_id)
        return False
    
    def create_query_embedding(self, query: str) -> Optional[List[float]]:
        """Create embedding for a search query"""
        try:
            query_embedding = embed.text(
                texts=[query],
                model=settings.embedding_model,
                task_type='search_query',
                dimensionality=settings.embedding_dimensionality
            )['embeddings'][0]
            return query_embedding
        except Exception as e:
            print(f"Error creating query embedding: {e}")
            return None
    
    def search_similar_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content in Pinecone"""
        try:
            query_embedding = self.create_query_embedding(query)
            if not query_embedding:
                return []
            
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            results = []
            for match in search_results.get('matches', []):
                results.append({
                    'score': match.get('score', 0),
                    'text': match.get('metadata', {}).get('text', ''),
                    'document_id': match.get('metadata', {}).get('document_id', ''),
                    'chunk_index': match.get('metadata', {}).get('chunk_index', 0)
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching similar content: {e}")
            return []
    
    def generate_response_with_gemini(self, query: str, context_texts: List[str]) -> str:
        """Generate response using Gemini with retrieved context"""
        if not self.gemini_model:
            return "Gemini API key not configured"
        
        try:
            # Combine context texts
            context = " ".join(context_texts)
            
            # Create prompt for Gemini
            prompt = f"""
            Based on the following context, please answer the user's question:
            
            Context: {context}
            
            Question: {query}
            
            Please provide a comprehensive and accurate answer based only on the provided context. 
            If the context doesn't contain enough information to answer the question, 
            please state that clearly.
            """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text if response.text else "No response generated"
            
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return f"Error generating response: {str(e)}"
    
    def query_rag_system(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Complete RAG pipeline: search + generate response"""
        try:
            # Search for relevant content
            search_results = self.search_similar_content(query, top_k)
            
            if not search_results:
                return {
                    "response": "No relevant information found.",
                    "sources": [],
                    "confidence": 0
                }
            
            # Extract context texts
            context_texts = [result['text'] for result in search_results]
            
            # Generate response using Gemini
            response = self.generate_response_with_gemini(query, context_texts)
            
            return {
                "response": response,
                "sources": search_results,
                "confidence": max([result['score'] for result in search_results]) if search_results else 0
            }
            
        except Exception as e:
            print(f"Error in RAG system: {e}")
            return {
                "response": f"Error processing query: {str(e)}",
                "sources": [],
                "confidence": 0
            }
    
    def clear_index(self) -> bool:
        """Clear all vectors from the Pinecone index"""
        try:
            self.index.delete(delete_all=True)
            return True
        except Exception as e:
            print(f"Error clearing index: {e}")
            return False
    
    def evaluate_resume_relevance(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Evaluate resume relevance against job description using Gemini"""
        if not self.gemini_model:
            return {"error": "Gemini API key not configured"}
        
        try:
            prompt = f"""
            You are an expert HR professional tasked with evaluating resume relevance against job requirements.
            
            Job Description:
            {job_description}
            
            Resume:
            {resume_text}
            
            Please provide:
            1. Overall relevance score (0-100)
            2. Key strengths (skills/experience that match)
            3. Areas of concern (missing requirements)
            4. Detailed analysis
            
            Format your response as a structured analysis.
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            return {
                "analysis": response.text if response.text else "No analysis generated",
                "status": "success"
            }
            
        except Exception as e:
            return {"error": f"Error evaluating resume: {str(e)}"}


# Global instance
pinecone_gemini_service = PineconeGeminiService()