import os
from dataclasses import dataclass
import google.auth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# To use AI Studio credentials:
# 1. Create a .env file in the /app directory with:
#    GOOGLE_GENAI_USE_VERTEXAI=FALSE
#    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
# 2. This will override the default Vertex AI configuration
try:
    _, project_id = google.auth.default()
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
except Exception:
    pass # Local development without gcloud auth

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class AntigravityConfiguration:
    """Configuration for Antigravity agent models and parameters."""

    model: str = "gemini-3-pro-preview"
    max_search_iterations: int = 3


config = AntigravityConfiguration()
