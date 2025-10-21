from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sync_database_url: str = "postgresql://postgres:postgres@localhost:5432/test_db"
    async_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
    api_key: str = "12345"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
