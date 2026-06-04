import random

SIZE  = 22
EMPTY = "."


# ── Grid helpers ──────────────────────────────────────────────────────────────

def _make_grid():
    return [[EMPTY] * SIZE for _ in range(SIZE)]


def _deltas(direction):
    """Return (row_delta, col_delta) for a given direction."""
    return (1, 0) if direction == "D" else (0, 1)


def _can_place(grid, word, row, col, direction):
    """Return True if word fits at (row, col) without conflicting neighbours."""
    dr, dc = _deltas(direction)

    # cell immediately before the word must be empty
    br, bc = row - dr, col - dc
    if 0 <= br < SIZE and 0 <= bc < SIZE and grid[br][bc] != EMPTY:
        return False

    # cell immediately after the word must be empty
    er, ec = row + dr * len(word), col + dc * len(word)
    if 0 <= er < SIZE and 0 <= ec < SIZE and grid[er][ec] != EMPTY:
        return False

    for i, ch in enumerate(word):
        r, c = row + dr * i, col + dc * i

        if r >= SIZE or c >= SIZE or r < 0 or c < 0:
            return False

        cell = grid[r][c]

        if cell == ch:
            continue          # shared crossing letter — fine

        if cell != EMPTY:
            return False      # letter conflict

        # perpendicular neighbours of a new (non-crossing) cell must be empty
        for pr, pc in [(r - dc, c - dr), (r + dc, c + dr)]:
            if 0 <= pr < SIZE and 0 <= pc < SIZE and grid[pr][pc] != EMPTY:
                return False

    return True


def _place_word(grid, word, row, col, direction):
    dr, dc = _deltas(direction)
    for i, ch in enumerate(word):
        grid[row + dr * i][col + dc * i] = ch


def _count_crossings(grid, word, row, col, direction):
    """Count how many letters of word overlap with existing letters."""
    dr, dc = _deltas(direction)
    return sum(
        1 for i, ch in enumerate(word)
        if grid[row + dr * i][col + dc * i] == ch
    )


# ── Puzzle generation ─────────────────────────────────────────────────────────

def _generate(words):
    """
    Place words on the grid and return (grid, placed).
    placed is a list of (word, clue, row, col, direction) tuples.
    """
    grid   = _make_grid()
    placed = []
    pool   = list(words)
    random.shuffle(pool)

    # Place the first word across the centre
    w0, c0 = pool[0]
    r0     = SIZE // 2
    col0   = (SIZE - len(w0)) // 2
    _place_word(grid, w0, r0, col0, "A")
    placed.append((w0, c0, r0, col0, "A"))

    for word, clue in pool[1:]:
        best       = None
        best_score = -1

        for p_word, _, p_row, p_col, p_dir in placed:
            alt_dir    = "D" if p_dir == "A" else "A"
            p_dr, p_dc = _deltas(p_dir)
            a_dr, a_dc = _deltas(alt_dir)

            for pi, pch in enumerate(p_word):
                for li, lch in enumerate(word):
                    if lch != pch:
                        continue

                    # intersection point on the already-placed word
                    ir, ic = p_row + p_dr * pi, p_col + p_dc * pi

                    # start of the new word so letter li lands at (ir, ic)
                    nr, nc = ir - a_dr * li, ic - a_dc * li

                    if nr < 0 or nc < 0:
                        continue
                    if not _can_place(grid, word, nr, nc, alt_dir):
                        continue

                    score = _count_crossings(grid, word, nr, nc, alt_dir)
                    if score > best_score:
                        best_score = score
                        best = (word, clue, nr, nc, alt_dir)

        if best:
            _place_word(grid, best[0], best[2], best[3], best[4])
            placed.append(best)

    return grid, placed


def _crop(grid, placed):
    """Trim the grid to the bounding box of placed words."""
    all_r = (
        [r for _, _, r, c, d in placed] +
        [r + (len(w) if d == "D" else 1) - 1 for w, _, r, c, d in placed]
    )
    all_c = (
        [c for _, _, r, c, d in placed] +
        [c + (len(w) if d == "A" else 1) - 1 for w, _, r, c, d in placed]
    )
    r0, r1 = min(all_r), max(all_r) + 1
    c0, c1 = min(all_c), max(all_c) + 1

    cropped = [row[c0:c1] for row in grid[r0:r1]]
    adjusted = [(w, cl, r - r0, c - c0, d) for w, cl, r, c, d in placed]
    return cropped, adjusted


def _number_starts(placed):
    """
    Assign crossword numbers to word-start cells, ordered top-to-bottom
    then left-to-right.  Returns {(row, col): number}.
    """
    unique_starts = sorted({(r, c) for _, _, r, c, _ in placed})
    return {pos: i + 1 for i, pos in enumerate(unique_starts)}


# ── Public API ────────────────────────────────────────────────────────────────

def build_puzzle(words):
    """
    Generate a crossword from a list of (word, clue) tuples.

    Returns a dict ready to serialise as JSON:
        {
            rows, cols,
            cells:  [{r, c, empty, number?}, ...],
            across: [{num, clue, length, row, col, dir, word}, ...],
            down:   [...],
        }
    """
    # Retry up to 10 times to get a puzzle with at least 5 words placed
    grid, placed = _generate(words), None
    for _ in range(10):
        grid, placed = _generate(words)
        if len(placed) >= 5:
            break

    grid, placed = _crop(grid, placed)
    nums = _number_starts(placed)

    # Build flat cell list
    cells = []
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            cell = {"r": r, "c": c, "empty": ch == EMPTY}
            if ch != EMPTY:
                cell["number"] = nums.get((r, c))
            cells.append(cell)

    # Build clue lists
    clues_across, clues_down = [], []
    for w, cl, r, c, d in placed:
        entry = {
            "num":    nums[(r, c)],
            "clue":   cl,
            "length": len(w),
            "row":    r,
            "col":    c,
            "dir":    d,
            "word":   w,
        }
        (clues_across if d == "A" else clues_down).append(entry)

    clues_across.sort(key=lambda x: x["num"])
    clues_down.sort(key=lambda x:   x["num"])

    return {
        "rows":   len(grid),
        "cols":   len(grid[0]),
        "cells":  cells,
        "across": clues_across,
        "down":   clues_down,
    }