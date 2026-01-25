import asyncio
import logging
import json
import sys
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(r"d:\nova\backend")

from app.state import create_initial_state
# Mock config BEFORE importing graph
with patch("app.config.settings.GEMINI_API_KEY", "mock_key"):
    from app.graph import patient_intake_node

logging.basicConfig(level=logging.INFO)

async def test_prompt_injection():
    print("\n--- Testing Prompt Context Injection ---")
    
    # Mock state with some extracted data and missing fields
    state = create_initial_state("+1234567890", "I have a headache")
    state["extracted_data"] = {"drug_name": "Metformin", "drug_dosage": "500mg"}
    state["missing_fields"] = ["timeline"]
    state["messages"] = [{"role": "user", "content": "I have a headache"}]
    
    # Mock LLM service
    with patch("app.services.llm_service.gemini_service.generate_text") as mock_generate:
        mock_generate.return_value = "Response from LLM"
        
        # Run node
        await patient_intake_node(state)
        
        # Verify the call arguments
        call_args = mock_generate.call_args
        kwargs = call_args.kwargs
        system_instruction = kwargs.get("system_instruction", "")
        
        print(f"Call prompted with system instruction length: {len(system_instruction)}")
        
        # Check if extracted data was injected
        assert "Metformin" in system_instruction
        assert "500mg" in system_instruction
        assert "timeline" in system_instruction
        
        print("✅ Prompt contains injected context!")
        print("System Instruction Snippet:")
        print(system_instruction[350:600]) # Print the relevant part

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_prompt_injection())
