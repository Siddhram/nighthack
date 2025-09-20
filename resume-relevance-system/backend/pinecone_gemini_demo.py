"""
Simple demo script for Pinecone + Gemini integration
This demonstrates the key functionality without complex dependencies
"""

import sys
import os

# Set up environment variables directly
os.environ['PINECONE_API_KEY'] = 'pcsk_4B27To_tY2jeLoxqgm97GKUfwxMccU39ZsN3jcd2D8Lq7UjZhjwEyHerwKDc8hpeinqpe'
os.environ['NOMIC_API_KEY'] = 'nk-LeXriqiihZl6pT8TT4QhSB8JQVhmJBAznO6Y-EaaDX4'
os.environ['GEMINI_API_KEY'] = 'your_gemini_api_key_here'  # Replace with actual key

# Import required libraries
try:
    import requests
    import numpy as np
    from PyPDF2 import PdfReader
    from pinecone import Pinecone
    from nomic import login, embed
    import google.generativeai as genai
    from io import BytesIO
    import re
    print("✅ All libraries imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class SimpleTextSplitter:
    """Simple text splitter"""
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text):
        """Split text into chunks"""
        if not text.strip():
            return []
        
        text = re.sub(r'\s+', ' ', text.strip())
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = end - self.chunk_overlap
        
        return chunks

class SimplePineconeGeminiDemo:
    def __init__(self):
        print("🚀 Initializing Pinecone + Gemini Demo...")
        
        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])
            self.index = self.pc.Index("lang")
            print("✅ Pinecone initialized")
        except Exception as e:
            print(f"❌ Pinecone initialization failed: {e}")
            return
        
        # Initialize Nomic
        try:
            login(os.environ['NOMIC_API_KEY'])
            print("✅ Nomic initialized")
        except Exception as e:
            print(f"❌ Nomic initialization failed: {e}")
            return
        
        # Initialize Gemini (optional)
        try:
            if os.environ['GEMINI_API_KEY'] != 'your_gemini_api_key_here':
                genai.configure(api_key=os.environ['GEMINI_API_KEY'])
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini initialized")
            else:
                self.gemini_model = None
                print("⚠️ Gemini not configured (no API key)")
        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
            self.gemini_model = None
        
        self.text_splitter = SimpleTextSplitter()
        print("✅ Demo initialized successfully!\n")
    
    def create_embeddings(self, texts):
        """Create embeddings using Nomic"""
        try:
            output = embed.text(
                texts=texts,
                model='nomic-embed-text-v1.5',
                task_type='search_document',
                dimensionality=256
            )
            return np.array(output['embeddings'])
        except Exception as e:
            print(f"❌ Error creating embeddings: {e}")
            return np.array([])
    
    def process_text(self, text, document_id="demo_doc"):
        """Process text and store in Pinecone"""
        print(f"📄 Processing text (length: {len(text)})...")
        
        # Split text
        chunks = self.text_splitter.split_text(text)
        print(f"📑 Split into {len(chunks)} chunks")
        
        if not chunks:
            return False
        
        # Create embeddings
        embeddings = self.create_embeddings(chunks)
        if embeddings.size == 0:
            return False
        
        print(f"🧠 Created embeddings (shape: {embeddings.shape})")
        
        # Store in Pinecone
        try:
            vectors_to_upsert = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{document_id}_{i}"
                metadata = {"text": chunk, "document_id": document_id}
                vectors_to_upsert.append((vector_id, embedding.tolist(), metadata))
            
            self.index.upsert(vectors=vectors_to_upsert)
            print(f"💾 Stored {len(vectors_to_upsert)} vectors in Pinecone")
            return True
            
        except Exception as e:
            print(f"❌ Error storing in Pinecone: {e}")
            return False
    
    def search_similar(self, query, top_k=3):
        """Search for similar content"""
        print(f"🔍 Searching for: '{query}'")
        
        try:
            # Create query embedding
            query_embedding = embed.text(
                texts=[query],
                model='nomic-embed-text-v1.5',
                task_type='search_query',
                dimensionality=256
            )['embeddings'][0]
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            print(f"📊 Found {len(results.get('matches', []))} results")
            
            for i, match in enumerate(results.get('matches', [])):
                score = match.get('score', 0)
                text = match.get('metadata', {}).get('text', '')
                print(f"\n🎯 Result {i+1} (Score: {score:.3f})")
                print(f"   {text[:100]}...")
            
            return results.get('matches', [])
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

def demo_workflow():
    """Run a complete demo workflow"""
    print("=" * 60)
    print("🎯 PINECONE + GEMINI INTEGRATION DEMO")
    print("=" * 60)
    
    # Initialize service
    service = SimplePineconeGeminiDemo()
    
    # Demo text (resume sample)
    demo_text = """
    John Doe is a Senior Software Engineer with 5 years of experience in Python development.
    He has extensive knowledge of machine learning frameworks including TensorFlow, PyTorch, 
    and scikit-learn. John has worked on various AI projects including natural language 
    processing, computer vision, and data analytics. He holds a Master's degree in Computer 
    Science from Stanford University. His technical skills include Python, JavaScript, 
    Docker, Kubernetes, AWS, and PostgreSQL. John has led teams of 3-5 developers and 
    has experience with agile methodologies.
    """
    
    print("1️⃣ Processing sample resume text...")
    success = service.process_text(demo_text, "john_doe_resume")
    
    if not success:
        print("❌ Failed to process text. Check your API keys and connections.")
        return
    
    print("\n2️⃣ Testing search functionality...")
    
    # Test searches
    queries = [
        "Python machine learning experience",
        "team leadership skills",
        "university education background"
    ]
    
    for query in queries:
        print(f"\n{'='*40}")
        service.search_similar(query, top_k=2)
    
    print("\n" + "="*60)
    print("✅ Demo completed successfully!")
    print("\n🔧 Next steps:")
    print("   1. Add your Gemini API key to test AI responses")
    print("   2. Try uploading PDF files")
    print("   3. Run the FastAPI server for REST API access")
    print("="*60)

if __name__ == "__main__":
    demo_workflow()