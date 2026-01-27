# Frontend Setup

## Problem: No Response from Backend

If you're opening `index.html` directly from the file system (`file://`), browsers block fetch requests to `http://localhost:8000` due to CORS security restrictions.

## Solution: Use a Local Web Server

### Option 1: Python HTTP Server (Recommended)

```bash
cd frontend
python server.py
```

Then open: `http://localhost:3000/index.html`

### Option 2: Python Built-in Server

```bash
cd frontend
python -m http.server 3000
```

Then open: `http://localhost:3000/index.html`

### Option 3: Node.js HTTP Server

```bash
cd frontend
npx http-server -p 3000
```

Then open: `http://localhost:3000/index.html`

## Prerequisites

1. **Backend must be running** on `http://localhost:8000`
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **MongoDB must be running** (if using local MongoDB)
   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

## Testing

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend server: `cd frontend && python server.py`
3. Open browser: `http://localhost:3000/index.html`
4. Send a message: "hello"
5. You should see a response asking if you're a Patient or Doctor

## Troubleshooting

### Still no response?

1. **Check browser console** (F12):
   - Look for CORS errors
   - Look for network errors
   - Check if request is being sent

2. **Check backend logs**:
   - Should see incoming requests
   - Check for errors

3. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Check API endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/message \
     -H "Content-Type: application/json" \
     -d '{"message": "hello", "sender_phone": "+1234567890"}'
   ```
