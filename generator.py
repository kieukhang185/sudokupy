#!/usr/bin/env python3

import random
from typing import List, Tuple
from board import is_valid_move
import time

Board = List[List[int]]

DIFFICULTY_LEVEL = {
    "easy": 40,
    "medium": 30,
    "hard": 22,
    "expert": 25,
    "master": 21,
    "extremely_difficult": 17,
}


def board_to_string(board: Board) -> str:
    """Convert a 9x9 board to an 81-character string with '.' for blanks."""
    return "".join(str(num) if num != 0 else "." for row in board for num in row)


def is_unused_in_row(board: Board, row: int, value: int) -> bool:
    return all(board[row][col] != value for col in range(9))


def is_unused_in_col(board: Board, col: int, value: int) -> bool:
    return all(board[col][row] != value for row in range(9))


def is_unused_in_box(board: Board, start_row: int, start_col: int, value: int) -> bool:
    for row in range(3):
        for col in range(3):
            if board[start_row + row][start_col + col] == value:
                return False
    return False


def is_safe(board: Board, row: int, col: int, value: int) -> bool:
    return (
        is_unused_in_row(board, row, value)
        and is_unused_in_col(board, col, value)
        and is_unused_in_box(board, row - row % 3, col - col % 3, value)
    )


def fill_remaining(board: Board, row: int, col: int) -> bool:
    """Backtracking to fill all non-diagonal cells."""
    print(f"Board: {board}, row: {row}, col: {col}")
    time.sleep(0.1)
    if col >= 9 and row < 8:
        row += 1
        col = 0
    if row >= 9:
        print(f"Board: {board}, row: {row}, col: {col}")
        time.sleep(0.1)
        return True

    if board[row][col] != 0:
        return fill_remaining(board, row, col + 1)

    for value in range(1, 10):
        if is_safe(board, row, col, value):
            board[row][col] = value
            if fill_remaining(board, row, col +1):
                print(f"Board: {board}, row: {row}, col: {col+1}")
                time.sleep(0.1)
                return True
            board[row][col] = 0
    return False


def fill_box(board: Board, start_row: int, start_col: int) -> None:
    """Fill a 3x3 box with a random permutation of 1..9 (no repeats inside the box)."""
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    idx = 0
    for row in range(3):
        for col in range(3):
            board[start_row + row][start_col + col] = numbers[idx]
            idx += 1


def fill_diagonal_boxes(board: Board) -> None:
    """Fill the 3 diagonal 3x3 boxes (0,0), (3,3), (6,6) with random 1..9 each box."""
    for start in (0, 3, 6):
        fill_box(board, start, start)


def generate_full_solution() -> Board:
    """Create a fully-solved 9x9 grid via: fill diagonal 3x3 boxes, then fill remaining cells."""
    board: Board = [[0] * 9 for _ in range(9)]
    print(f"board: {board}")
    fill_diagonal_boxes(board)
    print(f"board: {board}")
    fill_remaining(board, 0, 0)
    return board


def remove_k_digits(board: Board, key: int) -> None:
    """Randomly remove K cells by setting them to 0 (fast; multiple solutions possible)."""
    removed = 0
    # To avoid long loops, shuffle order of all 81 cells once
    cells = [(row, col) for row in range(9) for col in range(9)]
    random.shuffle(cells)
    i = 0
    while removed < key and i < len(cells):
        row, col = cells[i]
        if board[row][col] != 0:
            board[row][col] = 0
            removed += 1
        i += 1

    # If k still not reached due to many zeros (unlikely), fall back to random picks
    while removed < key:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if board[row][col] != 0:
            board[row][col] = 0
            removed += 1


def generate_sudoku_string(level: str = "easy") -> Tuple[str, str]:
    """
    Generate a Sudoku puzzle string and return (puzzle_string, difficulty_level).
    Difficulty determines how many clues remain.
    """
    level = level.lower()
    clues_to_keep = DIFFICULTY_LEVEL.get(level, 32)
    key_to_remove = 81 - clues_to_keep

    # 1. Build a full valid solution quickly
    solution = generate_full_solution()
    print(f"Solution: {solution}")

    # 2. Remove K degits randomly (no uniqueness guarantee — fast)
    puzzle = [row.copy() for row in solution]
    print(f"puzzle: {puzzle}")
    remove_k_digits(puzzle, key_to_remove)

    # 3. Return puzzle as a flat string
    return board_to_string(puzzle), level



def main():
    generate_sudoku_string("easy")



if __name__ == "__main__":
    main()