FILL_MISSING_SYSTEM_PROMPT = (
    "You are a Pharmacovigilance Information Extraction Assistant.\n\n"
    "Your task is to extract missing information from a given text.\n\n"
    "You will be provided with:\n"
    "- A user message text\n"
    "- A list of missing field names\n"
    "- Already extracted data\n\n"
    "Rules:\n"
    "1. Extract values ONLY for the fields listed as missing.\n"
    "2. Use ONLY the provided user text. Do NOT guess or infer.\n"
    "3. If a value is not clearly present, do NOT include it.\n"
    "4. Do NOT repeat fields that already exist in extracted data.\n"
    "5. Do NOT add extra fields.\n\n"
    "Output format (STRICT):\n"
    "- Return a valid JSON object only.\n"
    "- Keys must exactly match the missing field names.\n"
    "- Values must be strings.\n"
    "- If nothing can be extracted, return an empty JSON object: {}\n"
)


from services.llm_service import get_model
import json

def fill_data_remove_missing(state: dict) -> dict:
    to_use = state.get("to_use", "")
    missing = state.get("missing", [])
    extracted_data = state.get("extracted_data", {})

    # nothing to do
    if not to_use or not missing:
        return state

    client, model = get_model()

    messages = [
        {
            "role": "system",
            "content": FILL_MISSING_SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": f"Missing fields:\n{missing}"
        },
        {
            "role": "system",
            "content": f"Already extracted data:\n{extracted_data}"
        },
        {
            "role": "user",
            "content": to_use
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        new_data = json.loads(raw_output)
    except Exception:
        # model misbehaved → do nothing
        return state

    # update extracted_data
    for key, value in new_data.items():
        if key in missing and value:
            extracted_data[key] = value
            missing.remove(key)

    state["extracted_data"] = extracted_data
    state["missing"] = missing

    return state
