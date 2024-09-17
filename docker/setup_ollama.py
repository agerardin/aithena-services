"""Script to setup Ollama, for convenience purposes.

This script will:
* Pull llama3.1:latest to Ollama
* Pull nomic-embed-text to Ollama
* Update the config.json file for Aithena Services FastAPI
"""

import logging

import requests
import typer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
logger = logging.getLogger(__name__)

app = typer.Typer(help="Setup Ollama for Aithena Services.")


@app.command()
def main(
    ollama_host: str = "http://localhost:11434",
    api_host: str = "http://localhost:8000",
    internal_ollama_host: str = "http://192.0.0.89:11434",
):
    """Setup Ollama for Aithena Services."""
    logger.info("Pulling llama3.1:latest to Ollama")
    try:
        requests.post(
            f"{ollama_host}/api/pull",
            json={"name": "llama3.1"},
            timeout=20,
        )
    except Exception as e:
        logger.error(f"Failed to pull llama3.1: {e}")
    logger.info("Pulled llama3.1:latest to Ollama")
    logger.info("Pulling nomic-embed-text to Ollama")
    try:
        requests.post(
            f"{ollama_host}/api/pull",
            json={"name": "nomic-embed-text"},
            timeout=20,
        )
    except Exception as e:
        logger.error(f"Failed to pull nomic-embed-text: {e}")
    logger.info("Pulled nomic-embed-text to Ollama")
    logger.info("Updating config.json for Aithena Services - Chat")
    try:
        r = requests.put(
            f"{api_host}/chat/list/update/ollama",
            params={"overwrite": True, "url": internal_ollama_host},
            timeout=20,
        )
        if r.json() != {"status": "success"}:
            raise Exception(r.json()["detail"])
    except Exception as e:
        logger.error(f"Failed to update config.json for Aithena Services - Chat: {e}")
    logger.info("Updated config.json for Aithena Services - Chat")
    logger.info("Updating config.json for Aithena Services - Embed")
    try:
        requests.put(
            f"{api_host}/embed/list/update/ollama",
            params={"overwrite": True, "url": internal_ollama_host},
            timeout=20,
        )
        if r.json() != {"status": "success"}:
            raise Exception(r.json()["detail"])
    except Exception as e:
        logger.error(f"Failed to update config.json for Aithena Services - Embed: {e}")
    logger.info("Updated config.json for Aithena Services - Embed")
    logger.info("Setup complete.")


if __name__ == "__main__":
    app()
