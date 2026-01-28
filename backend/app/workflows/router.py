from typing import Tuple, List, Optional
from app.schemas.message import MessageIn, MessageOut
from app.schemas.conversation_state import ConversationState
from app.schemas.workflow_action import WorkflowAction
from app.workflows.patient.engine import run_patient_workflow
from app.workflows.doctor.engine import run_doctor_workflow


def route_message(
    message: MessageIn,
    state: Optional[ConversationState]
) -> Tuple[MessageOut, List[WorkflowAction], ConversationState]:
    """Main router"""
    
    if state is None:
        user_type = message.metadata.get("user_type", "patient")
        state = ConversationState(
            user_type=user_type,
            phone_number=message.phone_number,
            workflow_stage="INIT",
            language="en"
        )
    
    if state.user_type == "patient":
        return run_patient_workflow(message, state)
    elif state.user_type == "doctor":
        return run_doctor_workflow(message, state)
    else:
        raise ValueError(f"Unknown user_type: {state.user_type}")