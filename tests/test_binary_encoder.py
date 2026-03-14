from src.binary_encoder import SudokuEncoder
from src.puzzle_engine import SudokuPuzzle


def test_encoder_mapping_and_valid_bitstrings():
    puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
    encoder = SudokuEncoder(puzzle)
    assert encoder.mapping["n_value_qubits"] == 3
    valid = encoder.get_valid_bitstrings()
    assert len(valid) == 1


def test_bitstring_decode_qiskit_ordering():
    puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
    encoder = SudokuEncoder(puzzle)
    bitstring = encoder.get_valid_bitstrings()[0]
    grid = encoder.decode_bitstring(bitstring)
    assert grid == [[1, 0], [0, 1]]
