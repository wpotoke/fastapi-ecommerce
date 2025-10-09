from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLITE_DATABASE_URL: str = "sqlite:///ecommerce.db"
    MAX_FILE_SIZE_MB: int = 5
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_IMAGE_MIME_TYPES: list[str] = ["image/jpeg", "image/png"]
    ALLOWED_FILE_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png"]
    DATABASE_URL: str
    SECRET_KEY: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def reload_settings() -> Settings:
    """Очищает кэш и возвращает обновлённые настройки."""
    get_settings.cache_clear()
    return get_settings()


settings = get_settings()
