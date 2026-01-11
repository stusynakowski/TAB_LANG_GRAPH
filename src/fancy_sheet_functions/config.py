import os
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LG_HOST: str = "127.0.0.1"
    LG_PORT: int = 8000
    LG_WORKFLOW_DIR: str = "./src/workflows"
    
    # Model Provider Secrets (Optional for now)
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
