# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.api import webhooks, dashboard, websockets

# app = FastAPI(title="PV Connect", version="0.1.0")

# # Allow dashboard dev origin; tighten in production.
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(webhooks.router, prefix="/webhook", tags=["webhook"])
# app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
# app.include_router(websockets.router)


# @app.get("/health")
# async def health():
#     return {"status": "ok"}


from fastapi import FastAPI
from app.api.chat_ui import router as chat_ui_router
from app.api.chat_api import router as chat_api_router

app = FastAPI()

app.include_router(chat_ui_router)
app.include_router(chat_api_router, prefix="/api")
