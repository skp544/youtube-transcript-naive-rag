from functools import lru_cache
from pydantic import SecretStr
from langchain_openai import OpenAIEmbeddings

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    logger.info(
        f"Initializing OpenAI embeddings with model: {settings.embedding_model}"
    )
    return OpenAIEmbeddings(
        model=settings.embedding_model, api_key=SecretStr(settings.openai_api_key)
    )
