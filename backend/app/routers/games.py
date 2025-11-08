# api/app/routers/games.py
from typing import Dict, List, Set, Tuple

from app import schemas
from app.sudoku.generator import from_str, generate_puzzle, solve_backtrack, to_str
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/games", tags=["games"])

Board = List[List[int]]


def _row_conflicts(board: Board) -> Set[int]:
    bad: Set[int] = set()

    for row in range(9):
        seen_row: Dict[int, int] = {}  # value -> co
        for col in range(9):
            value = board[row][col]
            if value == 0:
                continue
            if value in seen_row:
                bad |= {row * 9 + col, row * 9 + seen_row[value]}
            else:
                seen_row[value] = col
    return bad


def _col_conflicts(board: Board) -> Set[int]:
    bad: Set[int] = set()

    for col in range(9):
        seen_col: Dict[int, int] = {}  # value -> row
        for row in range(9):
            value = board[row][col]
            if value == 0:
                continue
            if value in seen_col:
                bad |= {row * 9 + col, seen_col[value] * 9 + col}
            else:
                seen_col[value] = row

    return bad


def _box_conflicts(board: Board) -> Set[int]:
    bad: Set[int] = set()
    for board_row in range(0, 9, 3):
        for board_col in range(0, 9, 3):
            seen_box: Dict[int, Tuple[int, int]] = {}  # value -> (row, col)
            for i in range(3):
                for j in range(3):
                    row, col = board_row + i, board_col + j
                    value = board[row][col]
                    if value == 0:
                        continue
                    if value in seen_box:
                        rr, cc = seen_box[value]  # type ignore
                        bad |= {row * 9 + col, rr * 9 + cc}
                    else:
                        seen_box[value] = (row, col)
    return bad


def _conflicts(state: str) -> tuple[list[int], bool]:
    board = from_str(state)
    bad = _row_conflicts(board) | _col_conflicts(board) | _box_conflicts(board)
    full = all(board[r][c] != 0 for r in range(9) for c in range(9))
    return sorted(bad), full


@router.post("/validate", response_model=schemas.ValidateResp)
def validate(req: schemas.ValidateReq):
    state = req.board.state or req.board.puzzle
    bad, full = _conflicts(state)
    return schemas.ValidateResp(
        valid=len(bad) == 0, complete=(len(bad) == 0 and full), conflicts=bad
    )


@router.post("/solve", response_model=schemas.SolveResp)
def solve(req: schemas.SolveReq):
    state = req.board.state or req.board.puzzle
    b = from_str(state)
    if not solve_backtrack(b):
        raise HTTPException(400, "Unsolvable")
    return schemas.SolveResp(solution=to_str(b))


@router.post("/new", response_model=schemas.NewGameResp)
def new(req: schemas.NewGameReq):
    puzzle, solution = generate_puzzle(req.seed, req.difficulty.clues)
    return schemas.NewGameResp(
        difficulty=req.difficulty, puzzle=puzzle, solution=solution
    )
