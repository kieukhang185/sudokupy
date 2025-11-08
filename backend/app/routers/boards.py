# api/app/routers/boards.py
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..crud import boards as crud
from ..database import get_db

router = APIRouter(prefix="/boards", tags=["boards"])

DifficultyParam = Annotated[models.Difficulty, Query()]
DBSession: TypeAlias = Annotated[Session, Depends(get_db)]


@router.get("/random", response_model=schemas.BoardRead)
def random_board(
    db: DBSession,
    difficulty: DifficultyParam = models.Difficulty.EASY,
):
    return crud.get_random_board(db, difficulty)


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
