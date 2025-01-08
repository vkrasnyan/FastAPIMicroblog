from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://vickie:newpassword@localhost:5432/microblog"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
