import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import AsyncGenerator
from sqlalchemy import text

from blogapp.database import engine, async_session, Base
from blogapp.routers import users, medias, tweets

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # Корень проекта
static_dir = os.path.join(base_dir, "/app/static")
favicon_path = os.path.join(static_dir, "favicon.ico")

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

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(tweets.router, prefix="/api/tweets", tags=["Tweets"])
app.include_router(medias.router, prefix="/api/medias", tags=["Medias"])
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/js", StaticFiles(directory=os.path.join(static_dir, "js")), name="js")
app.mount("/css", StaticFiles(directory=os.path.join(static_dir, "css")), name="css")




@app.get("/login")
async def read_main():
    index_path = os.path.join(base_dir, "app", "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "index.html not found"}


@app.get("/", tags=["Health"])
async def health_check():
    """
    Проверка состояния сервера.
    """
    return {"status": "ok"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"detail": "Favicon not found"}


@app.get("/health/db", tags=["Health"])
async def db_health_check():
    """
    Проверка состояния БД
    """
    try:
        async with async_session() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "Database is connected"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
