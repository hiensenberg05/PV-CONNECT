# import google.generativeai as genai
# from app.config import GEMINI_API_KEY

# genai.configure(api_key=GEMINI_API_KEY)

# def get_embedding(text: str):
#     return genai.embed_content(
#         model="models/text-embedding-004",
#         content=text
#     )["embedding"]


from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding
