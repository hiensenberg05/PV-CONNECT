from langgraph.graph import StateGraph, START, END
from app.agents.state import GraphState
from app.agents.nodes.language_detection import detect_language_node
from app.agents.nodes.detect_user_type import detect_user_type_node
from app.agents.nodes.nlp_extraction import extract_data_node
from app.agents.nodes.compliance_check import check_compliance_node
from app.agents.nodes.clinical_triage import triage_case_node
from app.agents.nodes.followup_generator import generate_followup_node
from app.agents.nodes.save_case import save_case_node
from app.agents.nodes.send_response import send_response_node
from app.agents.nodes.doctor_verification import verify_doctor_node
from app.agents.nodes.ocr_processing import process_image_node
from app.agents.nodes.voice_processing import process_voice_node
import logging

logger = logging.getLogger(__name__)


def route_after_user_type(state: GraphState) -> str:
    """Route after user type detection - handles both user type and media type"""
    user_type = state.get("user_type", "patient")
    
    if user_type == "doctor":
        return "verify_doctor"
    
    # Patient path - check media type
    if state.get("has_image") or state.get("message_type") == "image":
        return "process_image"
    elif state.get("has_voice") or state.get("message_type") == "audio":
        return "process_voice"
    else:
        return "nlp_extraction"


def route_completeness(state: GraphState) -> str:
    """Route based on data completeness"""
    is_complete = state.get("is_complete", False)
    return "complete" if is_complete else "incomplete"


def route_doctor_verification(state: GraphState) -> str:
    """Route after doctor verification"""
    is_verified = state.get("doctor_verified", False)
    
    if is_verified:
        # Verified doctor - can provide medical opinion
        return "save_case"  # For now, go straight to save
        # TODO: Add medical opinion collection node in future
    else:
        # Not verified - need license or waiting for verification
        return "save_case"  # Still save the request for tracking


def create_graph():
    """Create and compile LangGraph workflow"""
    workflow = StateGraph(GraphState)
    
    # Add all nodes
    workflow.add_node("detect_language", detect_language_node)
    workflow.add_node("detect_user_type", detect_user_type_node)
    workflow.add_node("process_image", process_image_node)
    workflow.add_node("process_voice", process_voice_node)
    workflow.add_node("nlp_extraction", extract_data_node)
    workflow.add_node("compliance_check", check_compliance_node)
    workflow.add_node("clinical_triage", triage_case_node)
    workflow.add_node("followup_generator", generate_followup_node)
    workflow.add_node("save_case", save_case_node)
    workflow.add_node("send_response", send_response_node)
    workflow.add_node("verify_doctor", verify_doctor_node)
    
    # Define entry point
    workflow.set_entry_point("detect_language")
    
    # Sequential edges
    workflow.add_edge("detect_language", "detect_user_type")
    
    # Conditional: route based on user type AND media type
    workflow.add_conditional_edges(
        "detect_user_type",
        route_after_user_type,
        {
            "verify_doctor": "verify_doctor",
            "process_image": "process_image",
            "process_voice": "process_voice",
            "nlp_extraction": "nlp_extraction"
        }
    )
    
    # Media processing converges to compliance check (OCR/voice already extracted data)
    workflow.add_edge("process_image", "compliance_check")
    workflow.add_edge("process_voice", "compliance_check")
    
    # Text path goes through NLP extraction first
    workflow.add_edge("nlp_extraction", "compliance_check")
    
    # All paths converge to compliance check
    workflow.add_edge("compliance_check", "clinical_triage")
    
    # Conditional: complete vs incomplete
    workflow.add_conditional_edges(
        "clinical_triage",
        route_completeness,
        {
            "complete": "save_case",
            "incomplete": "followup_generator"
        }
    )
    
    # Both paths converge to save_case
    workflow.add_edge("followup_generator", "save_case")
    workflow.add_edge("save_case", "send_response")
    workflow.add_edge("send_response", END)
    
    # Doctor path - now with conditional routing
    workflow.add_conditional_edges(
        "verify_doctor",
        route_doctor_verification,
        {
            "save_case": "save_case"
        }
    )
    
    return workflow.compile()


# Create graph instance
graph = create_graph()
