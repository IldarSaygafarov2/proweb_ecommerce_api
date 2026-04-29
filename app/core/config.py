# pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import cached_property
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
    )

    # app
    APP_TITLE: str = 'Ecommerce API'
    APP_VERSION: str = '1.0.0'
    API_V1_STR: str = '/api/v1'

    # database
    DATABASE_URL: str = 'postgresql+asyncpg://user:password@host:port/database'

    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: str = ''
    POSTGRES_DB: str = ''
    POSTGRES_PORT: str = 0

    ALEMBIC_DATABASE_URL: str = ''
    TEST_DATABASE_URL: str = 'sqlite+aiosqlite:///./test.db'

    # auth, security
    SECRET_KEY: str = 'some-secret-key'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MEDIA_ROOT: str = './media'
    MEDIA_URL: str = '/media'
    MAX_IMAGE_UPLOAD_SIZE_MB: int = 10

    # admin data
    ADMIN_EMAIL: str = 'admin@example.com'
    ADMIN_PASSWORD: str = 'change-in-production'
    ADMIN_FULLNAME: str = 'Site Admin'

    # admin
    DEFAULT_RATE_LIMIT: str = '100/minute'

    # celery
    CELERY_BROKER_URL: str = 'redis://redis:6379/1'
    CELERY_RESULT_BACKEND: str = 'redis://redis:6379/1'

    REDIS_URL: str = 'redis://redis:6379/0'

    CORS_ORIGINS: list[str] | str = ['http://localhost:3000', 'http://localhost:5173']

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def normalize_origins(cls, value) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        if isinstance(value, list):
            return value
        return []

    @cached_property
    def cors_origins(self) -> list[str]:
        return self.CORS_ORIGINS if isinstance(self.CORS_ORIGINS, list) else []

    @cached_property
    def rate_limiter(self) -> Limiter:
        return Limiter(key_func=get_remote_address, default_limits=[self.DEFAULT_RATE_LIMIT])





settings = Settings()
