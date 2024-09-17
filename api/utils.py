"""Utilities for model and config."""

import json
import os
from pathlib import Path

CONFIG_PATH_ = os.getenv("AITHENA_SERVICES_CONFIG_PATH", None)
if CONFIG_PATH_ is None:
    CONFIG_PATH = Path(__file__).parent.joinpath("config.json")
else:
    CONFIG_PATH = Path(CONFIG_PATH_)


def _write_to_config_json(data: dict) -> None:
    """Write data to config.json."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        models = json.load(file)
        chat_models = models.get("chat_models", [])
        embed_models = models.get("embed_models", [])

    data_to_write = {"chat_models": chat_models, "embed_models": embed_models}
    if "chat_models" in data:
        data_to_write["chat_models"] = data["chat_models"]
    if "embed_models" in data:
        data_to_write["embed_models"] = data["embed_models"]
    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(data_to_write, file, indent=4)
