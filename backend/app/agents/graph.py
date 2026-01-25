from langgraph.graph import StateGraph, START, END
from app.agents.state import CaseState
from app.agents.nodes.consolidated_processor import consolidated_processor_node
from app.agents.nodes.compliance_check import check_compliance_node
from app.agents.nodes.followup_generator import generate_followup_node
from app.agents.nodes.save_case import save_case_node
from app.agents.nodes.send_response import send_response_node
from app.agents.nodes.doctor_verification import verify_doctor_node


def build_graph():
    """
    Optimized workflow that reduces API calls from 5-6 to 1-2 per request.
    
    Flow:
    1. Consolidated processor (1 API call for language, user type, extraction, triage)
    2. Compliance check (database lookup, no API call)
    3. Conditional: Follow-up generation (1 API call if needed) OR Save case
    4. Send response (WhatsApp API call)
    """
    workflow = StateGraph(CaseState)
    
    # Add nodes
    workflow.add_node("consolidated_processor", consolidated_processor_node)
    workflow.add_node("check_compliance", check_compliance_node)
    workflow.add_node("generate_followup", generate_followup_node)
    workflow.add_node("save_case", save_case_node)
    workflow.add_node("send_response", send_response_node)
    workflow.add_node("verify_doctor", verify_doctor_node)

    # Define workflow edges
    workflow.add_edge(START, "consolidated_processor")
    
    # Route based on user type (doctor verification or compliance check)
    workflow.add_conditional_edges(
        "consolidated_processor",
        lambda state: "doctor_path" if state.get("user_type") == "doctor" else "patient_path",
        {"patient_path": "check_compliance", "doctor_path": "verify_doctor"},
    )

    # After compliance check, decide if follow-up is needed
    workflow.add_conditional_edges(
        "check_compliance",
        lambda state: "followup" if state.get("requires_followup") else "complete",
        {"followup": "generate_followup", "complete": "save_case"},
    )

    # Both paths converge to send response
    workflow.add_edge("generate_followup", "send_response")
    workflow.add_edge("save_case", "send_response")
    workflow.add_edge("send_response", END)
    
    return workflow.compile()


graph = build_graph()
