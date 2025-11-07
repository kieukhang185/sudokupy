# sudoku_pygame.py
import pygame
import sys

from sudoku_cli import SIZE, clone, valid, make_puzzle, same_board
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

# --------------------------
# Pygame UI
# --------------------------
WIDTH = 540   # 60px per cell
HEIGHT = 620  # extra space for footer UI
GRID_SIZE = 540
CELL = GRID_SIZE // SIZE
MARGIN_TOP = 20
MARGIN_LEFT = 20
BOARD_TOP = MARGIN_TOP
BOARD_LEFT = MARGIN_LEFT
FOOTER_Y = GRID_SIZE + 40

BG = (245, 246, 248)
GRID = (40, 40, 40)
SUBGRID = (100, 100, 100)
TXT = (25, 25, 25)
FIXED_TXT = (30, 60, 130)
USER_TXT = (20, 20, 20)
HINT_TXT = (0, 120, 0)
HL_CELL = (190, 220, 255)
HL_SAME = (220, 235, 255)
HL_CONFLICT = (255, 200, 200)
WIN_BANNER = (0, 150, 80)

def draw_grid(screen):
    # Cell outlines + subgrid thick lines
    for i in range(SIZE + 1):
        x = BOARD_LEFT + i * CELL
        y = BOARD_TOP + i * CELL
        width = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, SUBGRID if i % 3 == 0 else GRID, (BOARD_LEFT, y), (BOARD_LEFT + GRID_SIZE, y), width)
        pygame.draw.line(screen, SUBGRID if i % 3 == 0 else GRID, (x, BOARD_TOP), (x, BOARD_TOP + GRID_SIZE), width)

def draw_numbers(screen, font, working, fixed, sel, show_conflicts=True):
    # optional conflict highlighting
    conflicts = set()
    if show_conflicts:
        # any duplicates in row/col/box for placed numbers
        for r in range(SIZE):
            for c in range(SIZE):
                v = working[r][c]
                if v == 0: 
                    continue
                # temporarily clear, test validity – if invalid, mark conflict
                working[r][c] = 0
                if not valid(working, r, c, v):
                    conflicts.add((r, c))
                working[r][c] = v

    # highlight: selected cell and same numbers
    if sel is not None:
        sr, sc = sel
        if working[sr][sc] != 0:
            target = working[sr][sc]
            for r in range(SIZE):
                for c in range(SIZE):
                    if working[r][c] == target:
                        rect = pygame.Rect(BOARD_LEFT + c*CELL + 1, BOARD_TOP + r*CELL + 1, CELL-2, CELL-2)
                        pygame.draw.rect(screen, HL_SAME, rect)

        # selected cell on top
        rect = pygame.Rect(BOARD_LEFT + sc*CELL + 1, BOARD_TOP + sr*CELL + 1, CELL-2, CELL-2)
        pygame.draw.rect(screen, HL_CELL, rect)

    # draw numbers
    for r in range(SIZE):
        for c in range(SIZE):
            v = working[r][c]
            if v == 0:
                continue
            color = FIXED_TXT if fixed[r][c] else USER_TXT
            if (r, c) in conflicts:
                color = HL_CONFLICT
            img = font.render(str(v), True, color)
            x = BOARD_LEFT + c * CELL + CELL//2 - img.get_width()//2
            y = BOARD_TOP + r * CELL + CELL//2 - img.get_height()//2
            screen.blit(img, (x, y))

def draw_footer(screen, small_font, message):
    info = "Arrows/Click: move • 1–9: set • 0/Backspace/Delete: erase • H: hint • C: clear • S: solve • N: new • Q: quit"
    img = small_font.render(info, True, TXT)
    screen.blit(img, (MARGIN_LEFT, FOOTER_Y))
    if message:
        msg = small_font.render(message, True, TXT)
        screen.blit(msg, (MARGIN_LEFT, FOOTER_Y + 24))

def cell_at_pos(pos):
    x, y = pos
    if not (BOARD_LEFT <= x < BOARD_LEFT + GRID_SIZE and BOARD_TOP <= y < BOARD_TOP + GRID_SIZE):
        return None
    c = (x - BOARD_LEFT) // CELL
    r = (y - BOARD_TOP) // CELL
    return int(r), int(c)

def main():
    pygame.init()
    pygame.display.set_caption("Sudoku (Pygame)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 42)
    small_font = pygame.font.SysFont(None, 22)
    banner_font = pygame.font.SysFont(None, 56)

    def new_game(holes=45):
        p, s = make_puzzle(holes=holes)
        f = [[p[r][c] != 0 for c in range(SIZE)] for r in range(SIZE)]
        return p, s, clone(p), f

    puzzle, solution, working, fixed = new_game(holes=47)
    sel = (0, 0)  # selected cell
    message = ""
    won = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                picked = cell_at_pos(event.pos)
                if picked:
                    sel = picked

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    r, c = sel
                    sel = (r, (c + 1) % SIZE)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    r, c = sel
                    sel = (r, (c - 1) % SIZE)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    r, c = sel
                    sel = ((r + 1) % SIZE, c)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    r, c = sel
                    sel = ((r - 1) % SIZE, c)
                elif event.key in (pygame.K_0, pygame.K_DELETE, pygame.K_BACKSPACE):
                    r, c = sel
                    if not fixed[r][c] and not won:
                        working[r][c] = 0
                        message = ""
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    r, c = sel
                    if not fixed[r][c] and not won:
                        v = event.key - pygame.K_0
                        if valid(working, r, c, v):
                            working[r][c] = v
                            message = ""
                            if same_board(working, solution):
                                won = True
                        else:
                            # keep it gentle; show conflict message
                            working[r][c] = v  # temporarily place to highlight conflicts in red
                            # if you prefer not to place on invalid, comment the line above
                            message = f"'{v}' conflicts with row/col/box. (Shown in red.)"
                elif event.key == pygame.K_h:
                    # hint: fill selected from solution if not fixed
                    r, c = sel
                    if not fixed[r][c] and not won and solution[r][c] != 0:
                        working[r][c] = solution[r][c]
                        message = "Hint used."
                        if same_board(working, solution):
                            won = True
                elif event.key == pygame.K_c:
                    working = clone(puzzle)
                    won = False
                    message = "Cleared to starting puzzle."
                elif event.key == pygame.K_s:
                    working = clone(solution)
                    won = True
                    message = "Solved."
                elif event.key == pygame.K_n:
                    puzzle, solution, working, fixed = new_game(holes=47)
                    sel = (0, 0)
                    won = False
                    message = "New puzzle."

        screen.fill(BG)
        draw_grid(screen)
        draw_numbers(screen, font, working, fixed, sel, show_conflicts=True)

        if won:
            banner = banner_font.render("You solved it! 🎉", True, WIN_BANNER)
            screen.blit(banner, (MARGIN_LEFT, GRID_SIZE + 5))

        draw_footer(screen, small_font, message)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
