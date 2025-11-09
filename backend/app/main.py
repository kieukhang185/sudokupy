# api/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import boards, games

app = FastAPI(title="Sudoku API")


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ["*"] for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "*"],
    expose_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def _create_tables():
    from .database import engine
    from .models import Base  # Base.metadata includes Board, User, RefreshToken, etc.

    Base.metadata.create_all(bind=engine)


app.include_router(boards.router)
app.include_router(games.router)
