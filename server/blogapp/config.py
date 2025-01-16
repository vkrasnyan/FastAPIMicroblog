from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql+asyncpg://vickie:newpassword@localhost/microblog'

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
