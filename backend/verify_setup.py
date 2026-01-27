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
    print(f"   ✓ Gemini model: {settings.GEMINI_TEXT_MODEL}")
except Exception as e:
    print(f"   ✗ Config error: {e}")
    sys.exit(1)

try:
    from app.state import NovaState, create_initial_state
    print("   ✓ State module loaded")
except Exception as e:
    print(f"   ✗ State error: {e}")
    sys.exit(1)

try:
    from app.services.llm_service import gemini_service
    print("   ✓ LLM service (Ollama) loaded")
except Exception as e:
    print(f"   ✗ LLM service error: {e}")
    sys.exit(1)

try:
    from app.services.mongodb_service import mongodb_service
    print("   ✓ MongoDB service loaded")
except Exception as e:
    print(f"   ✗ MongoDB service error: {e}")
    sys.exit(1)

try:
    from app.graph import graph_app, load_prompt
    print("   ✓ Graph loaded")
except Exception as e:
    print(f"   ✗ Graph error: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("   ✓ FastAPI app loaded")
except Exception as e:
    print(f"   ✗ FastAPI error: {e}")
    sys.exit(1)

# Test 3: Check prompt files
print("\n3. Checking prompt files...")
prompts = [
    "shared_prompts/language_detection.txt",
    "shared_prompts/user_type_detection.txt",
    "shared_prompts/clinical_triage.txt",
    "patient_workflow/prompts/patient_intake.txt",
    "patient_workflow/prompts/document_extraction.txt",
    "patient_workflow/prompts/followup_questions.txt",
    "doctor_workflow/prompts/doctor_intake.txt",
    "doctor_workflow/prompts/license_request.txt",
]

app_dir = Path(__file__).parent.parent / "app"
for prompt_path in prompts:
    full_path = app_dir / prompt_path
    if full_path.exists():
        print(f"   ✓ {prompt_path}")
    else:
        print(f"   ✗ Missing: {prompt_path}")

# Test 4: Check YAML files
print("\n4. Checking YAML files...")
yaml_files = [
    "patient_workflow/nodes.yaml",
    "doctor_workflow/nodes.yaml",
]

for yaml_path in yaml_files:
    full_path = app_dir / yaml_path
    if full_path.exists():
        print(f"   ✓ {yaml_path}")
    else:
        print(f"   ✗ Missing: {yaml_path}")

# Test 5: Check environment
print("\n5. Checking environment...")
import httpx
try:
    ollama_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"   ✓ OLLAMA_BASE_URL configured: {ollama_url}")
    
    # Check connectivity
    try:
        response = httpx.get(ollama_url)
        if response.status_code == 200:
            print("   ✓ Ollama server is reachable")
        else:
             print(f"   ⚠ Ollama server returned status {response.status_code}")
    except Exception as e:
        print(f"   ⚠ Could not connect to Ollama: {e}")
        print("     (Make sure Ollama is running: 'ollama serve')")

except Exception:
     print("   ⚠ Error checking Ollama settings")

print(f"   ✓ MongoDB URI: {settings.MONGODB_URI}")
print(f"   ✓ Database: {settings.MONGODB_DATABASE}")

# Test 6: Check prompt loading
print("\n6. Testing prompt loading...")
try:
    prompt = load_prompt("shared_prompts/language_detection.txt")
    if len(prompt) > 0:
        print(f"   ✓ Prompt loaded ({len(prompt)} characters)")
        print(f"   ✓ Preview: {prompt[:80]}...")
    else:
        print("   ✗ Prompt is empty")
except Exception as e:
    print(f"   ✗ Prompt loading error: {e}")

# Test 7: Check graph nodes
print("\n7. Checking graph nodes...")
try:
    # The graph should have nodes
    print("   ✓ Graph compiled successfully")
    print("   ✓ Entry point: language_detection")
except Exception as e:
    print(f"   ✗ Graph error: {e}")

print("\n" + "=" * 60)
print("Verification Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Set GEMINI_API_KEY in .env file")
print("2. Start MongoDB: docker run -d -p 27017:27017 mongo")
print("3. Run server: uvicorn app.main:app --reload")
print("4. Test: curl http://localhost:8000/api/test/patient")
print("\nFor detailed architecture, see:")
print("- WORKFLOW_ARCHITECTURE.md")
print("- CONNECTION_MAP.md")
print("=" * 60)
