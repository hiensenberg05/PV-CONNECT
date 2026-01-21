from fastapi import APIRouter, Request
from app.agents.graph import graph

router = APIRouter()


@router.post("")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    message = (
        data.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("messages", [{}])[0]
    )
    phone = message.get("from")
    text = (message.get("text") or {}).get("body", "")
    state = {"phone_number": phone, "current_message": text, "messages": [message], "documents": [], "voice_notes": []}
    await graph.ainvoke(state)
    return {"status": "ok"}
