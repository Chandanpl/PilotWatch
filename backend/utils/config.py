import os

class Settings:
    PROJECT_NAME: str = "PilotWatch Backend"
    DATABASE_URL: str = "sqlite:///./pilotwatch.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "b30a13efd85c4ad4b05a76cb402b9e69317d7b0f0b4d4554b5dfd6d9c6d48c8b")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
