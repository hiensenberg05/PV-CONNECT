"""Test if all imports work"""
try:
    from app.main import app
    print("SUCCESS: App imported successfully!")
    print("SUCCESS: All dependencies are installed correctly!")
except Exception as e:
    print(f"ERROR: Import failed: {e}")
    import traceback
    traceback.print_exc()
