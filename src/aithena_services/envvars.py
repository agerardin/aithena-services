"""Environment Variable Configuration for Aithena Services."""

import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(), override=True)

OPENAI_KEY = os.getenv("OPENAI_API_KEY", None)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", None)
if isinstance(OLLAMA_HOST, str) and OLLAMA_HOST.endswith("/"):
    OLLAMA_HOST = OLLAMA_HOST[:-1]

# ----AzureOpenAI----
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY", None)
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", None)
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", None)
AZURE_OPENAI_MODEL_ENV = os.getenv("AZURE_OPENAI_DEPLOYMENT", None)
AZURE_OPENAI_ENV_DICT = {
    "api_key": AZURE_OPENAI_KEY,
    "azure_endpoint": AZURE_OPENAI_ENDPOINT,  # redundant, compatible with LI
    "api_version": AZURE_OPENAI_API_VERSION,
}

OPENAI_AVAILABLE = OPENAI_KEY is not None
OLLAMA_AVAILABLE = OLLAMA_HOST is not None

AZURE_OPENAI_AVAILABLE = (
    (AZURE_OPENAI_KEY is not None)
    and (AZURE_OPENAI_ENDPOINT is not None)
    and (AZURE_OPENAI_API_VERSION is not None)
)


__all__ = [
    "OPENAI_AVAILABLE",
    "OLLAMA_AVAILABLE",
    "OPENAI_KEY",
    "OLLAMA_HOST",
    "AZURE_OPENAI_AVAILABLE",
    "AZURE_OPENAI_ENV_DICT",
]
