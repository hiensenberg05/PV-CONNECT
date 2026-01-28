from pydantic import BaseModel, Field
from typing import Dict, Any

class WorkflowAction(BaseModel):
    """
    Represents a side-effect action emitted by the workflow engine.
    The engine never executes these; it only describes them.
    External services (Partner's responsibility) must listen and execute.
    """
    action_type: str  # e.g., "CALL_OCR", "CALL_STT", "SAVE_STATE", "GENERATE_CASE_ID"
    payload: Dict[str, Any] = Field(default_factory=dict)
