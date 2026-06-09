import os
from google.genai import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
client = Client(api_key=api_key)
try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(f"Error: {e}")
