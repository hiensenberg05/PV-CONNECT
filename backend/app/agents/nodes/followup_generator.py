# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# async def generate_followup_node(state: CaseState) -> CaseState:
#     model = get_model()
#     missing_fields = state.get("missing_fields") or ["details"]
#     missing = missing_fields[0]
#     language = state.get("language", "en")
#     prompt = f"""
#     Ask one friendly, short question in {language} to collect: {missing}.
#     Return plain text only.
#     """
#     response = model.generate_content(prompt)
#     state["next_question"] = response.text.strip()
#     return state


# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# FIELD_QUESTION_HINTS = {
#     "drug_name": "the name of the medicine",
#     "symptoms": "the symptoms you experienced",
#     "severity": "how severe the problem was (mild, moderate, or severe)",
#     "start_date": "when the symptoms started",
#     "dosage": "the dose you were taking",
#     "bill_or_prescription": "a photo of the prescription or bill"
# }


# async def generate_followup_node(state: CaseState) -> CaseState:
#     model = get_model()

#     missing_fields = state.get("missing_fields") or ["details"]
#     missing = missing_fields[0]

#     language = state.get("language", "en")

#     ask_for = FIELD_QUESTION_HINTS.get(missing, missing)

#     prompt = f"""
#         Ask ONE friendly, short question in {language} to collect {ask_for}.
#         If asking for a document, politely ask the user to upload it.
#         Return plain text only.
#         """

#     response = model.generate_content(prompt)

#     state["next_question"] = response.text.strip() if response and response.text else ""

#     return state

# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# FIELD_QUESTION_HINTS = {
#     "drug_name": "the name of the medicine",
#     "symptoms": "the symptoms you experienced",
#     "severity": "how severe the problem was (mild, moderate, or severe)",
#     "start_date": "when the symptoms started",
#     "dosage": "the dose you were taking",
# }


# async def generate_followup_node(state: CaseState) -> CaseState:
#     if state.get("next_question") is not None:
#         return state
#     missing_fields = state.get("missing_fields")

#     # ✅ NOTHING missing → do not ask anything
#     if not missing_fields:
#         state["next_question"] = None
#         return state

#     missing = missing_fields[0]
#     language = state.get("language", "en")

#     ask_for = FIELD_QUESTION_HINTS.get(missing, missing)

#     model = get_model()
#     prompt = f"""
#         Ask ONE friendly, short question in {language} to collect {ask_for}.
#         If asking for a document, politely ask the user to upload it.
#         Return plain text only.
#         """

#     response = model.generate_content(prompt)
#     state["next_question"] = response.text.strip() if response and response.text else None

#     return state


# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# FIELD_QUESTION_HINTS = {
#     "drug_name": "the name of the medicine",
#     "symptoms": "the symptoms you experienced",
#     "severity": "how severe the problem was (mild, moderate, or severe)",
#     "start_date": "when the symptoms started",
#     "dosage": "the dose you were taking",
# }


# async def generate_followup_node(state: CaseState) -> CaseState:
#     if state.get("next_question") is not None:
#         return state

#     missing_fields = state.get("missing_fields")

#     # ✅ NOTHING missing → do not ask anything
#     if not missing_fields:
#         state["next_question"] = None
#         return state

#     missing = missing_fields[0]
#     language = state.get("language", "en")

#     ask_for = FIELD_QUESTION_HINTS.get(missing, missing)

#     documents = state.get("documents")

#     model = get_model()


#     # ✅ ONLY mention bill if no document uploaded yet
#     if not documents:
#         prompt = f"""
#         Ask ONE friendly, short question in {language} to collect {ask_for}.
#         Also politely mention that if they have a prescription or medical bill, uploading it would be helpful.
#         Return plain text only.
#         """
#     else:
#         prompt = f"""
#         Ask ONE friendly, short question in {language} to collect {ask_for}.
#         Return plain text only.
#         """

#     response = model.generate_content(prompt)
#     state["next_question"] = response.text.strip() if response and response.text else None

#     return state



# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# FIELD_QUESTION_HINTS = {
#     "drug_name": "the name of the medicine",
#     "symptoms": "the symptoms you experienced",
#     "severity": "how severe the problem was (mild, moderate, or severe)",
#     "start_date": "when the symptoms started",
#     "dosage": "the dose you were taking",
# }


# async def generate_followup_node(state: CaseState) -> CaseState:
#     if state.get("next_question") is not None:
#         return state

#     missing_fields = state.get("missing_fields")

#     # ✅ NOTHING missing → do not ask anything
#     if not missing_fields:
#         state["next_question"] = None
#         return state

#     missing = missing_fields[0]
#     language = state.get("language", "en")
#     ask_for = FIELD_QUESTION_HINTS.get(missing, missing)

#     documents = state.get("documents")
#     extracted = state.get("extracted_data", {})
#     has_medi = extracted.get("has_medi")
#     medi_ans = state.get("medi_ans")

#     model = get_model()

#     # -------------------------------------------------
#     # WHEN NO DOCUMENT IS UPLOADED
#     # -------------------------------------------------
#     if not documents:

#         # Case 1: has_medi = False AND medi_ans is None
#         if has_medi is False and medi_ans is None:
#             state["next_question"] = (
#                 "No problem, you can tell me the details yourself."
#             )
#             state["medi_ans"] = 1
#             return state

#         # Case 2: has_medi is None → ask for prescription + normal question
#         if has_medi is None:
#             prompt = f"""
#             Ask ONE friendly, short question in {language} to collect {ask_for}.
#             Also politely mention that if they have a prescription or medical bill, uploading it would be helpful.
#             Return plain text only.
#             """
#         # Case 3: has_medi = False AND medi_ans is NOT None → normal question
#         else:
#             prompt = f"""
#             Ask ONE friendly, short question in {language} to collect {ask_for}.
#             Return plain text only.
#             """

#     # -------------------------------------------------
#     # DOCUMENT ALREADY UPLOADED → NORMAL QUESTION
#     # -------------------------------------------------
#     else:
#         prompt = f"""
#         Ask ONE friendly, short question in {language} to collect {ask_for}.
#         Return plain text only.
#         """

#     response = model.generate_content(prompt)
#     state["next_question"] = response.text.strip() if response and response.text else None

#     return state



from app.services.gemini_service import get_model
from app.agents.state import CaseState


FIELD_QUESTION_HINTS = {
    "drug_name": "the name of the medicine",
    "symptoms": "the symptoms you experienced",
    "severity": "how severe the problem was (mild, moderate, or severe)",
    "start_date": "when the symptoms started",
    "dosage": "the dose you were taking",
}


async def generate_followup_node(state: CaseState) -> CaseState:
    if state.get("next_question") is not None:
        return state

    missing_fields = state.get("missing_fields")

    # Nothing missing → ask nothing
    if not missing_fields:
        state["next_question"] = None
        return state

    missing = missing_fields[0]
    language = state.get("language", "en")
    ask_for = FIELD_QUESTION_HINTS.get(missing, missing)

    documents = state.get("documents")
    has_medi = state.get("has_medi_bill")   # False or None only
    medi_ans = state.get("medi_ans")       # latch

    model = get_model()
    print(has_medi)

    # -------------------------------------------------
    # DOCUMENT LOGIC (REALISTIC)
    # -------------------------------------------------
    if not documents:

        # User explicitly said NO document → acknowledge ONCE
        if has_medi is False and medi_ans is None:
            state["next_question"] = (
                "No problem, you can tell me the details yourself."
            )
            state["medi_ans"] = 1
            return state

        # Doc unknown AND not handled yet → ask + mention upload ONCE
        if has_medi is None and medi_ans is None:
            prompt = f"""
            Ask ONE friendly, short question in {language} to collect {ask_for}.
            Also politely mention that if they have a prescription or medical bill, uploading it would be helpful.
            Return plain text only.
            """
        else:
            # Doc topic already handled → normal question
            prompt = f"""
            Ask ONE friendly, short question in {language} to collect {ask_for}.
            Return plain text only.
            """

    # -------------------------------------------------
    # DOCUMENT UPLOADED → NORMAL QUESTION
    # -------------------------------------------------
    else:
        prompt = f"""
        Ask ONE friendly, short question in {language} to collect {ask_for}.
        Return plain text only.
        """

    response = model.generate_content(prompt)
    state["next_question"] = response.text.strip() if response and response.text else None

    return state
