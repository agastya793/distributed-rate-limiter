import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME")
    APP_VERSION = os.getenv("APP_VERSION")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    )

    DEBUG = os.getenv("DEBUG") == "True"

    RATE_LIMIT_REQUESTS = int(
        os.getenv("RATE_LIMIT_REQUESTS")
    )

    RATE_LIMIT_WINDOW = int(
        os.getenv("RATE_LIMIT_WINDOW")
    )


settings = Settings()