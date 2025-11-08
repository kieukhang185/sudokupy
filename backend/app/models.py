import uuid
from datetime import datetime as py_datetime
from datetime import timedelta
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, validates

from .database import Base


class Difficulty(str, Enum):
    """Enumerates the difficulty levels of a Sudoku puzzle."""

    EASY = "30"  # ~30 clues
    MEDIUM = "40"  # ~40 clues
    HARD = "50"  # ~50 clues
    EXPERT = "60"  # ~60 clues

    @property
    def clues(self) -> int:
        """Return the numeric count of filled cells."""
        return int(self.value)

    def __str__(self) -> str:
        return self.name.lower()


# ---------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Store as lowercase; see validator below
    username = Column(String(150), unique=False, nullable=False)
    email = Column(String(254), unique=False, nullable=True)

    full_name = Column(String(150))
    # Store only password hashes here, never raw passwords
    password_hash = Column(Text, nullable=False)

    is_deleted = Column(Boolean, nullable=False, server_default="false")

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # relationship
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # If you are NOT using Postgres CITEXT, these functional unique indexes
    # enforce case-insensitive uniqueness.
    __table_args__ = (
        # Case-insensitive unique constraints via functional indexes
        Index("uq_users_username_ci", func.lower(username), unique=True),
        Index("uq_users_email_ci", func.lower(email), unique=True),
    )

    # -------- helpers (suggested usage with passlib) ----------
    def set_password(self, raw_password: str, hasher):
        """
        hasher: an object with method hash(str)->str (e.g. passlib.hash.bcrypt)
        """
        if not raw_password or len(raw_password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        self.password_hash = hasher.hash(raw_password)

    def verify_password(self, raw_password: str, hasher) -> bool:
        """
        hasher: an object with method verify(raw, hash)->bool
        """
        return hasher.verify(raw_password, self.password_hash)

    @validates("username")
    def _v_username(self, key, val: str):
        if not val:
            raise ValueError("username is required")
        val = val.strip().lower()
        if len(val) > 150:
            raise ValueError("username too long")
        return val

    @validates("email")
    def _v_email(self, key, val: str | None):
        if val is None:
            return None
        val = val.strip().lower()
        if len(val) > 254:
            raise ValueError("email too long")
        # Optional: do a lightweight sanity check (don’t over-validate at model level)
        if "@" not in val or val.startswith("@") or val.endswith("@"):
            raise ValueError("invalid email format")
        return val

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


# ---------------------------------------------------------------------
# REFRESH TOKENS
# ---------------------------------------------------------------------
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"  # plural table names for consistency

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Opaque random string (JTI or full token, depending on how you store it)
    token = Column(String(512), unique=True, nullable=False)

    # For rotation / revocation
    parent_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("refresh_tokens.id"), nullable=True
    )
    revoked = Column(Boolean, nullable=False, server_default="false")

    # Optional device / context fingerprinting (handy for security audits)
    user_agent = Column(String(512))
    ip_address = Column(String(64))

    # Expiry & timestamps (timezone-aware)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        # Useful index for cleaning up expired or revoked tokens
        Index("ix_refresh_tokens_userid_revoked", "user_id", "revoked"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )

    def mark_revoked(self):
        self.revoked = True

    @staticmethod
    def default_expiry(days: int = 30) -> py_datetime:
        return py_datetime.utcnow() + timedelta(days=days)

    def __repr__(self):
        return (
            f"<RefreshToken id={self.id} user_id={self.user_id} revoked={self.revoked}>"
        )


class Board(Base):
    __tablename__ = "boards"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_id = Column(String(150), unique=True, nullable=False)

    # Difficulty is stored as an Enum (string values: "30", "40", etc.)
    difficulty = Column(SAEnum(Difficulty, name="difficulty"), nullable=False)

    # Store Sudoku as flat 81-character strings
    initial_board = Column(String(81), nullable=False)
    solution_board = Column(String(81), nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ---------------- Validators ---------------- #
    @validates("initial_board", "solution_board")
    def _validate_board_string(self, key, value):
        if len(value) != 81:
            raise ValueError(f"{key} must be exactly 81 characters long")
        if not all(ch.isdigit() for ch in value):
            raise ValueError(f"{key} must contain only digits (0–9)")
        if key == "solution_board" and "0" in value:
            raise ValueError("solution_board cannot contain zeros")
        return value

    def __repr__(self):
        return f"<Board {self.public_id} ({self.difficulty.name})>"

    # ---------------- Helpers ---------------- #
    def to_grid(self):
        """Return board as a 9×9 list of integers."""
        return [
            [int(self.initial_board[r * 9 + c]) for c in range(9)] for r in range(9)
        ]

    def check_consistency(self):
        """Ensure all given numbers in initial_board match solution_board."""
        for i in range(81):
            a, b = self.initial_board[i], self.solution_board[i]
            if a != "0" and a != b:
                return False
        return True
