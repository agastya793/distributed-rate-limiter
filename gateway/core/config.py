import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Distributed Rate Limiter Gateway")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    REDIS_URL: str = os.getenv("REDIS_URL", os.getenv("REDIS_PRIVATE_URL", ""))
    REDIS_HOST: str = os.getenv("REDIS_HOST", os.getenv("REDISHOST", "localhost"))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", os.getenv("REDISPORT", "6379")))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", os.getenv("REDISPASSWORD", ""))

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "my_super_secret_key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "admin-secret-key-12345")
    ALLOWED_ORIGINS: list = ["*"]

    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "5"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8001")
    PRODUCT_SERVICE_URL: str = os.getenv("PRODUCT_SERVICE_URL", "http://127.0.0.1:8002")


settings = Settings()