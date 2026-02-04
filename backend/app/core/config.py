from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Elasticsearch
    ES_HOST: str = "http://localhost:9200"
    ES_USER: Optional[str] = None
    ES_PASSWORD: Optional[str] = None
    ES_INDEX: str = "scrapbox-rag"

    # Ollama (Gemma 3)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gemma3:4b"

    # SPLADE Encoder API
    SPLADE_API_URL: str = "http://localhost:8001/encode"

    # Scrapbox
    SCRAPBOX_PROJECT: Optional[str] = None
    SCRAPBOX_COOKIE_CONNECT_SID: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
