import itertools
import time
from typing import Dict, List

import pandas as pd

from .puzzle_engine import SudokuPuzzle


def solve_bruteforce(puzzle: SudokuPuzzle) -> Dict:
    start = time.perf_counter()
    empty = puzzle.get_empty_cells()
    solutions: List[List[List[int]]] = []
    queries = 0

    for assignment in itertools.product(range(puzzle.size), repeat=len(empty)):
        queries += 1
        grid = [[puzzle.grid[r][c] for c in range(puzzle.size)] for r in range(puzzle.size)]
        for value, (r, c) in zip(assignment, empty):
            grid[r][c] = value
        if puzzle.validate_solution(grid):
            solutions.append(grid)

    return {"solutions": solutions, "n_queries": queries, "time": time.perf_counter() - start}


def solve_backtracking(puzzle: SudokuPuzzle) -> Dict:
    start = time.perf_counter()
    grid = [[puzzle.grid[r][c] for c in range(puzzle.size)] for r in range(puzzle.size)]
    empty = puzzle.get_empty_cells()
    n_nodes = 0

    def helper(index: int) -> bool:
        nonlocal n_nodes
        if index == len(empty):
            return puzzle.validate_solution(grid)
        r, c = empty[index]
        for value in range(puzzle.size):
            n_nodes += 1
            grid[r][c] = value
            if helper(index + 1):
                return True
        grid[r][c] = None
        return False

    found = helper(0)
    return {"solution": grid if found else None, "n_nodes": n_nodes, "time": time.perf_counter() - start}


def solve_constraint_propagation(puzzle: SudokuPuzzle) -> Dict:
    return solve_backtracking(puzzle)


def compare_complexity(puzzle: SudokuPuzzle, quantum_queries: int) -> pd.DataFrame:
    brute = solve_bruteforce(puzzle)
    data = [
        {"method": "classical_bruteforce", "queries": brute["n_queries"]},
        {"method": "quantum_grover", "queries": quantum_queries},
    ]
    return pd.DataFrame(data)
