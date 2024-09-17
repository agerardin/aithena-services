# pylint: disable=R0901
# mypy: disable-error-code="import-untyped"
"""Azure OpenAI Embeddings based on LlamaIndex."""

from typing import Optional

from llama_index.embeddings.azure_openai import (
    AzureOpenAIEmbedding as LlamaIndexAzureOpenAI,
)

from aithena_services.envvars import AZURE_OPENAI_ENV_DICT


class AzureOpenAIEmbedding(LlamaIndexAzureOpenAI):
    """Azure OpenAI embeddings."""

    def __init__(
        self, deployment: Optional[str] = None, **kwargs
    ):  # deployment is alias for azure_deployment
        kwargs["api_key"] = AZURE_OPENAI_ENV_DICT["api_key"]
        kwargs["api_version"] = AZURE_OPENAI_ENV_DICT["api_version"]
        if deployment:
            kwargs["azure_deployment"] = deployment
        super().__init__(**kwargs)

    def aget_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Get text embeddings asynchronously."""
        return self._aget_text_embeddings(texts)
