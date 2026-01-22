"""
Pre-flight check for PV Connect ngrok setup
Run this before starting the server to verify everything is ready
"""

import sys
import os
from pathlib import Path

def check_mark(condition):
    return "✅" if condition else "❌"

def main():
    print("\n" + "="*80)
    print("🔍 PV CONNECT - PRE-FLIGHT CHECK")
    print("="*80 + "\n")
    
    checks_passed = 0
    total_checks = 0
    
    # Check 1: app/main.py exists
    total_checks += 1
    app_exists = os.path.exists("backend/app/main.py")
    print(f"{check_mark(app_exists)} FastAPI app found at backend/app/main.py")
    if app_exists:
        checks_passed += 1
    else:
        print("   💡 Make sure you're in the PV-CONNECT root directory")
    
    # Check 2: .env file exists
    total_checks += 1
    env_exists = os.path.exists(".env")
    print(f"{check_mark(env_exists)} Environment file (.env) found")
    if env_exists:
        checks_passed += 1
    else:
        print("   💡 Copy env_example to .env and fill in your credentials")
    
    # Check 3: pyngrok installed
    total_checks += 1
    try:
        import pyngrok
        pyngrok_installed = True
        print(f"✅ pyngrok library installed (v{pyngrok.__version__})")
        checks_passed += 1
    except ImportError:
        pyngrok_installed = False
        print("❌ pyngrok library NOT installed")
        print("   💡 Run: pip install pyngrok")
    
    # Check 4: uvicorn installed
    total_checks += 1
    try:
        import uvicorn
        uvicorn_installed = True
        print(f"✅ uvicorn library installed")
        checks_passed += 1
    except ImportError:
        uvicorn_installed = False
        print("❌ uvicorn library NOT installed")
        print("   💡 Run: pip install uvicorn")
    
    # Check 5: FastAPI installed
    total_checks += 1
    try:
        import fastapi
        fastapi_installed = True
        print(f"✅ FastAPI library installed (v{fastapi.__version__})")
        checks_passed += 1
    except ImportError:
        fastapi_installed = False
        print("❌ FastAPI library NOT installed")
        print("   💡 Run: pip install -r backend/requirements.txt")
    
    # Check 6: ngrok auth token
    total_checks += 1
    ngrok_config_path = Path.home() / ".ngrok2" / "ngrok.yml"
    ngrok_configured = ngrok_config_path.exists()
    print(f"{check_mark(ngrok_configured)} ngrok auth token configured")
    if not ngrok_configured:
        print("   💡 Run: ngrok config add-authtoken YOUR_TOKEN")
        print("   💡 Get token from: https://dashboard.ngrok.com/get-started/your-authtoken")
    else:
        checks_passed += 1
    
    # Check 7: Environment variables
    if env_exists:
        total_checks += 1
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv("GEMINI_API_KEY")
        has_gemini = gemini_key and len(gemini_key) > 10
        print(f"{check_mark(has_gemini)} GEMINI_API_KEY configured")
        if has_gemini:
            checks_passed += 1
        else:
            print("   💡 Set GEMINI_API_KEY in .env file")
    
    # Summary
    print("\n" + "="*80)
    print(f"📊 CHECKS PASSED: {checks_passed}/{total_checks}")
    print("="*80 + "\n")
    
    if checks_passed == total_checks:
        print("🎉 ALL CHECKS PASSED! You're ready to run:")
        print("   python run_with_ngrok.py")
        print("   OR")
        print("   python simple_ngrok.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above before running the server.")
        print("\n📚 Quick fixes:")
        if not pyngrok_installed:
            print("   pip install pyngrok")
        if not app_exists:
            print("   cd to PV-CONNECT root directory")
        if not env_exists:
            print("   cp env_example .env")
        if not ngrok_configured:
            print("   ngrok config add-authtoken YOUR_TOKEN")
    
    print()

if __name__ == "__main__":
    main()
