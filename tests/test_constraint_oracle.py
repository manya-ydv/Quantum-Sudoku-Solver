import pytest

pytest.importorskip("qiskit")

from src.binary_encoder import SudokuEncoder
from src.constraint_oracle import SudokuOracle
from src.puzzle_engine import SudokuPuzzle


def test_oracle_build_and_verify_map():
    puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
    encoder = SudokuEncoder(puzzle)
    oracle = SudokuOracle(encoder)
    qc = oracle.build_oracle()
    assert qc.num_qubits == encoder.mapping["n_value_qubits"]
    verify = oracle.verify_oracle(qc)
    assert any(verify.values())
