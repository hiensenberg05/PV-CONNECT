# 🚀 PV Connect - ngrok Setup Complete!

## ✅ What I've Created for You

I've set up **3 Python scripts** to run your FastAPI server with ngrok:

### 1. **`run_with_ngrok.py`** (Recommended - Full Featured)
- ✅ Comprehensive error handling
- ✅ Beautiful console output with all URLs
- ✅ Graceful shutdown on Ctrl+C
- ✅ Pre-flight checks

### 2. **`simple_ngrok.py`** (Quick & Simple)
- ✅ Minimal code
- ✅ Fast startup
- ✅ Perfect for quick testing

### 3. **`check_setup.py`** (Diagnostic Tool)
- ✅ Validates all dependencies
- ✅ Checks configuration
- ✅ Provides helpful error messages

---

## 📦 Installation Steps

### Step 1: Install pyngrok

```powershell
pip install pyngrok
```

✅ **Already done!** I've installed it for you.

### Step 2: Set up ngrok Authentication

1. **Sign up** at https://ngrok.com (free tier works fine)
2. **Get your auth token** from https://dashboard.ngrok.com/get-started/your-authtoken
3. **Configure it** (one-time setup):

```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

---

## 🎯 How to Run

### Option A: Full Featured Script (Recommended)

```powershell
cd C:\Users\RISHI\PV-CONNECT
python run_with_ngrok.py
```

### Option B: Simple Script

```powershell
cd C:\Users\RISHI\PV-CONNECT
python simple_ngrok.py
```

---

## 📋 What You'll See

When you run the script successfully, you'll see:

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

---

## 🔗 Configure WhatsApp Webhook

1. **Copy** the webhook URL from the console (e.g., `https://abc123.ngrok-free.app/webhook`)
2. **Go to** [Meta Developer Console](https://developers.facebook.com/)
3. **Navigate to** your WhatsApp Business app
4. **Paste** the webhook URL
5. **Use** your `WHATSAPP_VERIFY_TOKEN` from `.env` for verification

---

## 🛠️ Troubleshooting

### ❌ "ngrok authentication failed"

**Solution:**
```powershell
ngrok config add-authtoken YOUR_TOKEN_HERE
```

Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

### ❌ "backend/app/main.py not found"

**Solution:** Make sure you're in the PV-CONNECT root directory:
```powershell
cd C:\Users\RISHI\PV-CONNECT
```

### ❌ "pyngrok not installed"

**Solution:**
```powershell
pip install pyngrok
```

### ❌ Port 8000 already in use

**Solution:** Kill the existing process or change the port in the script:
```python
PORT = 8001  # Change this line in the script
```

---

## 🧪 Test Your Setup

Run the diagnostic tool:

```powershell
python check_setup.py
```

This will verify:
- ✅ FastAPI app exists
- ✅ .env file configured
- ✅ pyngrok installed
- ✅ uvicorn installed
- ✅ FastAPI installed
- ✅ ngrok auth token set
- ✅ GEMINI_API_KEY configured

---

## 🎨 Customization

### Change ngrok Region

Edit the script and change:
```python
conf.get_default().region = "in"  # Options: us, eu, ap, au, sa, jp, in
```

### Enable Auto-Reload (Development)

In `run_with_ngrok.py`, change:
```python
reload=False  # Change to True
```

### Change Port

```python
PORT = 8001  # Change from 8000 to any port
```

---

## 📝 Important Notes

- 🔄 **Free tier**: ngrok URL changes each time you restart
- 💰 **Paid plan**: Get a reserved domain that doesn't change
- ⏱️ **Rate limits**: Free tier has connection limits (usually sufficient for testing)
- 🌍 **Region**: Set to India (`in`) by default for best performance
- 🛑 **Stopping**: Press `Ctrl+C` to stop both server and tunnel

---

## 🎯 Quick Reference Commands

```powershell
# Install dependency
pip install pyngrok

# Set ngrok auth token (one-time)
ngrok config add-authtoken YOUR_TOKEN

# Check setup
python check_setup.py

# Run server with ngrok (recommended)
python run_with_ngrok.py

# Run server with ngrok (simple)
python simple_ngrok.py

# Stop server
Ctrl+C
```

---

## 📚 Additional Resources

- **ngrok Documentation**: https://ngrok.com/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **WhatsApp Cloud API**: https://developers.facebook.com/docs/whatsapp/cloud-api
- **Full Setup Guide**: See `NGROK_SETUP.md`

---

## ✨ What's Next?

1. ✅ Install pyngrok (Done!)
2. ⏳ Set ngrok auth token
3. ⏳ Run `python run_with_ngrok.py`
4. ⏳ Copy webhook URL
5. ⏳ Configure in Meta Developer Console
6. ⏳ Test with WhatsApp!

---

**Need help?** Check `NGROK_SETUP.md` for detailed troubleshooting or run `python check_setup.py` to diagnose issues.

**Happy coding! 🚀**
