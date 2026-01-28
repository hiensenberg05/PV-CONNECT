from fastapi import APIRouter
from typing import Dict
from uuid import uuid4
from app.schemas.message import MessageIn, MessageOut
from app.schemas.conversation_state import ConversationState
from app.workflows.router import route_message

router = APIRouter()

# DUMMY IN-MEMORY STORE FOR TESTING
SESSIONS: Dict[str, ConversationState] = {}

@router.post("/webhook", response_model=MessageOut)
async def whatsapp_webhook(message: MessageIn):
    """
    Simulate WhatsApp webhook entry point.
    """
    # 1. Retrieve State
    state = SESSIONS.get(message.phone_number)
    
    # 2. Route Message (Passing None triggers auto-init in router)
    response, actions, new_state = route_message(message, state)
    
    # 3. MOCK SERVICE EXECUTION (Glue Code)
    # In production, these actions go to a queue.
    # Here, we execute critical ones immediately to allow the flow to proceed.
    
    for action in actions:
        print(f"Action Emitted: {action.action_type} Payload: {action.payload}")
        
        if action.action_type == "GENERATE_CASE_ID":
            # Mock Case ID generation
            if not new_state.case_id:
                new_state.case_id = uuid4()
                print(f"DEBUG: Generated Case ID {new_state.case_id}")
        
        elif action.action_type == "SAVE_STATE":
            # State is saved at the end of this function anyway
            pass
            
    # 4. Save State
    SESSIONS[message.phone_number] = new_state
    
    return response
