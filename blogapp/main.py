from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from blogapp.database import engine, async_session, Base
# from routers import users, tweets, follows, likes, medias


# Функция для обработки жизненного цикла приложения в современных версиях FastAPI
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Выполняется при запуске приложения
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Выполняется при завершении работы приложения
    await engine.dispose()

app = FastAPI(title="Microblog API", lifespan=lifespan)

# Зависимость для получения сессии
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(users.router, prefix="/api/users", tags=["Users"])
# app.include_router(tweets.router, prefix="/api/tweets", tags=["Tweets"])
# app.include_router(follows.router, prefix="/api/follows", tags=["Follows"])
# app.include_router(likes.router, prefix="/api/likes", tags=["Likes"])
# app.include_router(medias.router, prefix="/api/medias", tags=["Medias"])


@app.get("/", tags=["Health"])
async def health_check():
    """
    Проверка состояния сервера.
    """
    return {"status": "ok"}


@app.get("/health/db")
async def db_health_check():
    try:
        db = async_session()
        db.execute("SELECT 1")
        return {"status": "Database is connected"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
    finally:
        db.close()
