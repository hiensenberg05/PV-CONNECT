"""
Workflows package for PV-CONNECT.

This package contains:
- Field registry (static PvPI field definitions)
- Question manager (decides what to ask next)
- Patient and doctor workflow engines
- Router to select appropriate workflow

IMPORTANT:
This package contains ONLY workflow logic.
No AI calls, no DB calls, no WhatsApp logic.
"""

from .field_registry import FIELD_REGISTRY, FieldMeta
from .question_manager import QuestionManager

__all__ = [
    "FIELD_REGISTRY",
    "FieldMeta",
    "QuestionManager",
]
