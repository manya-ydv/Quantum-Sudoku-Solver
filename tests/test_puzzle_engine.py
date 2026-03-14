from src.puzzle_engine import SudokuPuzzle


def test_2x2_constraints_and_unknowns():
    puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
    assert puzzle.get_num_unknowns() == 3
    constraints = puzzle.get_constraints()
    assert len(constraints) == 4


def test_validate_solution():
    puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
    assert puzzle.validate_solution([[1, 0], [0, 1]])
    assert not puzzle.validate_solution([[1, 1], [0, 1]])
