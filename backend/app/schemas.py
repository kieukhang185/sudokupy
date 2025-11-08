# schemas.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Import the Difficulty enum from your models module to avoid duplication.
# Adjust the import path to match your project layout.
from .models import Difficulty

# =========================
# Shared / Utilities
# =========================


def _validate_board_str(value: str, *, field_name: str) -> str:
    if len(value) != 81:
        raise ValueError(f"{field_name} must be exactly 81 characters long")
    if not value.isdigit():
        raise ValueError(f"{field_name} must contain only digits (0–9)")
    if field_name == "solution_board" and "0" in value:
        raise ValueError("solution_board cannot contain zeros")
    return value


def _count_clues(board: str) -> int:
    # number of non-zero digits
    return sum(1 for ch in board if ch != "0")


# =========================
# Board Schemas
# =========================


class BoardBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: str = Field(..., min_length=1, max_length=150)
    difficulty: Difficulty
    initial_board: str = Field(..., min_length=81, max_length=81)
    solution_board: str = Field(..., min_length=81, max_length=81)

    @field_validator("initial_board")
    @classmethod
    def _v_initial_board(cls, v: str) -> str:
        return _validate_board_str(v, field_name="initial_board")

    @field_validator("solution_board")
    @classmethod
    def _v_solution_board(cls, v: str) -> str:
        return _validate_board_str(v, field_name="solution_board")

    @field_validator("solution_board")
    @classmethod
    def _v_consistency(cls, sol: str, info):
        # Ensure fixed clues in initial match solution
        initial = info.data.get("initial_board")
        if initial and len(initial) == 81:
            for i in range(81):
                if initial[i] != "0" and initial[i] != sol[i]:
                    raise ValueError(
                        f"solution_board conflicts with initial_board at index {i}"
                    )
        return sol


class BoardCreate(BoardBase):
    # Optional strict check: enforce the clue count equals the Difficulty value.
    # Comment this out if you prefer not to enforce it.
    @field_validator("initial_board")
    @classmethod
    def _v_clues_match_difficulty(cls, v: str, info):
        difficulty: Difficulty | None = info.data.get("difficulty")
        if difficulty is not None:
            clues = _count_clues(v)
            expected = int(difficulty.value)
            if clues != expected:
                raise ValueError(
                    f"initial_board has {clues} clues;"
                    "expected {expected} for {difficulty.name.lower()}"
                )
        return v


class BoardUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # All optional for PATCH-style updates
    public_id: Optional[str] = Field(None, min_length=1, max_length=150)
    difficulty: Optional[Difficulty] = None
    initial_board: Optional[str] = Field(None, min_length=81, max_length=81)
    solution_board: Optional[str] = Field(None, min_length=81, max_length=81)

    @field_validator("initial_board")
    @classmethod
    def _v_initial_board(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_board_str(v, field_name="initial_board")

    @field_validator("solution_board")
    @classmethod
    def _v_solution_board(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_board_str(v, field_name="solution_board")


class BoardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    public_id: str
    difficulty: Difficulty
    initial_board: str
    solution_board: str
    created_at: datetime
    updated_at: datetime


class BoardPayload(BaseModel):
    puzzle: str
    state: Optional[str] = None


class ValidateReq(BaseModel):
    board: BoardPayload


class ValidateResp(BaseModel):
    valid: bool
    complete: bool
    conflicts: list[int]


class NewGameReq(BaseModel):
    difficulty: Difficulty = Difficulty.MEDIUM
    seed: Optional[int] = None


class NewGameResp(BaseModel):
    difficulty: Difficulty
    puzzle: str
    solution: str


class SolveReq(BaseModel):
    board: BoardPayload


class SolveResp(BaseModel):
    solution: str


# =========================
# User Schemas
# =========================


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., min_length=1, max_length=150)
    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None

    @field_validator("username")
    @classmethod
    def _v_username(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("email")
    @classmethod
    def _v_email(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v


class UserCreate(UserBase):
    # Accept a raw password on create; your service layer should hash it.
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: Optional[str] = Field(None, min_length=1, max_length=150)
    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = None
    # For password changes, keep a dedicated field name to avoid confusion
    new_password: Optional[str] = Field(None, min_length=8)

    @field_validator("username")
    @classmethod
    def _v_username(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v

    @field_validator("email")
    @classmethod
    def _v_email(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().lower() if v else v


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    full_name: Optional[str]
    email: Optional[EmailStr]
    created_at: datetime
    last_updated: Optional[datetime]
    is_deleted: bool


# =========================
# Refresh Token Schemas
# =========================


class RefreshTokenBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    # token string can be long (e.g., JWT or opaque)
    token: str = Field(..., min_length=1, max_length=2048)
    expires_at: datetime
    user_agent: Optional[str] = Field(None, max_length=512)
    ip_address: Optional[str] = Field(None, max_length=64)
    parent_id: Optional[uuid.UUID] = None


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    # You may or may not want to expose the token after creation; keep optional here.
    token: Optional[str] = None
    revoked: bool
    expires_at: datetime
    created_at: datetime
    user_agent: Optional[str]
    ip_address: Optional[str]
    parent_id: Optional[uuid.UUID]


# =========================
# Auth Convenience (optional)
# =========================


class TokenPair(BaseModel):
    """Useful response schema when issuing tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
