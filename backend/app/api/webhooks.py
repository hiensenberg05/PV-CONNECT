from fastapi import APIRouter, Request
from app.agents.graph import graph
import asyncio

router = APIRouter()


# @router.post("")
# async def whatsapp_webhook(request: Request):
#     data = await request.json()
#     message = (
#         data.get("entry", [{}])[0]
#         .get("changes", [{}])[0]
#         .get("value", {})
#         .get("messages", [{}])[0]
#     )
#     phone = message.get("from")
#     text = (message.get("text") or {}).get("body", "")
#     state = {"phone_number": phone, "current_message": text, "messages": [message], "documents": [], "voice_notes": []}
#     await graph.ainvoke(state)

#     # result = asyncio.run(graph.ainvoke(state))
#     return {"status": "ok"}



@router.post("")
async def whatsapp_webhook(request: Request):
    data = await request.json()

    messages = (
        data.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("messages", [])
    )

    state = {
        "phone_number": messages[0].get("from") if messages else None,
        "messages": messages,
        "current_message": "",
        "documents": [],
        "voice_notes": [],
        "media_ids": [],   # 🔥 important
    }

    text_parts = []

    for msg in messages:
        msg_type = msg.get("type")

        if msg_type == "text":
            text_parts.append(msg.get("text", {}).get("body", ""))

        elif msg_type in ("image", "document"):
            state["documents_id"].append(msg[msg_type]["id"])

        elif msg_type in ("audio", "voice"):
            state["voice_notes_id"].append(msg["audio"]["id"])

    state["current_message"] = "\n".join(text_parts)

    await graph.ainvoke(state)
    return {"status": "ok"}


