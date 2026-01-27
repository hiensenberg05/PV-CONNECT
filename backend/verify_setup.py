"""
Quick verification script to check all connections
Run this to verify the NOVA backend is properly configured
"""
import sys
from pathlib import Path

print("=" * 60)
print("NOVA Backend Verification")
print("=" * 60)

# Test 1: Check Python version
print("\n1. Python Version:")
print(f"   ✓ {sys.version}")

# Test 2: Check imports
print("\n2. Checking imports...")
try:
    from app.config import settings
    print("   ✓ Config loaded")
    print(f"   ✓ Groq model: {settings.GROQ_MODEL}")
except Exception as e:
    print(f"   ✗ Config error: {e}")
    sys.exit(1)

try:
    from app.state import NovaState
    print("   ✓ State module loaded")
except Exception as e:
    print(f"   ✗ State error: {e}")
    sys.exit(1)

try:
    from app.services.llm_service import llm_service
    print("   ✓ LLM service loaded")
except Exception as e:
    print(f"   ✗ LLM service error: {e}")
    sys.exit(1)

try:
    from app.services.rag_service import rag_service
    print("   ✓ RAG service loaded")
except Exception as e:
    print(f"   ✗ RAG service error: {e}")
    sys.exit(1)

try:
    import groq
    print("   ✓ Groq SDK installed")
except ImportError:
    print("   ✗ Groq SDK missing (pip install groq)")

try:
    import sentence_transformers
    print("   ✓ Sentence Transformers installed")
except ImportError:
    print("   ✗ Sentence Transformers missing (pip install sentence-transformers)")

try:
    from app.main import app
    print("   ✓ FastAPI app loaded")
except Exception as e:
    print(f"   ✗ FastAPI error: {e}")
    sys.exit(1)

# Test 3: Check Environment
print("\n3. Checking usage...")
if settings.GROQ_API_KEY:
    print("   ✓ GROQ_API_KEY found")
else:
    print("   ⚠ GROQ_API_KEY not set in .env")

try:
    ollama_url = settings.OLLAMA_BASE_URL
    print(f"   ✓ OLLAMA_BASE_URL: {ollama_url}")
except Exception:
    pass

# Test 4: Check Embedding Model
print("\n4. Checking Embedding Model...")
try:
    from app.services.rag_service import rag_service
    if rag_service.model:
        print("   ✓ Embedding model loaded successfully")
    else:
        print("   ⚠ Embedding model failed to load")
except Exception as e:
     print(f"   ✗ Error checking embedding model: {e}")


print("\n" + "=" * 60)
print("Verification Complete!")
print("=" * 60)
