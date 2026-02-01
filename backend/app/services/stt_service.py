import assemblyai as aai

# Import centralized settings (handles .env loading)
from app.config import settings


def transcribe_audio(file_bytes: bytes) -> str:
    """
    Transcribe audio bytes using AssemblyAI.
    Returns the transcript text.
    """
    try:
        api_key = settings.ASSEMBLY_API_KEY
        if not api_key:
            print("STT Warning: No AssemblyAI API key found. Skipping transcription.")
            return ""

        aai.settings.api_key = api_key
        transcriber = aai.Transcriber()
        # Upload buffer directly
        upload_url = transcriber.upload_file(file_bytes)
        transcript = transcriber.transcribe(upload_url)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"Transcription failed: {transcript.error}")
            return ""

        return transcript.text
    except Exception as e:
        print(f"STT Error: {e}")
        return ""

def run_voice_on_state(state: dict, file_path: str) -> dict:
    """
    Legacy function for state-based processing from local file.
    """
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    text = transcribe_audio(file_bytes)

    state["current_voice_data"] = {
        "transcript": text,
        "entities": {
            "raw_voice_text": text
        },
        "confidence": 0.9 if text else 0.0
    }

    return state
