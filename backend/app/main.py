from fastapi import FastAPI
from app.api.webhooks import router as webhook_router

app = FastAPI(title="PV-CONNECT Backend")

app.include_router(webhook_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok", "service": "PV-CONNECT Converse Backend"}
