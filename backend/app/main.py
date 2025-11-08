# api/app/main.py
from app.routers import boards, games
from fastapi import FastAPI

app = FastAPI(title="Sudoku API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(boards.router)
app.include_router(games.router)
