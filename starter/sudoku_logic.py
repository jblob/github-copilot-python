import copy
import logging
import random

SIZE = 9
EMPTY = 0
logger = logging.getLogger(__name__)


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


def count_solutions(board, limit=2):
    """Count solutions, stopping once the requested limit is reached."""
    all_values = (1 << SIZE) - 1
    row_masks = [0] * SIZE
    col_masks = [0] * SIZE
    box_masks = [0] * SIZE
    empty_cells = []

    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                empty_cells.append((row, col))
                continue
            bit = 1 << (value - 1)
            box = (row // 3) * 3 + col // 3
            if (
                row_masks[row] & bit
                or col_masks[col] & bit
                or box_masks[box] & bit
            ):
                return 0
            row_masks[row] |= bit
            col_masks[col] |= bit
            box_masks[box] |= bit

    def search(remaining):
        if not remaining:
            return 1

        best_index = 0
        best_candidates = all_values
        for index, (row, col) in enumerate(remaining):
            box = (row // 3) * 3 + col // 3
            candidates = all_values & ~(
                row_masks[row] | col_masks[col] | box_masks[box]
            )
            if candidates.bit_count() < best_candidates.bit_count():
                best_index = index
                best_candidates = candidates
                if candidates.bit_count() <= 1:
                    break
        if best_candidates == 0:
            return 0

        row, col = remaining[best_index]
        box = (row // 3) * 3 + col // 3
        rest = remaining[:best_index] + remaining[best_index + 1:]
        total = 0
        while best_candidates:
            bit = best_candidates & -best_candidates
            best_candidates -= bit
            row_masks[row] |= bit
            col_masks[col] |= bit
            box_masks[box] |= bit
            total += search(rest)
            row_masks[row] ^= bit
            col_masks[col] ^= bit
            box_masks[box] ^= bit
            if total >= limit:
                return total
        return total

    return search(empty_cells)


def generate_puzzle(clues=35):
    while True:
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
        random.shuffle(cells)

        for row, col in cells:
            filled = sum(
                cell != EMPTY
                for current_row in board
                for cell in current_row
            )
            if filled <= clues:
                return deep_copy(board), solution
            value = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(board) > 1:
                logger.warning(
                    'Generated puzzle has multiple solutions; '
                    'trying a new puzzle candidate.'
                )
                board[row][col] = value

        filled = sum(
            cell != EMPTY
            for current_row in board
            for cell in current_row
        )
        if filled <= clues:
            return deep_copy(board), solution
        logger.warning(
            'Generated puzzle could not reach the requested clue count; '
            'generating a new puzzle.'
        )
