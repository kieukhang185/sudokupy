# api/app/routers/boards.py
from typing import Annotated, TypeAlias

from app import schemas
from app.crud import boards as crud
from app.database import get_db
from app.models import Difficulty
from app.sudoku.generator import generate_puzzle
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/boards", tags=["boards"])

DifficultyParam = Annotated[Difficulty, Query(Difficulty.MEDIUM)]
DBSession: TypeAlias = Annotated[Session, Depends(get_db)]
SEED = Query(default=None)


@router.post("", response_model=schemas.BoardRead)
def create_board(req: schemas.BoardCreate, db: DBSession):
    # Pydantic already enforced lengths & consistency
    board = crud.create_board(db, req)
    return board


@router.get("/{board_id}", response_model=schemas.BoardRead)
def get_board(board_id: str, db: DBSession):
    board = crud.get_board_by_id(db, board_id)
    if not board:
        raise HTTPException(404, "Board not found")
    return board


@router.get("/by-public/{public_id}", response_model=schemas.BoardRead)
def get_board_by_public_id(public_id: str, db: DBSession):
    board = crud.get_board_by_public_id(db, public_id)
    if not board:
        raise HTTPException(404, "Board not found")
    return board


@router.get("/random", response_model=schemas.BoardRead)
def random_board(
    db: DBSession,
    difficulty=DifficultyParam,
    seed=SEED,
):
    # Generate consistent with Difficulty.clues
    puzzle, solution = generate_puzzle(
        seed=seed, clues=difficulty.clues
    )  # uses property from your enum
    req = schemas.BoardCreate(
        public_id=crud.random_public_id(),
        difficulty=difficulty,
        initial_board=puzzle,
        solution_board=solution,
    )
    return crud.create_board(db, req)
