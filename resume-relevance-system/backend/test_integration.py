"""
Test script for Pinecone and Gemini integration
"""
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.config import settings
from app.services.pinecone_gemini_service import pinecone_gemini_service

def test_configuration():
    """Test if all configurations are properly set"""
    print("=== Configuration Test ===")
    print(f"Pinecone API Key configured: {'Yes' if settings.pinecone_api_key else 'No'}")
    print(f"Nomic API Key configured: {'Yes' if settings.nomic_api_key else 'No'}")
    print(f"Gemini API Key configured: {'Yes' if settings.gemini_api_key else 'No'}")
    print(f"Pinecone Index: {settings.pinecone_index_name}")
    print(f"Embedding Model: {settings.embedding_model}")
    print(f"LLM Model: {settings.llm_model}")
    print()

def test_embedding():
    """Test embedding creation"""
    print("=== Embedding Test ===")
    try:
        test_texts = ["This is a test document about artificial intelligence.", 
                     "Machine learning is a subset of AI."]
        embeddings = pinecone_gemini_service.create_embeddings(test_texts)
        print(f"Created embeddings for {len(test_texts)} texts")
        print(f"Embedding dimensions: {embeddings.shape}")
        print("✅ Embedding test passed")
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
    print()

def test_text_processing():
    """Test text processing and storage"""
    print("=== Text Processing Test ===")
    try:
        test_document = """
        John Doe is a software engineer with 5 years of experience in Python, 
        Machine Learning, and Data Science. He has worked on various AI projects 
        including computer vision and natural language processing. John holds a 
        Bachelor's degree in Computer Science and has expertise in frameworks 
        like TensorFlow, PyTorch, and scikit-learn.
        """
        
        success = pinecone_gemini_service.process_and_store_document(
            text=test_document, 
            document_id="test_resume"
        )
        
        if success:
            print("✅ Document processing and storage test passed")
        else:
            print("❌ Document processing and storage test failed")
            
    except Exception as e:
        print(f"❌ Text processing test failed: {e}")
    print()

def test_search():
    """Test search functionality"""
    print("=== Search Test ===")
    try:
        query = "Python machine learning experience"
        results = pinecone_gemini_service.search_similar_content(query, top_k=3)
        
        print(f"Search query: '{query}'")
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Score: {result['score']:.3f}")
            print(f"  Text: {result['text'][:100]}...")
            print()
        
        if results:
            print("✅ Search test passed")
        else:
            print("❌ Search test failed - no results found")
            
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    print()

def test_rag_system():
    """Test complete RAG system"""
    print("=== RAG System Test ===")
    try:
        query = "What programming languages and skills does John have?"
        result = pinecone_gemini_service.query_rag_system(query)
        
        print(f"Query: '{query}'")
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Number of sources: {len(result['sources'])}")
        
        if result['response'] and "Error" not in result['response']:
            print("✅ RAG system test passed")
        else:
            print("❌ RAG system test failed")
            
    except Exception as e:
        print(f"❌ RAG system test failed: {e}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting Pinecone + Gemini Integration Tests\n")
    
    test_configuration()
    test_embedding()
    test_text_processing()
    test_search()
    
    # Only test RAG if Gemini is configured
    if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
        test_rag_system()
    else:
        print("⚠️  Skipping RAG test - Gemini API key not configured")
        print("   Please set GEMINI_API_KEY in your .env file to test Gemini integration")
    
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main()