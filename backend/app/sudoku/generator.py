# api/app/sudoku/generator.py
import random
from typing import List, Tuple

from ..models import Difficulty

Board = List[List[int]]

DIFFICULTY_TO_CLUES = {
    "easy": 30,
    "medium": 40,
    "hard": 50,
    "master": 60,  # tweak this number if you want a different target
    "expert": 60,  # optional alias if you still use "expert" anywhere
}


def seeded_rng(seed: int | None) -> random.Random:
    return random.Random(seed if seed is not None else random.randrange(1, 2**31 - 1))


def empty_board() -> Board:
    return [[0] * 9 for _ in range(9)]


def is_safe(board: Board, row: int, col: int, value: int) -> bool:
    if any(board[row][i] == value for i in range(9)):
        return False
    if any(board[i][col] == value for i in range(9)):
        return False
    board_row, board_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[board_row + i][board_col + j] == value:
                return False
    return True


def find_empty(board: Board) -> Tuple[int, int] | None:
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return (row, col)
    return None


def solve_backtrack(board: Board) -> bool:
    pos = find_empty(board)
    if not pos:
        return True
    row, col = pos
    for value in range(1, 10):
        if is_safe(board, row, col, value):
            board[row][col] = value
            if solve_backtrack(board):
                return True
            board[row][col] = 0
    return False


def to_str(board: Board) -> str:
    return "".join(str(board[row][col]) for row in range(9) for col in range(9))


def from_str(string: str) -> Board:
    return [[int(string[row * 9 + col]) for col in range(9)] for row in range(9)]


def generate_full(seed: int | None) -> Board:
    rng = seeded_rng(seed)
    board = empty_board()
    # Seed diagonal boxes to speed up solving
    nums = list(range(1, 10))
    for key in range(0, 9, 3):
        rng.shuffle(nums)
        idx = 0
        for i in range(3):
            for j in range(3):
                board[key + i][key + j] = nums[idx]
                idx += 1
    solve_backtrack(board)
    return board


def carve_to_clues(full: Board, clues: int, seed: int | None) -> Board:
    """Remove exactly 81 - clues cells (target clue count)."""
    rng = seeded_rng(seed if seed is not None else 0)
    coords = [(row, col) for row in range(9) for col in range(9)]
    rng.shuffle(coords)

    target_holes = 81 - clues
    board = [row[:] for row in full]
    removed = 0
    for row, col in coords:
        if removed >= target_holes:
            break
        if board[row][col] == 0:
            continue
        backup = board[row][col]
        board[row][col] = 0
        # Keep a light check: board remains solvable.
        copy = [row[:] for row in board]
        if solve_backtrack(copy):
            removed += 1
        else:
            board[row][col] = backup
    return board


def clues_for(d: str | Difficulty) -> int:
    name = (d.value if isinstance(d, Difficulty) else str(d)).lower()
    return DIFFICULTY_TO_CLUES.get(name, DIFFICULTY_TO_CLUES["easy"])


def generate_puzzle(seed: int | None, difficulty: str | Difficulty) -> tuple[str, str]:
    clues = clues_for(difficulty)
    full = generate_full(clues)
    solution = to_str(full)
    puzzle = to_str(carve_to_clues(full, clues, seed))
    return puzzle, solution
