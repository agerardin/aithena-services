# mypy: disable-error-code="import-untyped"
"""Aithena-Services FastAPI REST Endpoints. """

# pylint: disable=W1203, C0412

import json
from typing import Optional

from chat_models import ChatModel, init_chat_models
from embed_models import EmbedModel, init_embed_models
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from funcs import (
    add_chat_model_to_config,
    add_embed_model_to_config,
    update_ollama_chat,
    update_ollama_embed,
)
from pydantic import HttpUrl

from aithena_services.envvars import (
    AZURE_OPENAI_AVAILABLE,
    OLLAMA_AVAILABLE,
    OPENAI_AVAILABLE,
)

# OPENAI_AVAILABLE = False
# AZURE_OPENAI_AVAILABLE = False

if OPENAI_AVAILABLE:
    from aithena_services.llms.openai import OpenAI
if AZURE_OPENAI_AVAILABLE:
    from aithena_services.embeddings.azure_openai import AzureOpenAIEmbedding
    from aithena_services.llms.azure_openai import AzureOpenAI
if OLLAMA_AVAILABLE:
    from aithena_services.embeddings.ollama import OllamaEmbedding
    from aithena_services.llms.ollama import Ollama


app = FastAPI()


ChatModels = init_chat_models()
EmbedModels = init_embed_models()


def check_platform(platform: str):
    """Check if the platform is valid."""
    if platform not in ["ollama", "openai", "azure"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid platform, must be 'ollama', 'openai' or 'azure'",
        )
    if platform == "ollama" and not OLLAMA_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Ollama is not available.",
        )
    if platform == "openai" and not OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="OpenAI is not available.",
        )
    if platform == "azure" and not AZURE_OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Azure OpenAI is not available.",
        )


@app.get("/test")
def test():
    """Test FastAPI deployment."""
    return {"status": "success"}


@app.get("/chat/list")
def list_chat_models():
    """List all available chat models."""
    return ChatModels.names


@app.get("/embed/list")
def list_embed_models():
    """List all available embed models."""
    return EmbedModels.names


@app.get("/chat/list/{platform}")
def list_chat_models_by_platform(platform: str):
    """List all available chat models by platform."""
    check_platform(platform)
    return [model.name for model in ChatModels.filter_models(platform)]


@app.get("/embed/list/{platform}")
def list_embed_models_by_platform(platform: str):
    """List all available embed models by platform."""
    check_platform(platform)
    return [model.name for model in EmbedModels.filter_models(platform)]


@app.put("/chat/list/update")
def update_chat_models():
    """Update chat models."""
    ChatModels.update()
    return {"status": "success"}


@app.put("/embed/list/update")
def update_embed_models():
    """Update embed models."""
    EmbedModels.update()
    return {"status": "success"}


@app.post("/chat/list/add")
def add_chat_model_to_list(model_dict: dict):
    """Add model to config"""
    try:
        add_chat_model_to_config(model_dict)
        ChatModels.update()
    except Exception as exc:
        print(exc.__class__)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success"}


@app.post("/embed/list/add")
def add_embed_model_to_list(model_dict: dict):
    """Add model to config"""
    try:
        add_embed_model_to_config(model_dict)
        EmbedModels.update()
    except Exception as exc:
        print(exc.__class__)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success"}


@app.delete("/chat/list/delete/{model}")
def delete_chat_model_from_list(model: str):
    """Delete chat model from config."""
    if model not in ChatModels.names:
        raise HTTPException(status_code=400, detail="Model not found.")
    try:
        ChatModels.delete_model(model)
        ChatModels.update()
    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success"}


@app.delete("/embed/list/delete/{model}")
def delete_embed_model_from_list(model: str):
    """Delete embed model from config."""
    if model not in EmbedModels.names:
        raise HTTPException(status_code=400, detail="Model not found.")
    try:
        EmbedModels.delete_model(model)
        EmbedModels.update()
    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "success"}


@app.put("/embed/list/update/ollama")
def update_ollama_embed_models(url: Optional[str] = None, overwrite: bool = False):
    """Update Ollama models."""

    update_ollama_embed(url, overwrite)
    EmbedModels.update()
    return {"status": "success"}


@app.put("/chat/list/update/ollama")
def update_ollama_chat_models(url: Optional[str] = None, overwrite: bool = False):
    """Update Ollama models."""

    update_ollama_chat(url, overwrite)
    ChatModels.update()
    return {"status": "success"}


def _resolve_url(url: Optional[HttpUrl]) -> Optional[str]:
    """Resolve URL to str or None."""
    if url:
        return str(url)
    return None


def get_client(model: ChatModel | EmbedModel):
    """Get client for model."""
    if isinstance(model, ChatModel):
        if model.backend == "ollama":
            if model.params:
                return Ollama(
                    model=model.model,
                    base_url=_resolve_url(model.config.url),
                    **model.params,
                )
            return Ollama(model=model.model, base_url=_resolve_url(model.config.url))
        if model.backend == "openai":
            if model.params:
                return OpenAI(
                    model=model.model,
                    api_base=model.config.api_base,
                    **model.params,
                )
            return OpenAI(
                model=model.model,
                api_base=model.config.api_base,
            )
        if model.backend == "azure":
            if model.params:
                return AzureOpenAI(
                    azure_endpoint=_resolve_url(model.config.endpoint),
                    api_version=model.config.api_version,
                    model=model.model,
                    deployment=model.config.deployment,
                    **model.params,
                )
            return AzureOpenAI(
                azure_endpoint=_resolve_url(model.config.endpoint),
                api_version=model.config.api_version,
                model=model.model,
                deployment=model.config.deployment,
            )
        raise HTTPException(
            status_code=400,
            detail="Invalid platform, must be 'ollama', 'openai' or 'azure'",
        )
    if isinstance(model, EmbedModel):
        if model.backend == "ollama":
            if model.params:
                return OllamaEmbedding(
                    model=model.model,
                    base_url=_resolve_url(model.config.url),
                    **model.params,
                )
            return OllamaEmbedding(
                model=model.model,
                base_url=_resolve_url(model.config.url),
            )
        if model.backend == "azure":
            if model.params:
                return AzureOpenAIEmbedding(
                    azure_endpoint=_resolve_url(model.config.endpoint),
                    api_version=model.config.api_version,
                    model=model.model,
                    deployment=model.config.deployment,
                    **model.params,
                )
            return AzureOpenAIEmbedding(
                azure_endpoint=_resolve_url(model.config.endpoint),
                api_version=model.config.api_version,
                model=model.model,
                deployment=model.config.deployment,
            )
        raise HTTPException(
            status_code=400,
            detail="Invalid platform, must be 'ollama', 'openai' or 'azure'",
        )


@app.post("/chat/{model}/generate")
async def generate_from_msgs(
    model: str,
    messages: list[dict] | str,
    stream: bool = True,
):
    """Generate a chat completion from a list of messages."""

    print(f"For {model} chat, received {messages}, stream: {stream}")
    model_ = ChatModels.get_model(model)
    backend = model_.backend
    check_platform(backend)
    try:
        client = get_client(model_)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    if stream:

        async def stream_response(messages):
            async for chunk in await client.astream_chat(messages):
                # print(chunk, type(chunk))
                response = chunk.__dict__
                # print(f"response is {response}")
                response["message"] = chunk.message.as_json()
                yield json.dumps(response, default=lambda x: x.model_dump_json()) + "\n"
                # yield json.dumps(response)

        return StreamingResponse(
            stream_response(messages), media_type="application/json"
        )
    try:
        res = await client.achat(messages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return res.as_json()


@app.post("/embed/{model}/generate")
async def text_embeddings(
    model: str,
    text: str | list[str],
):
    """Get text embeddings."""
    model_ = EmbedModels.get_model(model)
    backend = model_.backend
    check_platform(backend)
    if backend == "openai":
        raise HTTPException(
            status_code=400,
            detail="OpenAI has not been implemented for embeddings yet.",
        )
    try:
        client = get_client(model_)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        if isinstance(text, str):
            res = await client.aget_text_embedding(text)
        if isinstance(text, list):
            res = await client.aget_text_embeddings(text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return res
