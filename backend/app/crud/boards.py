# api/app/crud/boards.py
import secrets

from app import models, schemas
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_board(db: Session, data: schemas.BoardCreate) -> models.Board:
    board = models.Board(
        public_id=data.public_id,
        difficulty=data.difficulty,
        initial_board=data.initial_board,
        solution_board=data.solution_board,
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def get_board_by_id(db: Session, board_id):
    return db.get(models.Board, board_id)


def get_board_by_public_id(db: Session, public_id: str):
    return db.execute(
        select(models.Board).where(models.Board.public_id == public_id)
    ).scalar_one_or_none()


def random_public_id() -> str:
    return secrets.token_hex(6)
