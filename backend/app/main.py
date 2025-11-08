from fastapi import FastAPI

app = FastAPI(title="Sudoku API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/hello")
def hello():
    return {"message": "Hello from Sudoku API"}
