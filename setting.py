from pydantic import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    MONGO_URL: str
    MONGO_DB: str
    ALLOWED_ORIGINS: str = "*"
    ENV: str = "development"
    JWT_SECRET: str = "your-secret"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
