from src.binary_encoder import SudokuEncoder
from src.puzzle_engine import SudokuPuzzle
from src.solution_decoder import SudokuDecoder


def test_decode_counts_and_verify():
    puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
    encoder = SudokuEncoder(puzzle)
    decoder = SudokuDecoder(encoder, puzzle)
    valid_state = encoder.get_valid_bitstrings()[0]
    decoded = decoder.decode_counts({valid_state: 100})
    assert decoded[0]["is_valid"] is True
