import logging
from pathlib import Path
from aithena_services.envvars import (
    AZURE_OPENAI_AVAILABLE,
    OLLAMA_AVAILABLE,
    OPENAI_AVAILABLE,
)

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)

def get_logger(file = "", log_level = logging.DEBUG):
    logger = logging.getLogger(file)
    logger.setLevel(log_level)
    return logger

logger = get_logger(__file__)


if AZURE_OPENAI_AVAILABLE:
    from aithena_services.envvars import AZURE_OPENAI_MODEL_ENV
    from aithena_services.llms.azure_openai import AzureOpenAI
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", None)
    AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", None)
if OPENAI_AVAILABLE:
    from aithena_services.llms.openai import OpenAI
if OLLAMA_AVAILABLE:
    from aithena_services.llms.ollama import Ollama

from llama_index.core.llms.llm import LLM

FILE_PATH = Path(__file__).parent.absolute()

# keep track of all available models
LLMS_AVAILABLE = []
if AZURE_OPENAI_AVAILABLE:
    LLMS_AVAILABLE.append(f"azure/{AZURE_OPENAI_MODEL_ENV}")
if OPENAI_AVAILABLE:
    LLMS_AVAILABLE.extend(OpenAI.list_models())
if OLLAMA_AVAILABLE:
    LLMS_AVAILABLE.extend(Ollama.list_models())

def create_llm(name: str):
    """Create a model client for a given model configuration
    Configuration are defined through environment variables in aithena services.
    ."""
    if AZURE_OPENAI_AVAILABLE and name.startswith("azure/"):
        return AzureOpenAI(model=AZURE_OPENAI_DEPLOYMENT, deployment=AZURE_OPENAI_DEPLOYMENT)
    if OPENAI_AVAILABLE and name in OpenAI.list_models():
        return OpenAI(model=name)
    if OLLAMA_AVAILABLE and name in Ollama.list_models():
        return Ollama(model=name)


"""Retrieve all available models.
TODO this should probably be part of the services API
since aithena-services act as a gateway to all models.
"""
LLM_DICT = {name: create_llm(name) for name in LLMS_AVAILABLE}

PROMPT = """
You are a helpful assistant named Aithena.
Respond to users with witty, entertaining, and thoughtful answers.
User wants short answers, maximum five sentences.
If user asks info about yourself or your architecture,
respond with info about your LLM model and its capabilities.
Do not finish every sentence with a question.
If you ask a question, always include a question mark.
Do not introduce yourself to user if user does not ask for it.
Never explain to user how your answers are.
"""

logger.info(LLMS_AVAILABLE)


