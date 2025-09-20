# Pinecone + Gemini Integration Guide

This document explains the integration of Pinecone vector database and Google Gemini AI into your resume relevance system, replacing the previous OpenAI setup.

## 🚀 What's New

### Replaced Components:

- ❌ **OpenAI GPT** → ✅ **Google Gemini** for text generation
- ❌ **Local embeddings** → ✅ **Nomic AI embeddings** + **Pinecone** for vector storage
- ✅ **Enhanced RAG (Retrieval-Augmented Generation)** pipeline

### Key Features:

1. **PDF Processing**: Upload PDFs from URLs or files
2. **Vector Storage**: Store document embeddings in Pinecone
3. **Semantic Search**: Find relevant content using vector similarity
4. **AI-Powered Responses**: Generate responses using Gemini AI
5. **Resume Evaluation**: Evaluate resumes against job descriptions

## 📦 New Dependencies

Added to `requirements.txt`:

```
pinecone-client==4.1.0
google-generativeai==0.8.3
nomic==3.0.43
PyPDF2==3.0.1
```

## ⚙️ Configuration

### 1. Environment Variables (.env file)

```env
# Pinecone Configuration
PINECONE_API_KEY=pcsk_4B27To_tY2jeLoxqgm97GKUfwxMccU39ZsN3jcd2D8Lq7UjZhjwEyHerwKDc8hpeinqpe
PINECONE_INDEX_NAME=lang
PINECONE_ENVIRONMENT=us-east-1

# Nomic AI Configuration (for embeddings)
NOMIC_API_KEY=nk-LeXriqiihZl6pT8TT4QhSB8JQVhmJBAznO6Y-EaaDX4

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# AI Settings
EMBEDDING_MODEL=nomic-embed-text-v1.5
LLM_MODEL=gemini-1.5-flash
EMBEDDING_DIMENSIONALITY=256
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### 2. Get Your API Keys

#### Gemini API Key:

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Replace `your_gemini_api_key_here` in the .env file

#### Pinecone & Nomic Keys:

The keys from the reference code are already included, but you should:

1. Get your own [Pinecone API key](https://www.pinecone.io/)
2. Get your own [Nomic API key](https://www.nomic.ai/)

## 🔧 New API Endpoints

### 1. Upload PDF from URL

```http
POST /api/pdf/upload-url
Content-Type: application/json

{
    "url": "https://example.com/resume.pdf",
    "document_id": "john_doe_resume" // optional
}
```

### 2. Upload PDF File

```http
POST /api/pdf/upload-file
Content-Type: multipart/form-data

file: [PDF_FILE]
document_id: "resume_123" // optional
```

### 3. Query Documents (RAG)

```http
POST /api/query
Content-Type: application/json

{
    "question": "What programming languages does the candidate know?",
    "top_k": 5 // optional, defaults to 5
}
```

### 4. Evaluate Resume with Gemini

```http
POST /api/resume/evaluate-with-gemini
Content-Type: application/json

{
    "resume_text": "John Doe is a software engineer...",
    "job_description": "We are looking for a Python developer..."
}
```

### 5. Clear Pinecone Index

```http
DELETE /api/pinecone/clear
```

### 6. Check Configuration

```http
GET /api/config/check
```

## 🏗️ Architecture Overview

```
[PDF Upload] → [Text Extraction] → [Text Chunking] → [Nomic Embeddings] → [Pinecone Storage]
                                                                                    ↓
[User Query] → [Query Embedding] → [Vector Search] → [Retrieved Context] → [Gemini AI] → [Response]
```

## 🧪 Testing the Integration

Run the test script to verify everything works:

```bash
cd backend
python test_integration.py
```

This will test:

- ✅ Configuration setup
- ✅ Embedding creation
- ✅ Document processing and storage
- ✅ Vector search
- ✅ RAG system (if Gemini API key is configured)

## 📝 Usage Examples

### Python Usage:

```python
from app.services.pinecone_gemini_service import pinecone_gemini_service

# Process a PDF from URL
success = pinecone_gemini_service.process_pdf_url(
    pdf_url="https://example.com/resume.pdf",
    document_id="candidate_123"
)

# Query the system
result = pinecone_gemini_service.query_rag_system(
    query="What are the candidate's Python skills?"
)
print(result['response'])

# Evaluate resume
evaluation = pinecone_gemini_service.evaluate_resume_relevance(
    resume_text="John has 5 years Python experience...",
    job_description="Looking for senior Python developer..."
)
```

### cURL Examples:

```bash
# Upload PDF from URL
curl -X POST http://localhost:8000/api/pdf/upload-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/resume.pdf", "document_id": "test_resume"}'

# Query documents
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What programming skills does the candidate have?"}'

# Check configuration
curl http://localhost:8000/api/config/check
```

## 🔍 Key Components

### 1. PineconeGeminiService (`app/services/pinecone_gemini_service.py`)

Main service class handling:

- PDF processing and text extraction
- Embedding creation using Nomic AI
- Vector storage in Pinecone
- Semantic search
- Gemini AI integration for response generation

### 2. Updated Configuration (`app/config.py`)

New settings for:

- Pinecone API credentials
- Nomic AI configuration
- Gemini AI settings
- Text processing parameters

### 3. Enhanced Main App (`app/main.py`)

New endpoints for:

- PDF upload and processing
- Document querying
- Resume evaluation
- System management

## 🚨 Important Notes

1. **API Keys Security**: Never commit real API keys to version control
2. **Rate Limits**: Be aware of API rate limits for Pinecone, Nomic, and Gemini
3. **Costs**: Monitor usage costs for all services
4. **Index Management**: The Pinecone index will persist data between sessions
5. **Error Handling**: All services include comprehensive error handling

## 🔧 Troubleshooting

### Common Issues:

1. **Import Errors**: Run `pip install -r requirements.txt` to install dependencies
2. **API Key Errors**: Verify all API keys are correctly set in .env file
3. **Pinecone Index Errors**: Ensure the index exists and has correct dimensions (256)
4. **Embedding Errors**: Check Nomic API key and internet connection
5. **Gemini Errors**: Verify Gemini API key and model availability

### Debug Mode:

Set `DEBUG=True` in your .env file for detailed error messages.

## 🎯 Next Steps

1. **Set up your Gemini API key** to enable AI responses
2. **Test the integration** using the provided test script
3. **Upload some test documents** and try querying them
4. **Integrate with your frontend** using the new API endpoints
5. **Monitor usage** and optimize for your specific needs

---

## 📞 Support

If you encounter issues:

1. Check the test script output for specific errors
2. Verify all API keys are valid and active
3. Ensure all dependencies are properly installed
4. Check the FastAPI docs at `http://localhost:8000/docs` for endpoint details
