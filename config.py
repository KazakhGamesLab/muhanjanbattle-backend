from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="../.env")


class Settings(BaseSettings):
    APP_ENV: str = os.getenv("APP_ENV")
    REDIS_URL: str = os.getenv("REDIS_URL")
    DATABASE_URL: str = os.getenv("DATABASE_URL")


settings = Settings()