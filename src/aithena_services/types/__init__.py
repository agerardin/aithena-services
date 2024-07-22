"""Aithena Services Types."""

# pylint: disable=W0718

import os

from .message import Message
from .models import BaseLLM

__all__ = ["Message", "BaseLLM"]

if os.getenv("OPENAI_API_KEY", None) is not None:
    from .models import OpenAI

    __all__.append("OpenAI")

if os.getenv("ANTHROPIC_API_KEY", None) is not None:
    from .models import Anthropic

    __all__.append("Anthropic")

if os.getenv("OLLAMA_URL", None) is not None:
    from .models import Ollama

    __all__.append("Ollama")
