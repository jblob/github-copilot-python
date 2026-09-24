import sudoku_logic


def test_create_empty_board_has_expected_shape():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_generate_puzzle_preserves_solution_and_clue_count():
    clues = 40
    puzzle, solution = sudoku_logic.generate_puzzle(clues)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
    assert all(sorted(row) == list(range(1, sudoku_logic.SIZE + 1)) for row in solution)
    assert all(
        solution[row][col] == puzzle[row][col]
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] != sudoku_logic.EMPTY
    )


def test_is_safe_rejects_existing_row_column_and_box_values():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1

    assert not sudoku_logic.is_safe(board, 0, 1, 1)
    assert not sudoku_logic.is_safe(board, 1, 0, 1)
    assert not sudoku_logic.is_safe(board, 1, 1, 1)
    assert sudoku_logic.is_safe(board, 1, 1, 2)