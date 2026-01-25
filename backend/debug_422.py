import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/message"

def test_payload(name, payload):
    print(f"\n--- Testing: {name} ---")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 422:
            print(f"Error Body: {response.text}")
        else:
            print("Success")
    except Exception as e:
        print(f"Request failed: {e}")

# 1. Standard valid payload
test_payload("Valid Input", {
    "message": "Hello",
    "sender_phone": "+1234567890",
    "case_id": None
})

# 2. Empty string case_id
test_payload("Empty String Case ID", {
    "message": "Hello",
    "sender_phone": "+1234567890",
    "case_id": ""
})

# 3. Missing case_id (should be optional)
test_payload("Missing Case ID", {
    "message": "Hello",
    "sender_phone": "+1234567890"
})

# 4. Null message (Invalid?)
test_payload("Null Message", {
    "message": None,
    "sender_phone": "+1234567890"
})

# 5. Missing message
test_payload("Missing Message", {
    "sender_phone": "+1234567890"
})

# 6. Invalid Attachments
test_payload("Invalid Attachments", {
    "message": "Hello",
    "sender_phone": "+1234567890",
    "attachments": "not a list"
})
