import os
from google.genai import Client
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
client = Client(api_key=api_key)

class SimpleOutput(BaseModel):
    message: str
    confidence: float

models = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
]

for model in models:
    try:
        response = client.models.generate_content(
            model=model,
            contents="Analyze if garlic cures COVID. Return structured JSON.",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SimpleOutput,
            ),
        )
        print(f"Success for {model}: {response.text}")
    except Exception as e:
        print(f"Error for {model}: {e}")
