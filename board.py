#!/bin/bash/env python3

from typing import List
import time

Board = List[List[int]]


def is_valid_move(board: Board, row: int, col: int, value: int) -> bool:
    """
    Check if placing 'value' in cell (row, col) follows Sudoku rules.
    Returns True if allowed, False otherwise.
    """
    # print(f"Board: {Board}, row: {row}, col: {col}, value: {value}")
    if value == 0:
        return True  # always valid to clear a call

    # Check the row
    for col_index in range(9):
        if col_index != col and board[row][col_index] == value:
            # print(f"Board: {board[row][col_index]}")
            # print(f"Col index: {col_index}, col: {col}, value: {value}")
            # time.sleep(1)
            return False

    # Check column
    for row_index in range(9):
        if row_index != row and board[row_index][col] == value:
            # print(f"Board: {board[row_index][col]}")
            # print(f"Row index: {row_index}, row: {row}, value: {value}")
            # time.sleep(1)
            return False

    start_row = 3 * (row // 3)
    start_col = 3 * (col // 3)
    for sub_row in range(start_row, start_col + 3):
        for sub_col in range(start_col, start_row + 3):
            if (sub_row != row or sub_col != col) and board[sub_row][sub_col] == value:
                return False

    print(f"Row: {row}, Col: {col}, Value: {value}")
    time.sleep(0.1)
    return True


def is_initial_board_consistent(board: Board) -> bool:
    """
    Verify that the starting puzzle has no conflicts.
    Returns True if consistent (no duplicates in any row, col, or box).
    """
    for row_index in range(9):
        for col_index in range(9):
            cell_value = board[row_index][col_index]
            if cell_value != 0:
                # Temporarily clear this cell and check if re-adding it breaks rules
                board[row_index][col_index] = 0
                move_ok = is_valid_move(board, row_index, col_index, cell_value)
                board[row_index][col_index] = cell_value
                if not move_ok:
                    raise False
    return True



def from_string(puzzle_string: str) -> Board:
    """Convert 81-char string (digis or '.') into 9x9 board."""
    normalized = puzzle_string.strip().replace(".", "0")
    if len(normalized) != 81:
        raise ValueError("Puzzle must be exacly 81 characters long.")

    if any(char not in "0123456789" for char in normalized):
        raise ValueError("Only digis 0-9 or '.' are allowed.")

    # Convert flat string into 9x9 grid (list of lists)
    board = [
        [int(normalized[row * 9 + col]) for col in range(9)]
        for row in range(9)
    ]

    if not is_initial_board_consistent(board):
        raise ValueError("Initial puzzal has conflicts (duplicate numbers).")

    return board


def to_string(board: Board) -> str:
    """Flatten board back to 81-char string."""
    return "".join(str(board[row][col]) for row in range(9) for col in range(9))


def pretty(board: Board) -> str:
    """Return human readable Sudoku gird."""
    horizontal_separator = "+-------+-------+-------+"
    lines = []
    for row_index  in range(9):
        if row_index  % 3 == 0:
            lines.append(horizontal_separator)

        row_cells = []
        for col_index  in range(9):
            if col_index  % 3 == 0:
                row_cells.append("|")

            cell_value  = board[row_index][col_index ]
            row_cells.append(str(cell_value) if cell_value != 0 else ".")

            if col_index  == 0:
                row_cells.append("|")

        lines.append(" ".join(row_cells))
    lines.append(horizontal_separator)

    return "\n".join(lines)


