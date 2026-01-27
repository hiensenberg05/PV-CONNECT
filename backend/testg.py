# import os
# import requests
# from dotenv import load_dotenv

# # ✅ Load .env file
# load_dotenv()

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     raise RuntimeError("GROQ_API_KEY environment variable not set")

# URL = "https://api.groq.com/openai/v1/models"

# headers = {
#     "Authorization": f"Bearer {GROQ_API_KEY}",
#     "Content-Type": "application/json",
# }

# response = requests.get(URL, headers=headers, timeout=30)
# response.raise_for_status()

# data = response.json()

# print("\n✅ Models available for your Groq API key:\n")

# for model in data.get("data", []):
#     print("-", model["id"])


import os
import requests
from dotenv import load_dotenv

# ✅ Load .env file
load_dotenv()

OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

if not OPEN_AI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

URL = "https://api.openai.com/v1/models"

headers = {
    "Authorization": f"Bearer {OPEN_AI_API_KEY}",
    "Content-Type": "application/json",
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

data = response.json()

print("\n✅ Models available for your OpenAI API key:\n")

for model in data.get("data", []):
    print("-", model["id"])

