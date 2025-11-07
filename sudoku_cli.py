from random import sample, shuffle
from copy import deepcopy
import time

SIZE = 9
BOX = 3
DIGITS = list(range(1, 10))

def empty_board():
    return [[0 for _ in range(SIZE)] for _ in range(9)]

def clone(board):
    return [row[:] for row in board]

def print_board(board):
    line = "+-------+-------+-------+"
    print(line)
    for row in range(SIZE):
        row_chunks = []
        for col in range(SIZE):
            val = board[row][col]
            if col == 0:
                row_chunks.append("|")
            row_chunks.append(str(val) if val != 0 else ".")
            if col % BOX == BOX - 1 and col != SIZE - 1:
                row_chunks.append("|")
        print(" ".join(row_chunks) + " |")
        if row % BOX == BOX - 1 and row != SIZE - 1:
            print(line)
    print(line)

def row_ok(board, row, value):
    """ Check value user input already in board[row] or not"""
    return value not in board[row]

def col_ok(board, col, value):
    """Check value user input already in board[col] or not"""
    return all(board[row][col] != value for row in range(SIZE))

def box_ok(board, row, col, value):
    """Check value already in box 3x3 or not"""
    row_ = (row // BOX) * BOX # row 4 -> row_ = 3 (0 1 2 3 4 5 6 7 8)
    col_ = (col // BOX) * BOX # col 7 -> row_ = 6 (0 1 2 3 4 5 6 7 8)
    for row_v in range(row_, row_ + BOX):
        for col_v in range(col_, col_ + BOX):
            if board[row_v][col_v] == value: # if value already in box -> False
                return False
    return True

def valid(board, row, col, value):
    return row_ok(board, row, value) and col_ok(board, col, value) and box_ok(board, row, col, value)

def find_empty(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == 0:
                return row, col
    return None # solved

def solve(board):
    spot = find_empty(board)
    if not spot:
        return True
    row, col = spot

    # Create a list [1, 2, 3, 4, 5, 6, 7, 8, 9]
    candidates = DIGITS[:]
    shuffle(candidates)

    # loop each value in candidates after shuffle
    for val in candidates:
        # check val valid or not
        if valid(board, row, col, val):

            # fill board[row][col] value from user
            board[row][col] = val

            # loop itself for full board
            if solve(board):
                return True
            board[row][col] = 0
    return False

def generate_full_solution():
    board = empty_board()
    # seed a few random values in each box to diversify layouts
    for board_row in range(0, SIZE, BOX):
        for board_col in range(0, SIZE, BOX):
            choose = sample(list(DIGITS), BOX) # 3 random digits into diagonal-like spread
            for i in range(BOX):
                row, col = board_row + i, board_col + i
                if board[row][col] == 0 and valid(board, row, col, choose[i]):
                    board[row][col] == choose[i]
    solve(board)
    return board

def make_puzzle(holes=45):
    full = generate_full_solution()
    puzzle = clone(full)

    # remove 'holes' cells at random positions
    coords = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    shuffle(coords)
    removed = 0

    for row, col in coords:
        if removed >= holes:
            break
        if puzzle[row][col] != 0:
            puzzle[row][col] = 0
            removed += 1
    return puzzle, full

def same_board(a, b):
    for row in range(SIZE):
        for col in range(SIZE):
            if a[row][col] != b[row][col]:
                return False
    return True

def run_cli(holes):
    puzzle, solution = make_puzzle(holes=holes)
    fixed = [[puzzle[row][col] != 0 for col in range(SIZE)] for row in range(SIZE)]
    working = clone(puzzle)

    print("\nSudoku! Input as: row col value   (1..9). Commands: 'solve', 'clear', 'quit'")
    print_board(working)

    while True:
        cmd = input("> ").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("bye!")
            return
        if cmd in ("s", "solve"):
            working = clone(solution)
            print_board(working)
            print("Solved.")
            return
        if cmd in ("c", "clear"):
            working = clone(puzzle)
            print_board(working)
            continue

        # user input
        try:
            row, col, val = map(int, cmd.split())
            if not (1 <= row <= 9 and 1 <= col <= 9 and 1 <= val <= 9):
                raise ValueError
            row -= 1; col -= 1

        except Exception:
            print("format: row col value  (all 1..9), or 'solve', 'clear', 'quit'")
            continue

        if fixed[row][col]:
            print("That cell is fixed.")
            continue
        if valid(working, row, col, val):
            print(working[row][col])
            working[row][col] = val
        else:
            print("invalid move (conflict in row/col/box).")
            continue

        print_board(working)
        if same_board(working, solution):
            print("you did it! 🎉")
            return


if __name__ == "__main__":
    run_cli(60) # increase holes (e.g. 50) for a harder puzzle
