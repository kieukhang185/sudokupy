# api/app/routers/boards.py
from typing import Annotated, TypeAlias

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..crud import boards as crud
from ..database import get_db

router = APIRouter(prefix="/boards", tags=["boards"])

DifficultyParam: str = Query("easy")
DBSession: TypeAlias = Annotated[Session, Depends(get_db)]


@router.post("", response_model=schemas.BoardRead)
def create_board(req: schemas.BoardCreate, db: DBSession):
    # Pydantic already enforced lengths & consistency
    board = crud.create_board(db, req)
    return board


@router.get("", response_model=list[schemas.BoardRead])
def get_boards(db: DBSession):
    boards = crud.get_board_all(db)
    if not boards:
        raise HTTPException(404, "Board not found")
    return boards


@router.get("/random", response_model=schemas.BoardRead)
def random_board(
    db: DBSession,
    difficulty=DifficultyParam,
):
    return crud.get_random_board(db, difficulty)


@router.get("/difficulty/{difficulty}", response_model=list[schemas.BoardRead])
def get_board_by_level(db: DBSession, difficulty: str):
    """Get board with a difficulty (e.g. easy,  medium, hard, expert)"""
    boards = crud.get_board_all_by_level(db, difficulty)
    if not boards:
        raise HTTPException(404, "Board not found")
    return boards


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
