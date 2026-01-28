from typing import Optional, List
from datetime import datetime

from app.schemas.conversation_state import ConversationState, FieldStatus
from app.workflows.field_registry import FIELD_REGISTRY


class QuestionManager:
    """
    Determines:
    - what question to ask next
    - what fields are already answered
    - what can be skipped
    - what is still missing

    This class contains NO AI logic.
    """

    def __init__(self, state: ConversationState):
        self.state = state

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def get_next_question(self) -> Optional[str]:
        """
        Returns the next field_name to ask, or None if complete.
        """

        # 1️⃣ Ask from pending queue first (highest priority)
        if self.state.pending_questions:
            return self.state.pending_questions.pop(0)

        # 2️⃣ Scan fields in PvPI order (section 1 → 7)
        for field_name, meta in FIELD_REGISTRY.items():

            # Skip if already answered
            if self._is_answered(field_name):
                continue

            # Skip if dependency not satisfied
            if not self._dependency_satisfied(meta):
                continue

            # Skip if extractable from OCR and OCR already processed
            if meta.extractable_from_ocr and self._ocr_already_processed(field_name):
                continue

            # Required field → ask immediately
            if meta.required:
                self._mark_field_asked(field_name)
                return field_name

        # 3️⃣ No required fields left → optional follow-ups
        for field_name, meta in FIELD_REGISTRY.items():
            if self._is_answered(field_name):
                continue
            if not self._dependency_satisfied(meta):
                continue

            self._mark_field_asked(field_name)
            return field_name

        # 4️⃣ Everything done
        return None

    # --------------------------------------------------
    # STATE UPDATE METHODS
    # --------------------------------------------------

    def mark_field_answered(
        self,
        field_name: str,
        value,
        source: str,
    ):
        """
        Marks a field as answered and stores value.
        """

        status = self.state.field_status.get(
            field_name,
            FieldStatus(field_name=field_name)
        )

        status.answered = True
        status.value = value
        status.source = source

        self.state.field_status[field_name] = status
        self._recalculate_missing_fields()

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------

    def _is_answered(self, field_name: str) -> bool:
        status = self.state.field_status.get(field_name)
        return status is not None and status.answered is True

    def _mark_field_asked(self, field_name: str):
        status = self.state.field_status.get(
            field_name,
            FieldStatus(field_name=field_name)
        )

        status.asked = True
        status.ask_count += 1
        status.last_asked_at = datetime.utcnow()

        self.state.field_status[field_name] = status

    def _dependency_satisfied(self, meta) -> bool:
        if not meta.depends_on:
            return True

        dep_status = self.state.field_status.get(meta.depends_on)
        if not dep_status or not dep_status.answered:
            return False

        if meta.depends_on_value is None:
            return True

        return dep_status.value == meta.depends_on_value

    def _ocr_already_processed(self, field_name: str) -> bool:
        """
        Skip asking OCR-extractable fields if value already exists.
        """
        return field_name in self.state.extracted_data

    def _recalculate_missing_fields(self):
        """
        Recalculate list of missing required fields.
        """
        missing = []

        for field_name, meta in FIELD_REGISTRY.items():
            if meta.required and not self._is_answered(field_name):
                missing.append(field_name)

        self.state.missing_fields = missing
