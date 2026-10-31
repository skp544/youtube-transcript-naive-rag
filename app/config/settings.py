from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Env settings for the application"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Openai
    openai_api_key : str = ""

    # qdrant 
    qdrant_url: str = ""

    # temporal
    temporal_host: str = ""
    temporal_namespace: str = ""
    temporal_task_queue: str = ""

    #collection and models
    collection_name: str = ""
    embedding_model: str = ""
    llm_model: str = ""
    llm_temperature : float = 0.0
    chunk_size: int = 1000
    chunk_overlap : int = 200
    retrieval_k: int = 4

    #API
    api_host: str = "0.0.0.0"
    api_port: str = "8080"
    log_level: str = "INFO"
    app_name: str = "YoutubeTranscriptNaiveRag"

    #upload limits 
    max_files_per_upload: int = 10
    index_batch_size: int = 100

    # ingestion mode
    use_temporal_ingestion: bool = False

    # evaluation
    enable_ragas_evaluation: bool = False

    upload_dir : str = "uploads"

@lru_cache
def get_settings() -> Settings:
    """Get the settings for the application"""
    return Settings()