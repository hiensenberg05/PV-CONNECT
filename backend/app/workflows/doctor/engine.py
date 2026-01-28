# backend/app/workflows/doctor/engine.py

from typing import List, Tuple
from app.schemas.message import MessageIn, MessageOut
from app.schemas.conversation_state import ConversationState
from app.schemas.workflow_action import WorkflowAction


def run_doctor_workflow(
    message: MessageIn,
    state: ConversationState
) -> Tuple[MessageOut, List[WorkflowAction], ConversationState]:
    """
    Doctor workflow engine.

    Stages:
    INIT → VERIFY → COLLECTING → COMPLETE
    """

    actions: List[WorkflowAction] = []

    # --------------------------------------------------
    # STEP 0 — UPDATE PER-TURN STATE
    # --------------------------------------------------
    state.current_message = message.text_content
    state.last_updated = message.timestamp

    # --------------------------------------------------
    # STEP 1 — INIT
    # --------------------------------------------------
    if state.workflow_stage == "INIT":
        state.workflow_stage = "VERIFY"

        actions.append(
            WorkflowAction(
                action_type="VERIFY_DOCTOR",
                payload={"phone_number": state.phone_number}
            )
        )

        actions.append(
            WorkflowAction(
                action_type="SAVE_STATE",
                payload={}
            )
        )

        return (
            MessageOut(
                text=(
                    "Welcome Doctor.\n\n"
                    "Please share your medical license number or a patient case ID."
                ),
                requires_input=True,
                show_file_upload=True,
                language=state.language,
            ),
            actions,
            state
        )

    # --------------------------------------------------
    # STEP 2 — VERIFY
    # --------------------------------------------------
    if state.workflow_stage == "VERIFY":

        # Doctor already verified (from DB async)
        if state.doctor_verified:
            state.workflow_stage = "COLLECTING"

            actions.append(
                WorkflowAction(
                    action_type="SAVE_STATE",
                    payload={}
                )
            )

            return (
                MessageOut(
                    text="Thank you. You are verified. Please continue.",
                    requires_input=True,
                    show_file_upload=False,
                    language=state.language,
                ),
                actions,
                state
            )

        # Waiting for license verification
        if state.awaiting_license:
            return (
                MessageOut(
                    text=(
                        "Your license verification is in progress.\n"
                        "You may continue providing case details meanwhile."
                    ),
                    requires_input=True,
                    show_file_upload=True,
                    language=state.language,
                ),
                actions,
                state
            )

        # License / case ID provided
        if state.current_message:
            actions.append(
                WorkflowAction(
                    action_type="REQUEST_LICENSE",
                    payload={"license_or_case_id": state.current_message}
                )
            )

            state.awaiting_license = True

            actions.append(
                WorkflowAction(
                    action_type="SAVE_STATE",
                    payload={}
                )
            )

            return (
                MessageOut(
                    text="Thank you. Verifying your details. You may continue.",
                    requires_input=True,
                    show_file_upload=True,
                    language=state.language,
                ),
                actions,
                state
            )

    # --------------------------------------------------
    # STEP 3 — COLLECTING (MINIMAL FOR NOW)
    # --------------------------------------------------
    if state.workflow_stage == "COLLECTING":
        
        # Extract any medical notes from current message
        if state.current_message:
            actions.append(
                WorkflowAction(
                    action_type="CALL_AI_EXTRACT",
                    payload={
                        "text": state.current_message,
                        "extract_type": "doctor_notes"
                    }
                )
            )
        
        actions.append(
            WorkflowAction(
                action_type="SAVE_STATE",
                payload={}
            )
        )
        
        return (
            MessageOut(
                text=(
                    "Please provide any additional clinical information "
                    "you would like to add to this case."
                ),
                requires_input=True,
                show_file_upload=True,
                language=state.language,
            ),
            actions,
            state
        )

    # --------------------------------------------------
    # STEP 4 — COMPLETE
    # --------------------------------------------------
    actions.append(
        WorkflowAction(
            action_type="GENERATE_CASE_ID",
            payload={"extracted_data": state.extracted_data}
        )
    )
    
    return (
        MessageOut(
            text="Thank you Doctor. The case has been updated successfully.",
            requires_input=False,
            show_file_upload=False,
            language=state.language,
        ),
        actions,
        state
    )