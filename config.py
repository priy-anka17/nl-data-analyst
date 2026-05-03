import os
from dotenv import load_dotenv

_project_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_project_root, ".env"), override=True)

LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))


def get_groq_api_key() -> str:
    return os.getenv("GROQ_API_KEY", "")
