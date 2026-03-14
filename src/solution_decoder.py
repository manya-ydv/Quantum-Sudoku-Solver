from typing import Dict, List, Tuple

from .binary_encoder import SudokuEncoder
from .puzzle_engine import SudokuPuzzle


class SudokuDecoder:
    def __init__(self, encoder: SudokuEncoder, puzzle: SudokuPuzzle):
        self.encoder = encoder
        self.puzzle = puzzle

    def decode_bitstring(self, bitstring: str) -> List[List[int]]:
        return self.encoder.decode_bitstring(bitstring)

    def decode_counts(self, counts: Dict[str, int]) -> List[Dict]:
        total = sum(counts.values()) if counts else 1
        results = []
        for bitstring, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
            grid = self.decode_bitstring(bitstring)
            is_valid, violations = self.verify_solution(grid)
            results.append(
                {
                    "bitstring": bitstring,
                    "count": count,
                    "probability": count / total,
                    "grid": grid,
                    "is_valid": is_valid,
                    "violations": violations,
                }
            )
        return results

    def verify_solution(self, grid: List[List[int]]) -> Tuple[bool, List[str]]:
        violations = []
        if len(grid) != self.puzzle.size or any(len(row) != self.puzzle.size for row in grid):
            return False, ["invalid-grid-shape"]

        for r in range(self.puzzle.size):
            for c in range(self.puzzle.size):
                clue = self.puzzle.grid[r][c]
                if clue is not None and grid[r][c] != clue:
                    violations.append(f"clue-mismatch@({r},{c})")

        for (a_r, a_c), (b_r, b_c) in self.puzzle.get_constraints():
            if grid[a_r][a_c] == grid[b_r][b_c]:
                violations.append(f"constraint-fail@({a_r},{a_c})!=({b_r},{b_c})")

        return len(violations) == 0, violations

    def format_solution(self, grid: List[List[int]]) -> str:
        rows = []
        for r in range(self.puzzle.size):
            row = []
            for c in range(self.puzzle.size):
                if self.puzzle.grid[r][c] is None:
                    row.append(f"[{grid[r][c]}]")
                else:
                    row.append(str(grid[r][c]))
            rows.append(" ".join(row))
        return "\n".join(rows)
