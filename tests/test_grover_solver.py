import pytest

pytest.importorskip("qiskit")

from src.grover_solver import QuantumSudokuSolver
from src.puzzle_engine import SudokuPuzzle


def test_solver_manual_2x2_one_clue():
    puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
    solver = QuantumSudokuSolver(puzzle)
    result = solver.solve(approach="manual", shots=512)
    assert result["is_valid"] is True
