# backend/app/workflows/patient/engine.py

from typing import List, Dict, Any, Tuple  # ✅ Added Tuple

from app.schemas.message import MessageIn, MessageOut
from app.schemas.conversation_state import ConversationState
from app.schemas.workflow_action import WorkflowAction
from app.workflows.questionmanager import QuestionManager  # ✅ Fixed: removed underscore
from app.workflows.field_registry import FIELD_REGISTRY


# ============================================================
# HELPER – APPLY EXTRACTION RESULTS INTO STATE
# ============================================================

def apply_extraction_results(
    state: ConversationState,
    extracted_data: Dict[str, Any],
    source: str
):
    """
    Merge AI / OCR / STT extracted data into conversation state.
    This function NEVER decides workflow flow.
    """

    qm = QuestionManager(state)

    for field_name, value in extracted_data.items():
        if value is None:
            continue

        qm.mark_field_answered(
            field_name=field_name,
            value=value,
            source=source
        )

        state.extracted_data[field_name] = value


# ============================================================
# MAIN PATIENT WORKFLOW ENGINE
# ============================================================

def run_patient_workflow(
    message: MessageIn,
    state: ConversationState
) -> Tuple[MessageOut, List[WorkflowAction], ConversationState]:  # ✅ Fixed return type
    """
    Main patient workflow engine.

    This function is called on EVERY incoming WhatsApp message.
    It is fully deterministic and side-effect free.
    """

    actions: List[WorkflowAction] = []

    # --------------------------------------------------
    # STEP 0 – UPDATE PER-TURN STATE
    # --------------------------------------------------
    state.current_message = message.text_content
    state.last_updated = message.timestamp

    # Reset per-turn flags
    state.document_current_uploaded = False
    state.voice_current_uploaded = False

    # --------------------------------------------------
    # STEP 1 – MEDIA HANDLING (ASYNC)
    # --------------------------------------------------
    if message.message_type == "document":
        state.document_current_uploaded = True

        actions.append(
            WorkflowAction(
                action_type="CALL_OCR",
                payload={
                    "media_id": message.document_media_id,
                    "filename": message.document_filename,
                }
            )
        )

    if message.message_type == "audio":
        state.voice_current_uploaded = True

        actions.append(
            WorkflowAction(
                action_type="CALL_STT",
                payload={
                    "media_id": message.audio_media_id,
                }
            )
        )

    # --------------------------------------------------
    # STEP 2 – LANGUAGE DETECTION (SAFE EVERY TURN)
    # --------------------------------------------------
    if state.current_message:
        actions.append(
            WorkflowAction(
                action_type="DETECT_LANGUAGE",
                payload={"text": state.current_message}
            )
        )

    # --------------------------------------------------
    # STEP 3 – APPLY ASYNC EXTRACTION RESULTS (REACTIVE)
    # --------------------------------------------------
    if state.current_doc_data:
        apply_extraction_results(
            state=state,
            extracted_data=state.current_doc_data,
            source="ocr"
        )
        state.current_doc_data = None

    if state.current_voice_data:
        apply_extraction_results(
            state=state,
            extracted_data={"free_text": state.current_voice_data},
            source="user_voice"
        )
        state.current_voice_data = None

    # --------------------------------------------------
    # STEP 4 – INIT STAGE
    # --------------------------------------------------
    if state.workflow_stage == "INIT":
        state.workflow_stage = "COLLECTING"

        actions.append(
            WorkflowAction(
                action_type="GENERATE_CASE_ID",
                payload={}
            )
        )

        actions.append(
            WorkflowAction(
                action_type="SAVE_STATE",
                payload={}
            )
        )

        return (  # ✅ Now returns tuple
            MessageOut(
                text="Hello! I'm here to help you report a medical side effect. Please tell me what happened.",
                requires_input=True,
                show_file_upload=True,
                language=state.language,
            ),
            actions,
            state
        )

    # --------------------------------------------------
    # STEP 5 – COLLECTING STAGE (MAIN LOOP)
    # --------------------------------------------------
    if state.workflow_stage == "COLLECTING":
        qm = QuestionManager(state)

        # Attempt AI extraction from free text (non-blocking)
        if state.current_message:
            actions.append(
                WorkflowAction(
                    action_type="CALL_AI_EXTRACT",
                    payload={
                        "text": state.current_message,
                        "expected_fields": list(FIELD_REGISTRY.keys())
                    }
                )
            )

        # Decide next question
        next_field = qm.get_next_question()

        if next_field:
            field_meta = FIELD_REGISTRY[next_field]

            # Language-aware question
            question_text = field_meta.question_en
            if state.language != "en" and field_meta.question_hi:
                question_text = field_meta.question_hi

            actions.append(
                WorkflowAction(
                    action_type="SAVE_STATE",
                    payload={}
                )
            )

            return (  # ✅ Now returns tuple
                MessageOut(
                    text=question_text,
                    requires_input=True,
                    show_file_upload=True,
                    language=state.language,
                ),
                actions,
                state
            )

        # --------------------------------------------------
        # ALL REQUIRED FIELDS COLLECTED
        # --------------------------------------------------
        state.workflow_stage = "COMPLETE"

        actions.append(
            WorkflowAction(
                action_type="SAVE_STATE",
                payload={}
            )
        )

        return (  # ✅ Now returns tuple
            MessageOut(
                text=(
                    "Thank you. All required information has been collected.\n\n"
                    f"Your case ID is {state.case_id}.\n"
                    "You may share this with your doctor if needed."
                ),
                requires_input=False,
                show_file_upload=False,
                language=state.language,
            ),
            actions,
            state
        )

    # --------------------------------------------------
    # STEP 6 – COMPLETE STAGE (IDEMPOTENT)
    # --------------------------------------------------
    return (  # ✅ Now returns tuple
        MessageOut(
            text="This report is already complete. Thank you for your time.",
            requires_input=False,
            show_file_upload=False,
            language=state.language,
        ),
        actions,
        state
    )