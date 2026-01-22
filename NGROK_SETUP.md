# 🚀 Quick Start Guide - Running PV Connect with ngrok

## Step 1: Install Dependencies

First, make sure you're in the backend directory and have your virtual environment activated:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

Then install the required package:

```powershell
pip install pyngrok
```

Or install all dependencies including pyngrok:

```powershell
pip install -r requirements.txt
```

## Step 2: Set up ngrok Authentication

You need an ngrok account and auth token:

1. Sign up at https://ngrok.com (free tier is fine)
2. Get your auth token from https://dashboard.ngrok.com/get-started/your-authtoken
3. Set it up (one-time setup):

```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## Step 3: Run the Server with ngrok

From the **root directory** (PV-CONNECT), run:

```powershell
python run_with_ngrok.py
```

The script will:
- ✅ Start your FastAPI server on port 8000
- ✅ Open an ngrok tunnel
- ✅ Display the public HTTPS URL prominently
- ✅ Show all important endpoints (webhook, dashboard, docs)

## Step 4: Configure WhatsApp Webhook

Copy the webhook URL from the console output (it will look like):
```
📋 WhatsApp Webhook URL: https://abc123.ngrok-free.app/webhook
```

Then:
1. Go to Meta Developer Console
2. Navigate to your WhatsApp app
3. Paste the webhook URL
4. Use your `WHATSAPP_VERIFY_TOKEN` from `.env` for verification

## Troubleshooting

### Error: "app/main.py not found"
- Make sure you're running from the PV-CONNECT root directory (not backend/)
- The script expects: `PV-CONNECT/app/main.py`

### Error: "ngrok authentication failed"
- Run: `ngrok config add-authtoken YOUR_TOKEN`
- Or set it in code (see alternative method below)

### Alternative: Set auth token in code
If you prefer, you can set the token directly in `run_with_ngrok.py`:

```python
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_AUTH_TOKEN_HERE")
```

Add this line before `tunnel = ngrok.connect(port, bind_tls=True)` in the `start_ngrok()` function.

## What You'll See

When running successfully, you'll see output like:

```
================================================================================
🚀 PV CONNECT - FASTAPI SERVER WITH NGROK
================================================================================

🔧 Starting ngrok tunnel...

================================================================================
✅ NGROK TUNNEL ACTIVE!
================================================================================

📡 Public URL: https://abc123.ngrok-free.app
🏠 Local URL:  http://localhost:8000

📋 WhatsApp Webhook URL: https://abc123.ngrok-free.app/webhook
📊 Dashboard API: https://abc123.ngrok-free.app/dashboard/cases
📚 API Docs: https://abc123.ngrok-free.app/docs
❤️  Health Check: https://abc123.ngrok-free.app/health

================================================================================
⚠️  IMPORTANT: Copy the webhook URL above and paste it in Meta Developer Console
================================================================================
```

## Stopping the Server

Press `Ctrl+C` to stop both the FastAPI server and ngrok tunnel.

## Notes

- The ngrok URL changes each time you restart (unless you have a paid plan with reserved domains)
- Free tier has a limit on connections/minute (usually sufficient for testing)
- The script is configured for India region (`in`) - you can change this in the code
- Server runs without auto-reload by default (change `reload=False` to `reload=True` for development)
