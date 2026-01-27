from fastapi import APIRouter, UploadFile, Form
from app.agents.graph import build_graph

router = APIRouter()
graph = build_graph()

@router.post("/chat")
async def chat(
    text: str = Form(None),
    file: UploadFile = None,
):
    phone_number = "919876543210"  # dummy number for testing

    messages = []
    documents = []
    voice_notes = []

    if text:
        messages.append({
            "from": phone_number,
            "text": {"body": text},
            "type": "text"
        })

    if file:
        documents.append({
            "filename": file.filename,
            "content_type": file.content_type
        })

    state = {
        "phone_number": phone_number,
        "current_message": text,
        "messages": messages,
        "documents": documents,
        "voice_notes": voice_notes,
    }

    result = await graph.ainvoke(state)

    return {
    "reply": result.get("next_question")
   }

