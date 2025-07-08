from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = (
        "redis://default:WD0FlpOtf3IE7OKRxcGCLOCQ1bit07WD@redis-11167.crce182.ap-south-1-1.ec2.redns.redis-cloud.com:11167"
    )
    MONGO_URL: str = "mongodb+srv://vg100:vg100@cluster0.bszog.mongodb.net/"
    MONGO_DB: str = ""
    ALLOWED_ORIGINS: str = "*"
    ENV: str = "development"
    JWT_SECRET: str = "your-secret"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
