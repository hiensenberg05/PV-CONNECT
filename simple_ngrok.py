"""
Simple ngrok launcher for PV Connect
Just run: python simple_ngrok.py
"""

from pyngrok import ngrok
import uvicorn
import os
import sys

# Configuration
PORT = 8000
REGION = "in"  # Change to: us, eu, ap, au, sa, jp, in

print("\n" + "="*80)
print("🚀 STARTING PV CONNECT WITH NGROK")
print("="*80 + "\n")

# Add backend to Python path
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

# Start ngrok tunnel
print("🔧 Opening ngrok tunnel...")
tunnel = ngrok.connect(PORT, bind_tls=True)
public_url = tunnel.public_url

# Print the URLs
print("\n" + "="*80)
print("✅ NGROK TUNNEL ACTIVE!")
print("="*80)
print(f"\n📡 PUBLIC URL: {public_url}")
print(f"\n📋 WEBHOOK URL (copy this): {public_url}/webhook")
print(f"📚 API DOCS: {public_url}/docs")
print("="*80 + "\n")

# Start FastAPI server
print("🌐 Starting FastAPI server...\n")
uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=False)
