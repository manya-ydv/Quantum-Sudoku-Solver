import argparse

from src.grover_solver import QuantumSudokuSolver
from src.puzzle_engine import SudokuPuzzle
from src.utils import load_yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Sudoku Solver")
    parser.add_argument("--puzzle", required=True, help="Path to puzzle JSON")
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--approach", choices=["manual", "high_level"], default="manual")
    parser.add_argument("--config", default="config/config.yaml")
    args = parser.parse_args()

    config = load_yaml(args.config)
    puzzle = SudokuPuzzle.from_json(args.puzzle)
    solver = QuantumSudokuSolver(puzzle=puzzle, config=config)
    result = solver.solve(approach=args.approach, shots=args.shots)

    print("Top measurement:", result["top_measurement"])
    print("Decoded solution:")
    for row in result["decoded_solution"]:
        print(row)
    print("Valid:", result["is_valid"])
    print("Iterations:", result["n_iterations"])


if __name__ == "__main__":
    main()
