import assemblyai as aai
import os


def run_voice_on_state(state: dict, file_path: str) -> dict:
    """
    Takes:
        state (CaseState)
        file_path (local audio)

    Updates:
        state["current_voice_data"]
    """

    aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY") 
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_path)

    text = transcript.text

    if transcript.status == aai.TranscriptStatus.error:
        print(f"Transcription failed: {transcript.error}")
        text = ""

    state["current_voice_data"] = {
        "transcript": text,
        "entities": {
            "raw_voice_text": text
        },
        "confidence": transcript.confidence if transcript.confidence else 0.0
    }

    return state
