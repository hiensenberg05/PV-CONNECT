
def sanitize_logic(new_data):
    current_data = {}
    for key, value in new_data.items():
        # Sanitize "null" strings
        if isinstance(value, str) and value.lower().strip() == "null":
            value = None
        
        if value is not None:
            if key == "patient_age":
                # Attempt to parse age as int
                if isinstance(value, int):
                    current_data[key] = value
                elif isinstance(value, str):
                    # Extract first number found
                    import re
                    match = re.search(r'\d+', value)
                    if match:
                        current_data[key] = int(match.group())
                    else:
                        current_data[key] = None 
                        
            elif key == "patient_gender":
                # Normalize gender
                if isinstance(value, str):
                    val_lower = value.lower().strip()
                    if val_lower in ["male", "female", "other"]:
                        current_data[key] = val_lower
                    else:
                        current_data[key] = None
            else:
                current_data[key] = value
    return current_data

def test():
    print("Testing Sanitization...")
    input_data = {
        "drug_name": "Dolo",
        "patient_age": "null",
        "patient_gender": "null",
        "timeline": "3 days"
    }
    
    output = sanitize_logic(input_data)
    print(f"Output: {output}")
    
    assert output.get("drug_name") == "Dolo"
    assert "patient_age" not in output or output["patient_age"] is None
    assert "patient_gender" not in output or output["patient_gender"] is None
    
    print("✅ Sanitization Logic Passed")

if __name__ == "__main__":
    test()
