from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_PORT: int
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    API_HOST: str
    API_PORT: int

    class Config:
        env_file = ".env"


settings = Settings()
