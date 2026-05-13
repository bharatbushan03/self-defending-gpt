import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings.
    Reads environment variables from the system or a .env file.
    """
    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/selfdefendinggpt")

    # NVIDIA Nemotron API Configuration
    NEMOTRON_API_KEY: str = os.getenv("NEMOTRON_API_KEY")
    NEMOTRON_BASE_URL: str = os.getenv("NEMOTRON_BASE_URL", "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions")

    # Frontend Configuration
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    class Config:
        # This allows Pydantic to read from a .env file if you choose to use it
        # without the load_dotenv() call, but explicit is better.
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate settings
settings = Settings()
