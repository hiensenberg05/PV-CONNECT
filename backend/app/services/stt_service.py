from services.llm_service import get_model


def run_voice_on_state(state: dict, file_path: str) -> dict:
    """
    Takes:
        state (CaseState)
        file_path (local audio)

    Updates:
        state["current_voice_data"]
    """

    client, model = get_model("whisper-large-v3")

    with open(file_path, "rb") as audio:
        transcription = client.audio.transcriptions.create(
            file=audio,
            model=model
        )

    text = transcription.text.strip()

    state["current_voice_data"] = {
        "transcript": text,
        "entities": {
            "raw_voice_text": text
        },
        "confidence": 0.9 if len(text) > 10 else 0.2
    }

    return state
