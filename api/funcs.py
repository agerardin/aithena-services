# mypy: disable-error-code="import-untyped"
"""Functions for Aithena Services API."""

import json
from copy import copy
from typing import Optional

import requests
from chat_models import ChatModel
from embed_models import EmbedModel
from utils import CONFIG_PATH, _write_to_config_json

from aithena_services.envvars import OLLAMA_AVAILABLE

if OLLAMA_AVAILABLE:
    from aithena_services.envvars import OLLAMA_HOST as OLLAMA_URL


def _get_current_models(key: str) -> tuple[list[dict], list[str]]:
    """Get current models in config.json and return (list[dict], list[str]).

    The first list is a list of ChatModels/EmbedModels as `dict`, the second list is
    a list of the model names, equivalent to doing `x["name"] for x in firstlist`.
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        current_models = json.load(file)[key]
    current_names = [x["name"] for x in current_models]
    return current_models, current_names


def _ollama_result_to_model_obj(url: str, mode: str, res: dict) -> ChatModel:
    """Convert Ollama API result to ChatModel/EmbedModel object."""
    # mypy complains no 'params'
    if mode == "chat":
        return ChatModel(  # type: ignore
            name=res["name"],
            model=res["model"],
            backend="ollama",
            config={"url": url},
        )
    return EmbedModel(  # type: ignore
        name=res["name"],
        model=res["model"],
        backend="ollama",
        config={"url": url},
    )


def get_chat_models_from_ollama(url: Optional[str] = None) -> list[ChatModel]:
    """Retrieve list of chat models from Ollama."""
    if url is None:
        url = OLLAMA_URL
    res = requests.get(f"{url}/api/tags", timeout=40).json()["models"]
    names = [model["name"] for model in res]
    names = [name for name in names if not "embed" in name]
    models = [model["model"] for model in res]
    models = [model for model in models if not "embed" in model]
    if len(names) < 1:
        return []
    return [
        _ollama_result_to_model_obj(url, "chat", {"name": name, "model": model})
        for name, model in zip(names, models)
    ]


def get_embed_models_from_ollama(url: Optional[str] = None) -> list[ChatModel]:
    """Retrieve list of embed models from Ollama."""
    if url is None:
        url = OLLAMA_URL
    res = requests.get(f"{url}/api/tags", timeout=40).json()["models"]
    names = [model["name"] for model in res]
    names = [name for name in names if "embed" in name]
    models = [model["model"] for model in res]
    models = [model for model in models if "embed" in model]
    if len(names) < 1:
        return []
    return [
        _ollama_result_to_model_obj(url, "embed", {"name": name, "model": model})
        for name, model in zip(names, models)
    ]


def update_ollama_chat(url: Optional[str] = None, overwrite: bool = False) -> None:
    """Scan local Ollama chat models and add to config.

    Args:
        overwrite: if `False`, a model with the same name as one
            that is already present in config.json will be ignored

    """
    current_models, current_names = _get_current_models("chat_models")
    ollama: dict[str, list] = {"models": []}
    ollama["models"].extend(
        [json.loads(x.model_dump_json()) for x in get_chat_models_from_ollama(url)]
    )
    data: dict[str, list] = {"chat_models": copy(current_models)}
    for model in ollama["models"]:
        if not overwrite:
            if model["name"] not in current_names:
                data["chat_models"].append(model)
        else:
            data["chat_models"].append(model)
    _write_to_config_json(data)


def update_ollama_embed(url: Optional[str] = None, overwrite: bool = False) -> None:
    """Scan local Ollama embed models and add to config.

    Args:
        overwrite: if `False`, a model with the same name as one
            that is already present in config.json will be ignored

    """
    current_models, current_names = _get_current_models("embed_models")
    ollama: dict[str, list] = {"models": []}
    ollama["models"].extend(
        [json.loads(x.model_dump_json()) for x in get_embed_models_from_ollama(url)]
    )
    data: dict[str, list] = {"embed_models": copy(current_models)}
    for model in ollama["models"]:
        if not overwrite:
            if model["name"] not in current_names:
                data["embed_models"].append(model)
        else:
            data["embed_models"].append(model)
    _write_to_config_json(data)


def add_chat_model_to_config(model_dict: dict) -> None:
    """Add new chat model to config.json"""
    chat_model = ChatModel(**model_dict)
    current_models, current_names = _get_current_models("chat_models")
    if chat_model.name in current_names:
        raise ValueError("Model name already in config.json")
    current_models.append(json.loads(chat_model.model_dump_json()))
    data: dict = {"chat_models": current_models}
    _write_to_config_json(data)


def add_embed_model_to_config(model_dict: dict) -> None:
    """Add new embed model to config.json"""
    embed_model = EmbedModel(**model_dict)
    current_models, current_names = _get_current_models("embed_models")
    if embed_model.name in current_names:
        raise ValueError("Model name already in config.json")
    current_models.append(json.loads(embed_model.model_dump_json()))
    data: dict = {"embed_models": current_models}
    _write_to_config_json(data)
