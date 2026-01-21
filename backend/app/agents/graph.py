from langgraph.graph import StateGraph, START, END
from app.agents.state import CaseState
from app.agents.nodes.language_detection import detect_language_node
from app.agents.nodes.detect_user_type import detect_user_type_node
from app.agents.nodes.nlp_extraction import extract_data_node
from app.agents.nodes.compliance_check import check_compliance_node
from app.agents.nodes.followup_generator import generate_followup_node
from app.agents.nodes.save_case import save_case_node
from app.agents.nodes.send_response import send_response_node
from app.agents.nodes.doctor_verification import verify_doctor_node
from app.agents.nodes.clinical_triage import triage_case_node


def build_graph():
    workflow = StateGraph(CaseState)
    workflow.add_node("detect_language", detect_language_node)
    workflow.add_node("detect_user_type", detect_user_type_node)
    workflow.add_node("extract_data", extract_data_node)
    workflow.add_node("check_compliance", check_compliance_node)
    workflow.add_node("generate_followup", generate_followup_node)
    workflow.add_node("triage_case", triage_case_node)
    workflow.add_node("save_case", save_case_node)
    workflow.add_node("send_response", send_response_node)
    workflow.add_node("verify_doctor", verify_doctor_node)

    workflow.add_edge(START, "detect_language")
    workflow.add_edge("detect_language", "detect_user_type")

    workflow.add_conditional_edges(
        "detect_user_type",
        lambda state: "doctor_path" if state.get("user_type") == "doctor" else "patient_path",
        {"patient_path": "extract_data", "doctor_path": "verify_doctor"},
    )

    workflow.add_edge("extract_data", "check_compliance")
    workflow.add_edge("check_compliance", "triage_case")
    workflow.add_conditional_edges(
        "triage_case",
        lambda state: "followup" if state.get("requires_followup") else "complete",
        {"followup": "generate_followup", "complete": "save_case"},
    )

    workflow.add_edge("generate_followup", "send_response")
    workflow.add_edge("save_case", "send_response")
    workflow.add_edge("send_response", END)
    return workflow.compile()


graph = build_graph()
