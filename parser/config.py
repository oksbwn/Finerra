import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ingestion Parser Microservice"
    PORT: int = 8001
    
    # Paths
    # To mimic main app structure if needed, but main app uses relative path in DB URL
    # Here we want to be explicit about the data folder per request
    
    # Database
    # Default to data folder in root
    DATABASE_URL: str = "duckdb:///../data/ingestion_engine_parser.duckdb"
    
    model_config = ConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
