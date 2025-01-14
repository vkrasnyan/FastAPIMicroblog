from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.database import engine, async_session, Base
from blogapp.routers import users, tweets, medias


# Функция для обработки жизненного цикла приложения в современных версиях FastAPI
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Выполняется при запуске приложения
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Выполняется при завершении работы приложения
    await engine.dispose()

app = FastAPI(title="Microblog API", lifespan=lifespan)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(tweets.router, prefix="/tweets", tags=["Tweets"])
# app.include_router(follows.router, prefix="/follows", tags=["Follows"])
# app.include_router(likes.router, prefix="/likes", tags=["Likes"])
app.include_router(medias.router, prefix="/medias", tags=["Medias"])


@app.get("/", tags=["Health"])
async def health_check():
    """
    Проверка состояния сервера.
    """
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"])
async def db_health_check():
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "Database is connected"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
