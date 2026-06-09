import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
client = Client(api_key=api_key)

models_to_test = ["gemini-2.0-flash", "gemini-flash-latest", "gemini-3.5-flash"]

for model in models_to_test:
    try:
        response = client.models.generate_content(
            model=model,
            contents="Say hello!",
        )
        print(f"Success for {model}: {response.text}")
    except Exception as e:
        print(f"Error for {model}: {e}")
