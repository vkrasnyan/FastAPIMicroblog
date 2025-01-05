from fastapi import FastAPI
from blogapp.database import init_db
from blogapp.routers import users, tweets, follows, likes, medias
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Microblog API")

# Инициализация базы данных
init_db()

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
app.include_router(follows.router, prefix="/api/follows", tags=["Follows"])
app.include_router(likes.router, prefix="/api/likes", tags=["Likes"])
app.include_router(medias.router, prefix="/api/medias", tags=["Medias"])


@app.get("/", tags=["Health"])
async def health_check():
    """
    Проверка состояния сервера.
    """
    return {"status": "ok"}