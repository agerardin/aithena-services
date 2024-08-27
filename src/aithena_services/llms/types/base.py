"""Base LLM class for Aithena Services."""

from functools import wraps
from typing import Any, Callable, Sequence

from aithena_services.llms.types import Message
from aithena_services.llms.types.response import (
    ChatResponse,
    ChatResponseAsyncGen,
    ChatResponseGen,
)
from aithena_services.llms.utils import check_and_cast_messages


class AithenaLLM:  # pylint: disable=too-few-public-methods
    """Base LLM class for Aithena Services.
    This class indicates that for `chat`, `stream_chat`, and `astream_chat` methods
    the responses are modified `llama_index.ChatResponse` objects where `.message` attribute
    is a `Message` from Aithena Services.
    """


# NOTE: Sequence[dict | Message] is used for mypy compatibility with LlamaIndex


def streamchataithena(method: Callable) -> Callable:
    """Decorator for `stream_chat` to return `ChatResponseGen` with `Message`."""

    @wraps(method)
    def wrapper(
        self, messages: Sequence[dict | Message], **kwargs: Any
    ) -> ChatResponseGen:
        messages_ = check_and_cast_messages(messages)
        llama_stream = method(self, messages_, **kwargs)

        def gen() -> ChatResponseGen:
            for response in llama_stream:
                yield ChatResponse.from_llamaindex(response)

        return gen()

    return wrapper


def chataithena(method: Callable) -> Callable:
    """Decorator for `chat` to return `ChatResponse` with `Message`."""

    @wraps(method)
    def wrapper(
        self, messages: Sequence[dict | Message], **kwargs: Any
    ) -> ChatResponse:
        messages_ = check_and_cast_messages(messages)
        llama_index_response = method(self, messages_, **kwargs)
        return ChatResponse.from_llamaindex(llama_index_response)

    return wrapper


def astreamchataithena(method: Callable) -> Callable:
    """Decorator for `astream_chat` to return `ChatResponseAsyncGen` with `Message`."""

    @wraps(method)
    async def wrapper(
        self, messages: Sequence[dict | Message], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        messages_ = check_and_cast_messages(messages)
        llama_stream = method(self, messages_, **kwargs)

        async def gen() -> ChatResponseAsyncGen:
            async for response in await llama_stream:
                yield ChatResponse.from_llamaindex(response)

        return gen()

    return wrapper


def achataithena(method: Callable) -> Callable:
    """Decorator for `chat` to return `ChatResponse` with `Message`."""

    @wraps(method)
    async def wrapper(
        self, messages: Sequence[dict | Message], **kwargs: Any
    ) -> ChatResponse:
        messages_ = check_and_cast_messages(messages)
        llama_index_response = await method(self, messages_, **kwargs)
        return ChatResponse.from_llamaindex(llama_index_response)

    return wrapper
