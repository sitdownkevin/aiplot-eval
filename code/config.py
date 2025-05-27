from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os

class Config:
    OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://burn.hair/v1")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxx")

    DRAMA_AGENT_MODEL_PROVIDER = "openailike"
    DRAMA_AGENT_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o")

    SCRIPTWRITER_AGENT_MODEL_PROVIDER = "openailike"
    SCRIPTWRITER_AGENT_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o")
