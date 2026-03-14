from __future__ import annotations

import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def _template_cells(name: str):
    md = nbformat.v4.new_markdown_cell
    code = nbformat.v4.new_code_cell

    templates = {
        "01_sudoku_basics_and_encoding.ipynb": [
            md("# 01 — Sudoku Basics and Encoding\nLoad a puzzle, inspect constraints, and inspect qubit mapping."),
            code(
                "from src.puzzle_engine import SudokuPuzzle\n"
                "from src.binary_encoder import SudokuEncoder\n"
                "puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])\n"
                "print(puzzle.display())\n"
                "print(puzzle.get_constraints())\n"
                "encoder = SudokuEncoder(puzzle)\n"
                "print(encoder.print_mapping())\n"
                "print(encoder.get_valid_bitstrings())"
            ),
        ],
        "02_oracle_construction_deep_dive.ipynb": [
            md("# 02 — Oracle Construction Deep Dive"),
            code(
                "from src.puzzle_engine import SudokuPuzzle\n"
                "from src.binary_encoder import SudokuEncoder\n"
                "from src.constraint_oracle import SudokuOracle\n"
                "puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])\n"
                "oracle = SudokuOracle(SudokuEncoder(puzzle))\n"
                "qc = oracle.build_oracle()\n"
                "print(oracle.get_oracle_stats())\n"
                "print([k for k,v in oracle.verify_oracle(qc).items() if v])"
            ),
        ],
        "03_grover_step_by_step.ipynb": [
            md("# 03 — Grover Step by Step"),
            code(
                "from src.puzzle_engine import SudokuPuzzle\n"
                "from src.grover_solver import QuantumSudokuSolver\n"
                "puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])\n"
                "solver = QuantumSudokuSolver(puzzle)\n"
                "res = solver.solve_with_visualization(shots=256)\n"
                "print(res['n_iterations'], res['top_measurement'], res['is_valid'])\n"
                "print(len(res['statevectors']))"
            ),
        ],
        "04_solving_2x2_sudoku.ipynb": [
            md("# 04 — Solving 2x2 Sudoku"),
            code(
                "from src.puzzle_engine import SudokuPuzzle\n"
                "from src.grover_solver import QuantumSudokuSolver\n"
                "for grid in ([[None,None],[None,None]], [[1,None],[None,None]]):\n"
                "    p = SudokuPuzzle(size=2, grid=grid)\n"
                "    r = QuantumSudokuSolver(p).solve(shots=512)\n"
                "    print(grid, r['top_measurement'], r['is_valid'])"
            ),
        ],
        "05_solving_4x4_sudoku.ipynb": [
            md("# 05 — Solving 4x4 Sudoku"),
            code(
                "from src.puzzle_engine import SudokuPuzzle\n"
                "from src.grover_solver import QuantumSudokuSolver\n"
                "p = SudokuPuzzle(size=4, grid=[[0,1,2,3],[2,3,None,1],[1,None,3,2],[3,2,1,0]])\n"
                "r = QuantumSudokuSolver(p).solve(shots=512)\n"
                "print(r['top_measurement'], r['is_valid'])\n"
                "print(r['decoded_solution'])"
            ),
        ],
        "06_visualization_showcase.ipynb": [
            md("# 06 — Visualization Showcase"),
            code(
                "from src.puzzle_engine import SudokuPuzzle\n"
                "from src.grover_solver import QuantumSudokuSolver\n"
                "from src.visualizer import SudokuVisualizer\n"
                "p = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])\n"
                "s = QuantumSudokuSolver(p)\n"
                "res = s.solve_with_visualization(shots=256)\n"
                "viz = SudokuVisualizer()\n"
                "viz.plot_measurement_histogram(res['counts'], s.valid_bitstrings)"
            ),
        ],
        "07_scalability_analysis.ipynb": [
            md("# 07 — Scalability Analysis"),
            code(
                "from src.puzzle_engine import SudokuPuzzle\n"
                "from src.grover_solver import QuantumSudokuSolver\n"
                "from src.complexity_analyzer import analyze_circuit, plot_scaling_analysis\n"
                "p = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])\n"
                "r = QuantumSudokuSolver(p).solve(shots=256)\n"
                "print(analyze_circuit(r['circuit']))\n"
                "plot_scaling_analysis()"
            ),
        ],
    }
    return templates[name]


def _load_or_bootstrap_notebook(input_path: Path):
    try:
        with input_path.open("r", encoding="utf-8") as handle:
            return nbformat.read(handle, as_version=4)
    except Exception:
        if input_path.name not in {
            "01_sudoku_basics_and_encoding.ipynb",
            "02_oracle_construction_deep_dive.ipynb",
            "03_grover_step_by_step.ipynb",
            "04_solving_2x2_sudoku.ipynb",
            "05_solving_4x4_sudoku.ipynb",
            "06_visualization_showcase.ipynb",
            "07_scalability_analysis.ipynb",
        }:
            raise
        notebook = nbformat.v4.new_notebook(cells=_template_cells(input_path.name))
        with input_path.open("w", encoding="utf-8") as handle:
            nbformat.write(notebook, handle)
        return notebook


def execute_notebook(
    input_path: Path,
    output_path: Path,
    timeout: int,
    allow_errors: bool,
    kernel_name: str,
) -> None:
    notebook = _load_or_bootstrap_notebook(input_path)

    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name=kernel_name,
        allow_errors=allow_errors,
    )
    client.execute(cwd=str(input_path.parent.parent))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        nbformat.write(notebook, handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute all project notebooks headlessly.")
    parser.add_argument("--input-dir", default="notebooks", help="Directory containing notebook files")
    parser.add_argument(
        "--output-dir",
        default="results/executed_notebooks",
        help="Directory where executed notebooks are written",
    )
    parser.add_argument("--timeout", type=int, default=300, help="Per-cell execution timeout (seconds)")
    parser.add_argument("--allow-errors", action="store_true", help="Continue and save output when a cell errors")
    parser.add_argument("--kernel", default="python3", help="Jupyter kernel name to execute with")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    notebooks = sorted(input_dir.glob("*.ipynb"))
    if not notebooks:
        raise SystemExit(f"No notebooks found in {input_dir}")

    failures: list[tuple[Path, str]] = []
    for notebook_path in notebooks:
        target_path = output_dir / notebook_path.name
        print(f"[run] {notebook_path} -> {target_path}")
        try:
            execute_notebook(
                input_path=notebook_path,
                output_path=target_path,
                timeout=args.timeout,
                allow_errors=args.allow_errors,
                kernel_name=args.kernel,
            )
            print(f"[ok ] {notebook_path.name}")
        except Exception as exc:
            failures.append((notebook_path, str(exc)))
            print(f"[err] {notebook_path.name}: {exc}")
            if not args.allow_errors:
                break

    if failures:
        print("\nExecution completed with failures:")
        for path, message in failures:
            print(f"- {path.name}: {message}")
        raise SystemExit(1)

    print("\nAll notebooks executed successfully.")


if __name__ == "__main__":
    main()
