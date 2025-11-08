def is_board_str(s: str) -> bool:
    return isinstance(s, str) and len(s) == 81 and all(ch.isdigit() for ch in s)


def count_clues(puzzle: str) -> int:
    return sum(1 for ch in puzzle if ch != "0")
