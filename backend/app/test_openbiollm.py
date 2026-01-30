"""
Test BioMistral-7B connectivity via HuggingFace Inference API
"""
import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HUGGING_FACE_TOKEN", "")
MODEL_ID = "BioMistral/BioMistral-7B"

print("=" * 60)
print("BioMistral-7B Connectivity Test")
print("=" * 60)

if not HF_TOKEN or "your_" in HF_TOKEN.lower():
    print("❌ ERROR: HUGGING_FACE_TOKEN not set in .env")
    exit(1)

print(f"✓ Token: {HF_TOKEN[:10]}...{HF_TOKEN[-4:]}")
print(f"✓ Model: {MODEL_ID}")

try:
    from huggingface_hub import InferenceClient
    
    print("\n" + "-" * 60)
    print("Connecting to BioMistral-7B...")
    print("-" * 60)
    
    client = InferenceClient(token=HF_TOKEN)
    
    test_prompt = """You are a pharmacovigilance expert. Extract the adverse event from this case report.

Case: A 45 year old female patient started taking Metformin 500mg twice daily for type 2 diabetes. 
After 30 minutes of the first dose, she experienced severe nausea and vomiting. 
She stopped the medication and symptoms resolved within 2 hours.

Extract in JSON format:
{
  "drug": "drug name",
  "adverse_event": "event description", 
  "severity": "mild/moderate/severe",
  "outcome": "resolved/ongoing/unknown"
}

Response:"""
    
    print("\nSending request...")
    
    response = client.text_generation(
        model=MODEL_ID,
        prompt=test_prompt,
        max_new_tokens=150,
        temperature=0.1
    )
    
    print("\n✅ SUCCESS! BioMistral-7B responded:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    print("\n✅ BioMistral-7B is working correctly!")
    print("\nYou can now proceed with WhatsApp integration.")
    
except Exception as e:
    error_msg = str(e)
    print(f"\n❌ Error: {error_msg}")
    
    if "loading" in error_msg.lower():
        print("\n⏳ Model is loading. Wait 1-2 minutes and try again.")
    elif "401" in error_msg or "auth" in error_msg.lower():
        print("\n   Check your HuggingFace token is valid.")
    elif "403" in error_msg:
        print("\n   Token needs 'Inference' permission.")
        print("   Go to: https://huggingface.co/settings/tokens")

print("\n" + "=" * 60)
