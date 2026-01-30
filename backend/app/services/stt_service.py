import assemblyai as aai
import os
from dotenv import load_dotenv
load_dotenv()  # reads .env in cwd or project root


def transcribe_audio(file_bytes: bytes) -> str:
    """
    Transcribe audio bytes using AssemblyAI.
    Returns the transcript text.
    """
    try:
        # Support both env var names (some libraries expect ASSEMBLYAI_API_KEY)
        api_key = os.getenv("ASSEMBLYAI_API_KEY") or os.getenv("ASSEMBLY_API_KEY")
        if not api_key:
            print("STT Warning: No AssemblyAI API key found in ASSEMBLYAI_API_KEY or ASSEMBLY_API_KEY. Skipping transcription.")
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
