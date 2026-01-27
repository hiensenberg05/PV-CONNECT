# from app.services.gemini_service import get_model
# from app.agents.state import CaseState


# async def detect_language_node(state: CaseState) -> CaseState:
#     model = get_model()
#     text = state.get("current_message", "")
#     prompt = f'Detect ISO language code only for: "{text}". Return JSON {{"language": "en"}}'
#     response = model.generate_content(prompt)
#     state["language"] = response.text.strip().lower()[:2] or "en"
#     return state


import re
from app.agents.state import CaseState

SCRIPT_MAP = {
    "hi": re.compile(r"[\u0900-\u0963\u0966-\u097F]"),  # Hindi (exclude danda)
    "bn": re.compile(r"[\u0980-\u09FF]"),               # Bengali
    "ta": re.compile(r"[\u0B80-\u0BFF]"),               # Tamil
    "te": re.compile(r"[\u0C00-\u0C7F]"),               # Telugu
    "ur": re.compile(r"[\u0600-\u06FF]"),               # Urdu
}


async def detect_language_node(state: CaseState) -> CaseState:
    if state.get("language"):
        return state  # Already detected
    text = state.get("current_message")

    if not text:
        msgs = state.get("messages", [])
        if msgs:
            text = msgs[-1].get("text", {}).get("body", "")
        else:
            return state

    text = str(text)

    scores = {}

    for lang, regex in SCRIPT_MAP.items():
        matches = regex.findall(text)
        scores[lang] = len(matches)

    # Debug (keep once if needed)
    print("LANG SCORES:", scores)

    # Pick language with highest count
    detected_lang = max(scores, key=scores.get)

    # If nothing meaningful matched → English
    if scores[detected_lang] == 0:
        state["language"] = "en"
    else:
        state["language"] = detected_lang

    return state
