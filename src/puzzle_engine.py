import itertools
import json
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


Cell = Tuple[int, int]


def _combinations(cells: List[Cell]) -> List[Tuple[Cell, Cell]]:
    return [(a, b) for a, b in itertools.combinations(cells, 2)]


@dataclass
class SudokuPuzzle:
    size: int = 2
    grid: Optional[List[List[Optional[int]]]] = None

    def __post_init__(self) -> None:
        if self.size not in (2, 4):
            raise ValueError("Only size 2 and 4 are supported in this project")
        if self.grid is None:
            self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self._validate_grid_shape()
        self._validate_grid_values(self.grid)

    @property
    def block_size(self) -> int:
        return 1 if self.size == 2 else 2

    @classmethod
    def from_json(cls, filepath: str) -> "SudokuPuzzle":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(size=data["size"], grid=data["grid"])

    @classmethod
    def from_string(cls, puzzle_str: str) -> "SudokuPuzzle":
        rows = [row.strip() for row in puzzle_str.split("|")]
        parsed_rows: List[List[Optional[int]]] = []
        for row in rows:
            tokens = row.split()
            parsed_rows.append([None if tok in {"_", "?", "."} else int(tok) for tok in tokens])
        size = len(parsed_rows)
        return cls(size=size, grid=parsed_rows)

    def _validate_grid_shape(self) -> None:
        if len(self.grid) != self.size:
            raise ValueError("Grid row count must match puzzle size")
        for row in self.grid:
            if len(row) != self.size:
                raise ValueError("Grid column count must match puzzle size")

    def _validate_grid_values(self, grid: List[List[Optional[int]]]) -> None:
        for row in grid:
            for value in row:
                if value is None:
                    continue
                if not isinstance(value, int):
                    raise ValueError("Grid values must be int or None")
                if not (0 <= value < self.size):
                    raise ValueError(f"Grid value {value} out of range [0, {self.size - 1}]")

    def get_empty_cells(self) -> List[Cell]:
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.grid[r][c] is None]

    def get_clue_cells(self) -> Dict[Cell, int]:
        return {(r, c): self.grid[r][c] for r in range(self.size) for c in range(self.size) if self.grid[r][c] is not None}

    def get_constraints(self) -> List[Tuple[Cell, Cell]]:
        constraints = set()
        for r in range(self.size):
            row_cells = [(r, c) for c in range(self.size)]
            constraints.update(_combinations(row_cells))
        for c in range(self.size):
            col_cells = [(r, c) for r in range(self.size)]
            constraints.update(_combinations(col_cells))

        if self.size == 4:
            b = self.block_size
            for br in range(0, self.size, b):
                for bc in range(0, self.size, b):
                    block_cells = [(br + dr, bc + dc) for dr in range(b) for dc in range(b)]
                    constraints.update(_combinations(block_cells))
        return sorted(constraints)

    def get_constraint_pairs_for_unknowns(self) -> List[Tuple[Cell, Cell, Optional[int], Optional[int]]]:
        pairs = []
        for cell_a, cell_b in self.get_constraints():
            val_a = self.grid[cell_a[0]][cell_a[1]]
            val_b = self.grid[cell_b[0]][cell_b[1]]
            if val_a is None or val_b is None:
                pairs.append((cell_a, cell_b, val_a, val_b))
        return pairs

    def validate_solution(self, solution_grid: List[List[int]]) -> bool:
        if len(solution_grid) != self.size or any(len(row) != self.size for row in solution_grid):
            return False
        for r in range(self.size):
            for c in range(self.size):
                v = solution_grid[r][c]
                if not isinstance(v, int) or not (0 <= v < self.size):
                    return False
                clue = self.grid[r][c]
                if clue is not None and clue != v:
                    return False

        for (a_r, a_c), (b_r, b_c) in self.get_constraints():
            if solution_grid[a_r][a_c] == solution_grid[b_r][b_c]:
                return False
        return True

    def display(self, highlight_unknowns: bool = True) -> str:
        rows = []
        for r in range(self.size):
            items = []
            for c in range(self.size):
                v = self.grid[r][c]
                if v is None:
                    items.append("_" if highlight_unknowns else " ")
                else:
                    items.append(str(v))
            rows.append(" ".join(items))
        return "\n".join(rows)

    @classmethod
    def generate_random(cls, size: int, n_clues: int) -> "SudokuPuzzle":
        if size not in (2, 4):
            raise ValueError("Only size 2 and 4 supported")
        full = cls._latin_solution(size)
        all_cells = [(r, c) for r in range(size) for c in range(size)]
        if n_clues < 0 or n_clues > len(all_cells):
            raise ValueError("n_clues out of range")

        selected = set(random.sample(all_cells, n_clues))
        grid: List[List[Optional[int]]] = []
        for r in range(size):
            row: List[Optional[int]] = []
            for c in range(size):
                row.append(full[r][c] if (r, c) in selected else None)
            grid.append(row)
        return cls(size=size, grid=grid)

    @staticmethod
    def _latin_solution(size: int) -> List[List[int]]:
        if size == 2:
            return [[0, 1], [1, 0]]
        return [
            [0, 1, 2, 3],
            [2, 3, 0, 1],
            [1, 0, 3, 2],
            [3, 2, 1, 0],
        ]

    def get_num_unknowns(self) -> int:
        return len(self.get_empty_cells())

    def get_value_range(self) -> int:
        return self.size

    def get_bits_per_cell(self) -> int:
        return math.ceil(math.log2(self.size))
