# Model Update to Gemini 2.5 Flash

## Change Applied ✅

**Updated in `config.py`:**
```python
# Before:
GEMINI_TEXT_MODEL: str = "gemini-2.0-flash"
GEMINI_VISION_MODEL: str = "gemini-2.0-flash"

# After:
GEMINI_TEXT_MODEL: str = "gemini-2.5-flash"  ✅
GEMINI_VISION_MODEL: str = "gemini-2.5-flash"  ✅
```

## Status
✅ **Updated to Gemini 2.5 Flash**

The backend is running with `--reload` so it will automatically restart and use the new model.

## Benefits of Gemini 2.5 Flash
- Latest model with improved performance
- Better accuracy and understanding
- Enhanced multilingual capabilities
- Faster response times
- More efficient token usage

## Test
The backend will auto-reload. Try sending a message from the frontend to test the new model!
