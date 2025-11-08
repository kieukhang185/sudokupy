# api/app/main.py
from fastapi import FastAPI

from .routers import boards, games

app = FastAPI(title="Sudoku API")


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
