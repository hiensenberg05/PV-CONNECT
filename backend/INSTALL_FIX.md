# Quick Fix for Python 3.13 Installation Issues

## Problem
Python 3.13 has compatibility issues with some packages that require Rust compiler (pydantic-core, pillow).

## Solution

### Option 1: Use Python 3.11 or 3.12 (Recommended)
```bash
# Download and install Python 3.11 or 3.12
# Then recreate venv
cd d:\nova
python -m venv venv
venv\Scripts\activate
cd backend
pip install -r requirements.txt
```

### Option 2: Install Without Optional Dependencies
```bash
# Already in venv
cd d:\nova\backend
pip install fastapi uvicorn pydantic pydantic-settings
pip install langgraph google-generativeai
pip install motor pymongo
pip install python-dotenv python-multipart httpx
pip install pytest pytest-asyncio
```

### Option 3: Use uv with system Python
```bash
cd d:\nova\backend
uv pip install --system -r requirements.txt
```

## Updated requirements.txt

I've updated the file to:
- Use flexible versions (>=) instead of exact versions
- Comment out Pillow and Cloudinary (optional for now)
- These are only needed for document upload feature

## Test Installation

```bash
# Activate venv
cd d:\nova
venv\Scripts\activate

# Install core dependencies
cd backend
pip install fastapi uvicorn[standard] pydantic pydantic-settings
pip install langgraph google-generativeai
pip install motor pymongo python-dotenv httpx

# Test
python -c "import fastapi; import langgraph; print('✅ Core packages installed')"
```

## Run Backend

```bash
# Make sure you're in venv
cd d:\nova\backend
uvicorn app.main:app --reload
```

The backend will work without Pillow/Cloudinary - those are only for image upload features which can be added later.
