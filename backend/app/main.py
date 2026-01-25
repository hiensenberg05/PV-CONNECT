from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import webhooks

app = FastAPI(title="PV Connect", version="0.1.0")

# CORS middleware for WhatsApp webhook integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks.router, prefix="/webhook", tags=["webhook"])


@app.get("/health")
async def health():
    return {"status": "ok"}
