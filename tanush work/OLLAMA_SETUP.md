# Ollama Integration Setup Guide

## Overview
This project has been migrated from Google Gemini API to Ollama (local LLM). All LLM functionality now uses Ollama instead of Gemini.

## Changes Made

### 1. Service Layer
- **Created**: `backend/app/services/ollama_service.py` - Replaces `gemini_service.py`
- **Updated**: All imports from `gemini_service` to `ollama_service`
- **Functions**: All LLM functions (detect_language, extract_adverse_event, etc.) now use Ollama

### 2. Configuration
- **Updated**: `backend/app/config.py` - Changed `GEMINI_API_KEY` to `OLLAMA_BASE_URL`
- **Default**: `http://localhost:11434` (Ollama's default port)

### 3. Requirements
- **Removed**: `google-generativeai` package
- **Note**: Ollama uses HTTP API, no Python package needed

### 4. Updated Files
- All node files in `backend/app/agents/nodes/` updated to use Ollama
- `backend/app/main.py` - Updated startup check to verify Ollama connection
- `backend/app/prompts.py` - Updated to mention Ollama instead of Gemini

## Setup Instructions

### 1. Install Ollama
```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

### 2. Start Ollama Server
```bash
ollama serve
```

### 3. Pull Required Models
```bash
# For text processing (required)
ollama pull llama3

# For embeddings/RAG (required for vector search)
ollama pull nomic-embed-text

# For vision/OCR (optional, if you need image processing)
ollama pull llama3.2-vision
```

### 4. Configure Environment
Create a `.env` file in the project root or backend directory:
```bash
# Ollama (default: http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=pv_connect

# Cloudinary (optional)
CLOUDINARY_CLOUD_NAME=your_cloud
CLOUDINARY_API_KEY=your_key
CLOUDINARY_API_SECRET=your_secret
```

## Testing

### Test Ollama Connection
```bash
cd backend
python test_ollama.py
```

This will test:
- Basic Ollama connection
- Language detection
- Adverse event extraction
- User type detection
- Clinical triage
- Follow-up question generation

### Test the API Server
```bash
cd backend
python run.py
```

Then visit:
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Important Notes

### Audio Transcription
- **Current Status**: Not implemented
- **Reason**: Ollama doesn't natively support audio transcription
- **Solution**: Consider integrating Whisper API or another transcription service
- **Location**: `backend/app/agents/nodes/voice_processing.py`

### Vision/OCR
- **Model Required**: `llama3.2-vision` or similar vision-capable model
- **Status**: Implemented but requires vision model
- **Location**: `backend/app/agents/nodes/ocr_processing.py`

### Model Selection
Default models used:
- **Text**: `llama3` (can be changed in `ollama_service.py`)
- **Embeddings**: `nomic-embed-text` (for RAG/vector search, in `rag_service.py`)
- **Vision**: `llama3.2-vision` (for OCR)

To use different models:
- Text: Modify `DEFAULT_MODEL` in `backend/app/services/ollama_service.py`
- Embeddings: Modify `EMBEDDING_MODEL` in `backend/app/services/rag_service.py`

## Troubleshooting

### Ollama Connection Failed
1. Make sure Ollama is running: `ollama serve`
2. Check if Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Verify `OLLAMA_BASE_URL` in your `.env` file

### Model Not Found
1. Pull the required model: `ollama pull llama3`
2. List available models: `ollama list`
3. Update model name in code if using a different model

### Timeout Errors
- Increase timeout in `call_ollama()` function if needed
- Check system resources (Ollama can be resource-intensive)

## Migration Summary

✅ **Completed**:
- Service layer migration
- All imports updated
- Configuration updated
- Requirements updated
- Test script created

⚠️ **Limitations**:
- Audio transcription not yet implemented
- Vision requires specific model installation

## Next Steps

1. Install and start Ollama
2. Pull required models
3. Run test script to verify integration
4. Start the API server
5. Test endpoints

For questions or issues, check the test script output for detailed error messages.
