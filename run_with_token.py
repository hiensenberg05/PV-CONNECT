"""
PV Connect - FastAPI Server with ngrok
Loads configuration from .env file
"""

import os
import sys
import time
from pyngrok import ngrok
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
PORT = 8000
REGION = "in"  # Options: us, eu, ap, au, sa, jp, in
# ============================================================================


def print_banner():
    """Print a nice banner with the ngrok URL"""
    print("\n" + "=" * 80)
    print("🚀 PV CONNECT - FASTAPI SERVER WITH NGROK")
    print("=" * 80 + "\n")


def start_ngrok(port: int = 8000):
    """Start ngrok tunnel and return the public URL"""
    
    # Check if token is set
    if not NGROK_AUTH_TOKEN or NGROK_AUTH_TOKEN == "":
        print("\n" + "="*80)
        print("❌ NGROK AUTH TOKEN NOT SET!")
        print("="*80)
        print("\n📋 Instructions:")
        print("1. Go to: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("2. Copy your auth token")
        print("3. Open the .env file in the project root")
        print("4. Add this line: NGROK_AUTH_TOKEN=your_token_here")
        print("\nExample .env entry:")
        print('   NGROK_AUTH_TOKEN=2abc123def456...')
        print("\n" + "="*80 + "\n")
        sys.exit(1)
    
    try:
        # Set auth token
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        
        # Open ngrok tunnel
        print("🔧 Starting ngrok tunnel...")
        tunnel = ngrok.connect(port, bind_tls=True)
        public_url = tunnel.public_url
        
        print("\n" + "=" * 80)
        print("✅ NGROK TUNNEL ACTIVE!")
        print("=" * 80)
        print(f"\n📡 Public URL: {public_url}")
        print(f"🏠 Local URL:  http://localhost:{port}")
        print(f"\n📋 WhatsApp Webhook URL: {public_url}/webhook")
        print(f" API Docs: {public_url}/docs")
        print(f"❤️  Health Check: {public_url}/health")
        print("\n" + "=" * 80)
        print("⚠️  IMPORTANT: Copy the webhook URL above and paste it in Meta Developer Console")
        print("=" * 80 + "\n")
        
        return public_url
    
    except Exception as e:
        print(f"\n❌ Error starting ngrok: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure your auth token is correct")
        print("   2. Check your internet connection")
        print("   3. Visit https://dashboard.ngrok.com to verify your account")
        sys.exit(1)


def run_server(port: int = 8000):
    """Run the FastAPI server using uvicorn"""
    print(f"🌐 Starting FastAPI server on port {port}...")
    
    # Add backend to Python path
    sys.path.insert(0, os.path.join(os.getcwd(), "backend"))
    
    # Run uvicorn server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )


def main():
    """Main function to orchestrate ngrok and FastAPI server"""
    
    print_banner()
    
    # Start ngrok tunnel first
    public_url = start_ngrok(PORT)
    
    # Give ngrok a moment to stabilize
    time.sleep(1)
    
    print("🎯 Starting FastAPI server...\n")
    
    try:
        # Run the FastAPI server (this will block)
        run_server(PORT)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down server...")
        ngrok.kill()
        print("✅ Server stopped. Ngrok tunnel closed.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error running server: {e}")
        ngrok.kill()
        sys.exit(1)


if __name__ == "__main__":
    # Check if running from correct directory
    if not os.path.exists("backend/app/main.py"):
        print("\n❌ Error: backend/app/main.py not found!")
        print("💡 Make sure you're running this script from the PV-CONNECT root directory:")
        print("   cd PV-CONNECT")
        print("   python run_with_token.py")
        sys.exit(1)
    
    main()
