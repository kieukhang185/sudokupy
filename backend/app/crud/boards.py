# api/app/crud/boards.py
import secrets
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models, schemas


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


def get_random_board(db: Session, difficulty: models.Difficulty):
    """Return one random board for the given difficulty."""
    row = (
        db.query(models.Board)
        .filter(models.Board.difficulty == difficulty)
        .order_by(func.random())
        .limit(1)
        .one_or_none()
    )
    if not row:
        raise HTTPException(404, f"No boards for {difficulty}")
    return row


def is_valid_uuid(uuid_string):
    try:
        uuid.UUID(str(uuid_string))  # Attempt to create a UUID object
        return True
    except ValueError:
        return False


def get_board_all(db: Session):
    return db.query(models.Board).order_by(models.Board.created_at.desc()).all()


def get_board_all_by_level(db: Session, difficulty: str):
    return (
        db.query(models.Board)
        .filter(models.Board.difficulty == difficulty)
        .order_by(models.Board.created_at.desc())
        .all()
    )


def get_board_by_id(db: Session, board_id):
    if not is_valid_uuid(board_id):
        raise HTTPException(400, f"Invalid Board id: {board_id}")
    return db.get(models.Board, board_id)


def get_board_by_public_id(db: Session, public_id: str):
    return db.execute(
        select(models.Board).where(models.Board.public_id == public_id)
    ).scalar_one_or_none()


def random_public_id() -> str:
    return secrets.token_hex(6)
